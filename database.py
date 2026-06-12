from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = (
    "postgresql://rabbani:rabbani@localhost/todo_application_server"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Sessionlocal = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()
