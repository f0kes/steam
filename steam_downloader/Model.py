from datetime import datetime
from typing import List

import sqlalchemy
from sqlalchemy import ForeignKey, Column, BigInteger, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()

friendship_table = Table(
    'friendship', Base.metadata,
    Column('user_id', BigInteger, ForeignKey('user_data.steam_id')),
    Column('friend_id', BigInteger, ForeignKey('user_data.steam_id'))
)


class PlayedTime(Base):
    __tablename__ = 'played_time'

    id: Mapped[int] = mapped_column(sqlalchemy.BigInteger, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(sqlalchemy.BigInteger, ForeignKey('game_data.id'))
    steam_id: Mapped[int] = mapped_column(sqlalchemy.BigInteger, ForeignKey('user_data.steam_id'))
    playtime_two_weeks: Mapped[int] = mapped_column(sqlalchemy.BigInteger)
    playtime_forever: Mapped[int] = mapped_column(sqlalchemy.BigInteger)
    time_stamp: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, default=datetime.now)


class GameData(Base):
    __tablename__ = 'game_data'

    id: Mapped[int] = mapped_column(sqlalchemy.BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(sqlalchemy.String, default="Unknown")
    play_times: Mapped[List["PlayedTime"]] = relationship()


class UserData(Base):
    __tablename__ = 'user_data'

    steam_id: Mapped[int] = mapped_column(sqlalchemy.BigInteger, primary_key=True, autoincrement=False)
    friends: Mapped[List["UserData"]] = relationship("UserData", secondary=friendship_table,
                                                     primaryjoin=steam_id == friendship_table.c.user_id,
                                                     secondaryjoin=steam_id == friendship_table.c.friend_id)
    is_dead_account: Mapped[bool] = mapped_column(sqlalchemy.Boolean, default=False)
    last_updated: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, default=datetime.now)
    total_playtime: Mapped[int] = mapped_column(sqlalchemy.BigInteger, default=0)
    total_playtime_two_weeks: Mapped[int] = mapped_column(sqlalchemy.BigInteger, default=0)
    play_times: Mapped[List["PlayedTime"]] = relationship()


class FollowedUsers(Base):
    __tablename__ = 'followed_users'

    id: Mapped[int] = mapped_column(sqlalchemy.BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped["UserData"] = mapped_column(sqlalchemy.BigInteger, ForeignKey('user_data.steam_id'))

