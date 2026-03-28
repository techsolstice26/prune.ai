import psycopg2
import random
from datetime import datetime, timedelta

DB_HOST = 'cloudscope-timescaledb.c2rk6ku6c9fj.us-east-1.rds.amazonaws.com'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS = 'CloudScopeMasterPassword2026!'
ROLE_ARN = 'arn:aws:iam::008533941157:role/PruneAI_CrossAccount_Role'

conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
cur = conn.cursor()

now = datetime.utcnow()
instances = ['i-0abcd1234efgh5678', 'i-09fe8d7c6b5a43210']

for i in range(96):
    ts = now - timedelta(minutes=15 * (96 - i))
    inst = random.choice(instances)

    if random.random() < 0.15:
        cpu = random.uniform(78, 98)
        mem = random.uniform(70, 92)
        net = random.randint(800000000, 2000000000)
        spend = round(random.uniform(3.5, 8.2), 2)
        score = round(random.uniform(0.65, 0.95), 2)
        is_anomaly = True
    else:
        cpu = random.uniform(12, 55)
        mem = random.uniform(20, 58)
        net = random.randint(50000000, 400000000)
        spend = round(random.uniform(0.3, 2.1), 2)
        score = round(random.uniform(0.05, 0.45), 2)
        is_anomaly = False

    cur.execute(
        """INSERT INTO metrics_history
        (time, instance_id, cpu_usage_percent, memory_usage_percent, network_in_bytes, hourly_spend, suspicion_score, is_anomaly, role_arn)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (ts, inst, round(cpu, 1), round(mem, 1), net, spend, score, is_anomaly, ROLE_ARN)
    )

conn.commit()
cur.close()
conn.close()
print('Seeded 96 data points (24h @ 15min intervals)')
