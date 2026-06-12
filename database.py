from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://rabbani:KTk2sifQVATspOmyiII0nvrM4oVITNuJ@dpg-d8m1er8js32c73bcfvkg-a/todo_app_578o"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Sessionlocal = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()
