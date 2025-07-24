import os
import asyncio
import base64
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
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delivered BOOLEAN DEFAULT FALSE,
                    seen BOOLEAN DEFAULT FALSE
                );
            """)
            conn.commit()

def upgrade_messages_table():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            ALTER TABLE messages
            ADD COLUMN IF NOT EXISTS delivered BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS seen BOOLEAN DEFAULT FALSE;
        """)
        conn.commit()
    conn.close()

def save_message(sender_id: int, receiver_id: int, message: str) -> int:
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO messages (sender_id, receiver_id, content)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (sender_id, receiver_id, message))
        message_id = cur.fetchone()["id"]
        conn.commit()
    conn.close()
    return message_id

def mark_message_delivered(message_id: int):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE messages SET delivered = TRUE WHERE id = %s;", (message_id,))
        conn.commit()
    conn.close()

def mark_message_seen(message_id: int):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE messages SET seen = TRUE WHERE id = %s;", (message_id,))
        conn.commit()
    conn.close()

def get_chat_history(sender_id: int, receiver_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, sender_id, receiver_id, content, timestamp, delivered, seen
        FROM messages
        WHERE (sender_id = %s AND receiver_id = %s)
           OR (sender_id = %s AND receiver_id = %s)
        ORDER BY timestamp;
        """,
        (sender_id, receiver_id, receiver_id, sender_id)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    messages = [
        {
            "from": str(r["sender_id"]),
            "message": base64.b64encode(r["content"].encode()).decode(),
            "status": (
                "seen" if r["seen"]
                else "delivered" if r["delivered"]
                else "sent"
            )
        }
        for r in rows
    ]
    return messages

def delete_old_messages():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM messages
            WHERE timestamp < NOW() - INTERVAL '24 hours';
        """)
        conn.commit()
    conn.close()

async def auto_delete_old_messages():
    while True:
        delete_old_messages()
        await asyncio.sleep(3600)

def init_db():
    create_users_table()
    create_messages_table()
    upgrade_messages_table()  # ✅ Apply new schema if needed