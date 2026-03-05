import sqlite3
from datetime import date, timedelta

DB_PATH = "data/task.db"

def should_generate(date, task):

    delta = (date - task["scheduled_start"]).days

    if task["frequency"] == "once":
        return delta == 0

    if task["frequency"] == "daily":
        return True

    if task["frequency"] == "everyTwoDay":
        return delta % 2 == 0

    if task["frequency"] == "everyThreeDay":
        return delta % 3 == 0

    if task["frequency"] in ("weekly", "weekday"):
        weekday = date.weekday()  # 0-6
        return (task["week_mask"] >> weekday) & 1

    if task["frequency"] == "everyTwoWeek":
        if (delta // 7) % 2 == 0:
            weekday = date.weekday()
            return (task["week_mask"] >> weekday) & 1
        return False

    if task["frequency"] == "monthly":
        return date.day == task["scheduled_start"].day

    return False

def generate_snapshots(task):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    today = date.today()
    # ---- 类型安全处理：字符串 → date ----
    if isinstance(task["scheduled_start"], str):
        task["scheduled_start"] = date.fromisoformat(task["scheduled_start"])

    if task["scheduled_end"] and isinstance(task["scheduled_end"], str):
        task["scheduled_end"] = date.fromisoformat(task["scheduled_end"])

    if task["scheduled_end"] is not None:
        target = min(task["scheduled_end"], today + timedelta(days=7))
    else:
        target = today + timedelta(days=7)

    cur.execute("""
        SELECT MAX(date)
        FROM daily_check
        WHERE task_id = ?
    """, (task["id"],))

    row = cur.fetchone()
    last_date = row[0]

    if last_date:
        start = date.fromisoformat(last_date) + timedelta(days=1)
    else:
        start = task["scheduled_start"]

    d = start

    while d <= target:
        if should_generate(d, task):
            cur.execute("""
                INSERT OR IGNORE INTO daily_check
                (task_id, date, snapshot_state_id)
                VALUES (?, ?, ?)
            """, (task["id"], d, task["state_id"]))
        d += timedelta(days=1)

    conn.commit()

def trim_future_snapshots(task_id, new_end):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM daily_check
        WHERE task_id = ?
        AND date > ?
    """, (task_id, new_end))
    conn.commit()

def ensure_all_snapshots():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM tasks
        WHERE is_active = 1
    """)

    tasks = cur.fetchall()

    for task in tasks:
        generate_snapshots(dict(task))