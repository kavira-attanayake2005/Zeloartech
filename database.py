import sqlite3
import os
import contextlib
from typing import List, Dict, Any, Optional
from datetime import datetime

# Parse DB path from config string (assuming simple mapping for sqlite3)
# From "sqlite:///./audit.db" to "./audit.db"
DB_FILE = "./audit.db"

def get_connection():
    """
    Returns a new connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database schemas.
    """
    with contextlib.closing(get_connection()) as conn:
        cursor = conn.cursor()
        
        # Append-only audit logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                intent TEXT NOT NULL,
                confidence REAL NOT NULL,
                routing_path TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT
            )
        ''')
        
        # Memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                tier TEXT NOT NULL,
                content TEXT NOT NULL,
                significance_score REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()

def log_audit(user_id: str, intent: str, confidence: float, routing_path: str, status: str, error_message: Optional[str] = None):
    """
    Inserts a new append-only log entry into the audit_logs table.
    """
    timestamp = datetime.utcnow().isoformat()
    with contextlib.closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audit_logs (timestamp, user_id, intent, confidence, routing_path, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, user_id, intent, confidence, routing_path, status, error_message))
        conn.commit()

def get_audit_logs() -> List[Dict[str, Any]]:
    """
    Retrieves all audit logs.
    """
    with contextlib.closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM audit_logs ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def add_memory(user_id: str, tier: str, content: str, significance_score: float) -> int:
    """
    Adds a new memory for a user.
    """
    created_at = datetime.utcnow().isoformat()
    with contextlib.closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO memories (user_id, tier, content, significance_score, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, tier, content, significance_score, created_at))
        conn.commit()
        return cursor.lastrowid

def get_memories(user_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves all memories for a specific user.
    """
    with contextlib.closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM memories WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# Initialize db upon import
init_db()
