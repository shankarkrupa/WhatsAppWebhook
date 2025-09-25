from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL
#DATABASE_URL = "postgresql://user:password@localhost/whatsapp_db"

# For SQLite, use:
DATABASE_URL = "sqlite:///./whatsapp.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()
