import sqlite3
from datetime import datetime
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_seen TEXT,
            last_seen TEXT,
            successful_conversions INTEGER DEFAULT 0,
            failed_conversions INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def log_user(user_id: int, username: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user:
        cursor.execute(
            "UPDATE users SET username = ?, last_seen = ? WHERE user_id = ?",
            (username, now, user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO users (user_id, username, first_seen, last_seen, successful_conversions, failed_conversions) VALUES (?, ?, ?, ?, 0, 0)",
            (user_id, username, now, now)
        )
    conn.commit()
    conn.close()

def record_conversion_result(user_id: int, success: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if success:
        cursor.execute(
            "UPDATE users SET successful_conversions = successful_conversions + 1 WHERE user_id = ?",
            (user_id,)
        )
    else:
        cursor.execute(
            "UPDATE users SET failed_conversions = failed_conversions + 1 WHERE user_id = ?",
            (user_id,)
        )
    conn.commit()
    conn.close()

def get_user_stats(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT successful_conversions, failed_conversions FROM users WHERE user_id = ?",
        (user_id,)
    )
    res = cursor.fetchone()
    conn.close()
    if res:
        return {"success": res[0], "failed": res[1]}
    return {"success": 0, "failed": 0}

def get_global_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(successful_conversions), SUM(failed_conversions) FROM users")
    res = cursor.fetchone()
    conn.close()
    return {
        "total_users": res[0] or 0,
        "total_success": res[1] or 0,
        "total_failed": res[2] or 0
    }

def get_all_user_ids():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]
