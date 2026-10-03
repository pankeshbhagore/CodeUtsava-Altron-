import os
import psycopg2
from dotenv import load_dotenv

def init_db():
    load_dotenv()
    db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        print("DATABASE_URL not found in .env")
        return
        
    print(f"Connecting to database to initialize schema and data...")
    
    # Connect to the default postgres database to create privdb
    # We parse the db_url to get credentials
    # format: postgresql://user:pass@host:port/dbname
    import urllib.parse
    result = urllib.parse.urlparse(db_url)
    username = urllib.parse.unquote(result.username) if result.username else None
    password = urllib.parse.unquote(result.password) if result.password else None
    host = result.hostname
    port = result.port
    dbname = result.path[1:]
    
    # Try to connect to postgres to create the DB if it doesn't exist
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=username,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
        if not cur.fetchone():
            print(f"Creating database {dbname}...")
            cur.execute(f"CREATE DATABASE {dbname}")
        else:
            print(f"Database {dbname} already exists.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error checking/creating database: {e}")
        print("Will attempt to connect directly to the target database...")
        
    # Connect to the target DB
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Read and execute schema
        with open("database/schema.sql", "r") as f:
            print("Applying schema.sql...")
            cur.execute(f.read())
            
        # Read and execute seed data
        with open("database/seed_data.sql", "r") as f:
            print("Applying seed_data.sql (this may take a moment for large datasets)...")
            cur.execute(f.read())
            
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialization complete!")
    except Exception as e:
        print(f"Error executing scripts: {e}")

if __name__ == "__main__":
    init_db()
