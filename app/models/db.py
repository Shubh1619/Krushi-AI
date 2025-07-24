import os
import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def create_users_table():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    mobile VARCHAR(20) UNIQUE NOT NULL
                );
            """)
            conn.commit()

def create_messages_table():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

def save_message(sender_id: int, receiver_id: int, message: str):
    db = get_db_connection()
    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO messages (sender_id, receiver_id, content)
            VALUES (%s, %s, %s)
        """, (sender_id, receiver_id, message))
        db.commit()

def get_chat_history(sender_id: int, receiver_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT sender_id, receiver_id, content, timestamp
        FROM messages
        WHERE (sender_id = %s AND receiver_id = %s)
           OR (sender_id = %s AND receiver_id = %s)
        ORDER BY timestamp
        """,
        (sender_id, receiver_id, receiver_id, sender_id)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    messages = [
        {"sender_id": r[0], "receiver_id": r[1], "content": r[2], "timestamp": r[3].isoformat()}
        for r in rows
    ]
    return messages


# ✅ Delete messages older than 24 hours
def delete_old_messages():
    db = get_db_connection()
    with db.cursor() as cur:
        cur.execute("""
            DELETE FROM messages
            WHERE timestamp < NOW() - INTERVAL '24 hours';
        """)
        db.commit()

# ✅ Background task to auto-delete every 1 hour
async def auto_delete_old_messages():
    while True:
        delete_old_messages()
        await asyncio.sleep(3600)  # Run hourly

# ✅ Auto-create tables on app startup
def init_db():
    create_users_table()
    create_messages_table()
