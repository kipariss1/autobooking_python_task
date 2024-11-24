import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from models import Base
import models


DB_URL = "sqlite:///./local.db"

engine = sa.create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()


def get_db():
    db_inst = SessionLocal()
    try:
        return db_inst
    finally:
        db_inst.close()
