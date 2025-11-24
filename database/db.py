from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings

DATABASE_URL = settings.SUPABASE_DB_URL  

engine = create_engine(DATABASE_URL, echo=True)  # echo=True shows SQL logs

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

