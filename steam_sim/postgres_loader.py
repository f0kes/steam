import psycopg2
import pandas as pd


class PostgreSQLWrapper:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print("Connected to PostgreSQL database successfully.")
        except psycopg2.Error as e:
            print("Error connecting to PostgreSQL database:", e)

    def disconnect(self):
        if self.conn is not None:
            self.conn.close()
            print("Disconnected from PostgreSQL database.")

    def execute_query(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except psycopg2.Error as e:
            print("Error executing query:", e)
            return None

    def load_data_into_dataframe(self, query) -> pd.DataFrame:
        try:
            df = pd.read_sql(query, self.conn)
            return df
        except Exception as e:
            print("Error loading data into DataFrame:", e)
            return None

    def get_time_played_query(self) -> str:
        query = """SELECT DISTINCT ON (steam_id,game_id) steam_id, game_id, playtime_forever, time_stamp
FROM public.played_time
ORDER BY steam_id, game_id, time_stamp DESC

                    
        """
        return query
