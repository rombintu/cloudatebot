# external imports
from sqlalchemy import create_engine, Column, MetaData, Table
from sqlalchemy import insert, select, update

# from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import Integer, String, BLOB
from sqlalchemy.orm import declarative_base
from internal.memory import User as Umem



Base = declarative_base()
Metadata = MetaData()

Users = Table(
    "users",
    Metadata,
    Column("_id", Integer, primary_key=True),
    Column("uuid", Integer, unique=True),
    Column("username", String),
    Column("creds", BLOB)
)

class User(Base):
    __table__ = Users

class Database:
    def __init__(self, engine):
        self.engine = create_engine(engine)
        Metadata.create_all(self.engine)
    
    # def execute(self, script):
    #     with self.engine.connect() as c:
    #         with c.begin():
    #             return c.execute(script)
                

    def login(self, u):
        with self.engine.connect() as c:
            with c.begin():
                select_user = select(User).where(User.uuid == u.uuid)
                login = c.execute(select_user).first()
                if not login:
                    create_user = (
                        insert(User).values(uuid=u.uuid, username=u.username)
                    )
                    c.execute(create_user)
                    login = c.execute(select_user).first()
                user = Umem(login["uuid"], login["username"])
                user.set_creds(login["creds"])
                return user

    def update_creds(self, u):
        with self.engine.connect() as c:
            with c.begin():
                update_user_creds = update(User).where(User.uuid == u.uuid).values(creds=u.creds)
                return c.execute(update_user_creds)

        