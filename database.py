import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from models import Base


DB_URL = "sqlite:///./local.db"

engine = sa.create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()
