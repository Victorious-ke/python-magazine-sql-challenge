import sqlite3
from typing import Optional

DB_FILE = 'magazine.db'

def get_connection() -> sqlite3.Connection:
 """
    Return a sqlite3.Connection to DB_FILE.
    Caller may rely on row_factory if they want (we set a default Row factory here).
    """
    conn = sqlite3.connect(DB_FILE)

    conn.row_factory = sqlite3.Row
    return conn


def create_tables() -> None:
    """
    Create authors, magazines, and articles tables with correct foreign keys.
    Enables PRAGMA foreign_keys = ON.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
        # authors table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """)
        # magazines table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS magazines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL
        );
        """)
        # articles table with foreign keys
        cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER NOT NULL,
            magazine_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            FOREIGN KEY (author_id) REFERENCES authors(id),
            FOREIGN KEY (magazine_id) REFERENCES magazines(id)
        );
        """)
        conn.commit()
    finally:
        conn.close()