import numpy as np

from RecVAE.postgres_loader import PostgreSQLWrapper
from scipy.sparse import csr_matrix, coo_matrix
from scipy.sparse.linalg import svds


class SvdLatentBuilder:

    def __init__(self, pg: PostgreSQLWrapper):
        self.pg = pg
        self.df = None
        self.game_enum = None
        self.user_to_idx = None
        self.idx_to_user = None
        self.game_to_idx = None
        self.idx_to_game = None
        self.U = None
        self.sigma = None
        self.Vt = None

    def load_df(self):
        query = """SELECT DISTINCT ON (steam_id,game_id) steam_id, game_id, playtime_forever, playtime_two_weeks
        FROM public.played_time
        ORDER BY steam_id, game_id, time_stamp DESC


                """
        self.df = self.pg.load_data_into_dataframe(query)

    def load_game_enum(self):
        query = """select * from game_enum"""
        self.game_enum = self.pg.load_data_into_dataframe(query)
        # this df has columns sid, id, name. game_to_idx is id:sid, idx_to_game is sid:id. all sid and id are unique. sid starts from 1,so we need to subtract 1 from sid to get the index
        game_to_idx = {}
        idx_to_game = {}
        for index, row in self.game_enum.iterrows():
            game_to_idx[row['id']] = row['sid'] - 1
            idx_to_game[row['sid'] - 1] = row['id']
        self.game_to_idx = game_to_idx
        self.idx_to_game = idx_to_game
        return game_to_idx, idx_to_game

    def enumerate_users(self, df=None):
        if df is None:
            df = self.df
        user_to_idx = {user: idx for idx, user in enumerate(df['steam_id'].unique())}
        idx_to_user = {idx: user for user, idx in user_to_idx.items()}
        self.user_to_idx = user_to_idx
        self.idx_to_user = idx_to_user
        return user_to_idx, idx_to_user

    def get_game_mapping(self):
        if self.game_to_idx is None or self.idx_to_game is None:
            self.load_game_enum()
        return self.game_to_idx, self.idx_to_game

    def get_user_mapping(self):
        if self.user_to_idx is None or self.idx_to_user is None:
            self.enumerate_users()
        return self.user_to_idx, self.idx_to_user

    def process_df(self, df=None):
        if df is None:
            df = self.df
        df_filtered = df[(df['playtime_forever'] > 60)]
        df_time_normalized = df_filtered.copy()
        df_time_normalized['playtime_forever'] = np.log(df_time_normalized['playtime_forever'])
        df_time_normalized['playtime_forever'] = ((df_time_normalized['playtime_forever']
                                                   - df_time_normalized['playtime_forever'].min())
                                                  / (df_time_normalized['playtime_forever'].max()
                                                     - df_time_normalized['playtime_forever'].min()))
        df_time_normalized.head()
        self.df = df_time_normalized
        return df_time_normalized

    def construct_latent_space(self, df=None, game_to_idx=None, user_to_idx=None):
        if df is None:
            df = self.df
        if game_to_idx is None:
            game_to_idx = self.game_to_idx
        if user_to_idx is None:
            user_to_idx = self.user_to_idx

        csr = csr_matrix(
            (df['playtime_forever'], (df['steam_id'].map(user_to_idx), df['game_id'].map(game_to_idx))))
        U, sigma, Vt = svds(csr, k=100)
        self.U = U
        self.sigma = sigma
        self.Vt = Vt.T
        return U, sigma, Vt

    def cosine_similarity(self, item_1, item_2):
        return np.dot(item_1, item_2) / (np.linalg.norm(item_1) * np.linalg.norm(item_2))

    def game_avg_vector(self, game_idx_steam_vector, vt=None):
        if vt is None:
            vt = self.Vt
        return np.mean([vt[self.game_to_idx[i]] for i in game_idx_steam_vector], axis=0)

    def game_vector(self, game_idx_steam, vt=None):
        if vt is None:
            vt = self.Vt
        return vt[self.game_to_idx[game_idx_steam]]

    def compare_games(self, game_1, game_2):
        g1idx = self.game_to_idx[game_1]
        g2idx = self.game_to_idx[game_2]
        return self.cosine_similarity(self.Vt[g1idx], self.Vt[g2idx])

    def save_latent_space(self):
        np.save('U.npy', self.U)
        np.save('sigma.npy', self.sigma)
        np.save('Vt.npy', self.Vt)

    def load_latent_space(self):
        self.U = np.load('U.npy')
        self.sigma = np.load('sigma.npy')
        self.Vt = np.load('Vt.npy')
