import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get('TIMESCALEDB_URL')

if not url:
    print("No TIMESCALEDB_URL found in .env!")
    exit(1)

try:
    print("Attempting to connect to TimescaleDB...")
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    with open('schema.sql', 'r') as f:
        print("Executing schema.sql...")
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()
    print("Database schema successfully initialized!")
except Exception as e:
    print(f"Failed to initialize database: {e}")
