# external imports
from sqlalchemy import create_engine, Column, MetaData, Table

# from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import Integer, String
from sqlalchemy.orm import declarative_base, Session

# internal imports
from datetime import datetime, timedelta

# local imports
#

Base = declarative_base()
Metadata = MetaData()

Users = Table(
    "users",
    Metadata,
    Column("_id", Integer, primary_key=True),
    Column("uuid", Integer),
    Column("nickname", String, unique=True),
    Column("bank", Integer, default=0)
)

class User(Base):
    __table__ = Users

class Database:
    def __init__(self, engine):
        self.engine = create_engine(engine)
        Metadata.create_all(self.engine)
        
    def _open(self):
        try:
            self.session = Session(self.engine)
            return 0
        except Exception as err:
            return err

    def _close(self):
        self.session.close()
        
    def increment_bank(self, uuid, nickname, i=5):
        err = self._open()
        if err:
            return err
        user = self.session.query(User).filter_by(nickname=nickname, uuid=uuid).first()
        user.bank = user.bank + i
        self._close()
        return 0