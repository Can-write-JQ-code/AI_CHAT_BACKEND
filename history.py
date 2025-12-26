import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

class HistoryManager:
    def __init__(self, db_path: str = "history.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create history table
        # type: 'chat' or 'image'
        # prompt: the user's input
        # response: the AI's response (text or image URL)
        # metadata: additional JSON data (model, parameters, etc)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            prompt TEXT,
            response TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()

    def add_history(self, type: str, prompt: str, response: str, metadata: Dict[str, Any] = None):
        """Add a new history record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else "{}"
        
        cursor.execute(
            'INSERT INTO history (type, prompt, response, metadata) VALUES (?, ?, ?, ?)',
            (type, prompt, response, metadata_json)
        )
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id

    def get_history(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get history records, newest first"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This allows accessing columns by name
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM history ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (limit, offset)
        )
        
        rows = cursor.fetchall()
        history = []
        
        for row in rows:
            history.append({
                "id": row["id"],
                "type": row["type"],
                "prompt": row["prompt"],
                "response": row["response"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                "created_at": row["created_at"]
            })
            
        conn.close()
        return history

    def clear_history(self):
        """Clear all history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM history')
        conn.commit()
        conn.close()
