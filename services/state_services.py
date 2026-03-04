import sqlite3

DB_PATH = "data/task.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# =========================
# 任务状态管理
# =========================

def get_all_states():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task_state ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_state(state_name, state_color):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO task_state (state_name, state_color) VALUES (?, ?)",
        (state_name, state_color)
    )
    conn.commit()
    conn.close()


def update_state(state_id, state_name, state_color):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE task_state SET state_name=?, state_color=? WHERE id=?",
        (state_name, state_color, state_id)
    )
    conn.commit()
    conn.close()


def delete_state(state_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM task_state WHERE id=?", (state_id,))
    conn.commit()
    conn.close()


def state_used(state_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tasks WHERE state_id=?", (state_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0