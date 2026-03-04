import sqlite3

DB_PATH = "data/task.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# =========================
# 任务类型管理
# =========================

def get_all_types():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task_type ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_type(type_name, type_color):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO task_type (type_name, type_color) VALUES (?, ?)",
        (type_name, type_color)
    )
    conn.commit()
    conn.close()


def update_type(type_id, type_name, type_color):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE task_type SET type_name=?, type_color=? WHERE id=?",
        (type_name, type_color, type_id)
    )
    conn.commit()
    conn.close()


def delete_type(type_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM task_type WHERE id=?", (type_id,))
    conn.commit()
    conn.close()


def type_used(type_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tasks WHERE type_id=?", (type_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0


