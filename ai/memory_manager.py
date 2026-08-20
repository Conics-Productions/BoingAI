import sqlite3
import json
import os

DB_PATH = "boingai.db"

class MemoryManager:
    def __init__(self):
        self._init_sqlite()

    def _init_sqlite(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Table for saved chat sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Table for messages inside chat sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
                )
            """)
            # Table for AI persistent memories
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact TEXT UNIQUE NOT NULL
                )
            """)
            conn.commit()

    # --- Chat History Methods ---
    def create_session(self, title="New Chat") -> int:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO chat_sessions (title) VALUES (?)", (title,))
            conn.commit()
            return cursor.lastrowid

    def get_all_sessions(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title FROM chat_sessions ORDER BY id DESC")
            return cursor.fetchall()

    def save_message(self, session_id: int, sender: str, content: str):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_messages (session_id, sender, content) VALUES (?, ?, ?)",
                (session_id, sender, content)
            )
            conn.commit()

    def get_session_messages(self, session_id: int):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT sender, content FROM chat_messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,)
            )
            return cursor.fetchall()

    def delete_session(self, session_id: int):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
            cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
            conn.commit()

    # --- AI Memory Methods ---
    def add_memory(self, fact: str):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO ai_memories (fact) VALUES (?)", (fact.strip(),))
                conn.commit()
            except sqlite3.IntegrityError:
                pass # Memory already exists

    def get_all_memories(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fact FROM ai_memories")
            return [row[0] for row in cursor.fetchall()]

    def delete_memory(self, fact: str):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ai_memories WHERE fact = ?", (fact,))
            conn.commit()