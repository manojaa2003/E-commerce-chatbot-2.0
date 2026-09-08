from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from .config import settings


SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.database_username,
    password=settings.database_password,
    host=settings.database_hostname,
    port=int(settings.database_port),
    database=settings.database_name,
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Sesssionlocal = sessionmaker(autocommit= False,autoflush=False,bind=engine)

Base = declarative_base()

def get_db():
    db = Sesssionlocal()
    try:
        yield db
    finally:
        db.close()

