import sqlite3
from datetime import date

DB_PATH = "data/task.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# =========================
# 基础查询
# =========================

def get_task_types():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task_type ORDER BY id;")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_task_states():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task_state ORDER BY id;")
    rows = cur.fetchall()
    conn.close()
    return rows


# =========================
# 任务操作
# =========================

def create_task(task_name, type_id, state_id, frequency,
                week_mask, start, end, total_amount, priority):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tasks
        (task_name, type_id, state_id, frequency,
         week_mask, scheduled_start, scheduled_end,
         total_amount, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (task_name, type_id, state_id, frequency,
          week_mask, start, end,
          total_amount, priority))

    conn.commit()
    conn.close()


def get_all_tasks():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT t.*, tt.type_name, tt.type_color, ts.state_name, ts.state_color
        FROM tasks t
        JOIN task_type tt ON t.type_id = tt.id
        JOIN task_state ts ON t.state_id = ts.id
        ORDER BY t.priority DESC, t.id DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


# =========================
# 今日任务
# =========================

def get_day_tasks(day = date.today().isoformat()):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            dc.task_id,
            dc.date,
            dc.finished_amount,
            t.task_name,
            t.total_amount,
            t.priority,
            tt.type_name,
            tt.type_color,
            ts.state_name,
            ts.state_color
        FROM daily_check dc
        JOIN tasks t ON dc.task_id = t.id
        JOIN task_type tt ON t.type_id = tt.id
        JOIN task_state ts ON t.state_id = ts.id
        WHERE dc.date = ?
        ORDER BY t.priority DESC
    """, (day,))

    rows = cur.fetchall()
    conn.close()
    return rows


def finish_today_task(task_id):
    today = date.today().isoformat()

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE daily_check
        SET finished_amount = 1
        WHERE task_id = ? AND date = ?
    """, (task_id, today))

    conn.commit()
    conn.close()

def undo_today_task(task_id):
    today = date.today().isoformat()

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE daily_check
        SET finished_amount = 0
        WHERE task_id = ? AND date = ?
    """, (task_id, today))

    conn.commit()
    conn.close()

# =========================
# 统计
# =========================

def get_task_completion_rate(task_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            COALESCE(SUM(dc.finished_amount), 0) * 1.0 / 
            COALESCE(t.total_amount, 1) AS rate
        FROM tasks t
        LEFT JOIN daily_check dc ON t.id = dc.task_id
        WHERE t.id = ?
        GROUP BY t.id
    """, (task_id,))

    row = cur.fetchone()
    conn.close()

    return row["rate"] if row and row["rate"] is not None else 0.0