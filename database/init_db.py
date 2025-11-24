from database.db import engine
from database.models import Base

def init_db():
    print("Creating tables in Supabase PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    init_db()
