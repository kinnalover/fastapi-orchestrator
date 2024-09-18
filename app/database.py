from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app import config
from contextlib  import contextmanager
# SQLALCHEMY_DATABASE_URL can be set to any database supported by SQLAlchemy.
# Examples:
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"  # For SQLite
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"  # For PostgreSQL
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@mysqlserver/db"  # For MySQL



# Create the SQLAlchemy engine
engine = create_engine(config.SQLALCHEMY_DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class that our models will inherit from
Base = declarative_base()

# Dependency to get a SQLAlchemy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_2():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()