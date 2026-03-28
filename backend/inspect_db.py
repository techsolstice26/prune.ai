import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "cloudscope-timescaledb.c2rk6ku6c9fj.us-east-1.rds.amazonaws.com")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "CloudScopeMasterPassword2026!")

def inspect_db():
    print("\n" + "="*80)
    print(" 🔍 CLOUDSCOPE AIOPS - TIMESCALEDB RAW INSPECTOR")
    print("="*80 + "\n")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        
        # Query the last 20 records
        query = """
            SELECT time, instance_id, cpu_usage_percent, suspicion_score, role_arn 
            FROM metrics_history 
            ORDER BY time DESC 
            LIMIT 20
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        if not rows:
            print(" [!] No records found in 'metrics_history' table.")
        else:
            # Print header
            print(f"{'TIMESTAMP':<25} | {'INSTANCE':<15} | {'CPU%':<6} | {'SCORE':<6} | {'ROLE ARN (SAMPLED)'}")
            print("-" * 80)
            
            for row in rows:
                ts, inst, cpu, score, arn = row
                arn_short = (arn[:30] + "..") if arn else "None"
                print(f"{str(ts):<25} | {inst:<15} | {cpu:<6.1f} | {score:<6.2f} | {arn_short}")
        
        cur.close()
        conn.close()
        print("\n" + "="*80)
        print(" [OK] End of Audit Trail.")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f" [ERROR] Could not connect to database: {e}")

if __name__ == "__main__":
    inspect_db()
