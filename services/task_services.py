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

def get_task_by_id(task_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM tasks WHERE id = ?
    """, (task_id,))

    row = cur.fetchone()
    conn.close()
    return row

def update_task(task_id, task_name, type_id, state_id, frequency,
                week_mask, start, end, total_amount, daily_target, priority):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE tasks
        SET task_name = ?,
            type_id = ?,
            state_id = ?,
            frequency = ?,
            week_mask = ?,
            scheduled_start = ?,
            scheduled_end = ?,
            total_amount = ?,
            daily_target = ?,
            priority = ?
        WHERE id = ?
    """, (
        task_name,
        type_id,
        state_id,
        frequency,
        week_mask,
        start,
        end,
        total_amount,
        daily_target,
        priority,
        task_id
    ))

    conn.commit()
    conn.close()

# =========================
# 任务操作
# =========================

def create_task(task_name, type_id, state_id, frequency,
                week_mask, start, end, total_amount, daily_target, priority):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tasks
        (task_name, type_id, state_id, frequency,
         week_mask, scheduled_start, scheduled_end,
         total_amount, daily_target, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (task_name, type_id, state_id, frequency,
          week_mask, start, end,
          total_amount, daily_target, priority))

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

def get_all_tasks_filtered(type_id=None, state_id=None, name_keyword=None, min_priority=None, max_priority=None):
    """
    获取任务列表，支持筛选
    :param type_id: int or list, 任务类型ID
    :param state_id: int or list, 任务状态ID
    :param name_keyword: str, 任务名称模糊匹配
    :param min_priority: int, 最低优先级
    :param max_priority: int, 最高优先级
    :return: list of dict
    """
    conn = get_conn()
    cur = conn.cursor()

    query = """
        SELECT t.*, tt.type_name, tt.type_color, ts.state_name, ts.state_color
        FROM tasks t
        JOIN task_type tt ON t.type_id = tt.id
        JOIN task_state ts ON t.state_id = ts.id
        WHERE 1=1
    """
    params = []

    if type_id is not None:
        if isinstance(type_id, list):
            placeholders = ",".join("?" for _ in type_id)
            query += f" AND t.type_id IN ({placeholders})"
            params.extend(type_id)
        else:
            query += " AND t.type_id = ?"
            params.append(type_id)

    if state_id is not None:
        if isinstance(state_id, list):
            placeholders = ",".join("?" for _ in state_id)
            query += f" AND t.state_id IN ({placeholders})"
            params.extend(state_id)
        else:
            query += " AND t.state_id = ?"
            params.append(state_id)

    if name_keyword:
        query += " AND t.task_name LIKE ?"
        params.append(f"%{name_keyword}%")

    if min_priority is not None:
        query += " AND t.priority >= ?"
        params.append(min_priority)

    if max_priority is not None:
        query += " AND t.priority <= ?"
        params.append(max_priority)

    query += " ORDER BY t.priority DESC, t.id DESC"

    cur.execute(query, params)
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
            t.daily_target,
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
        SET finished_amount = finished_amount + 1
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
        SET finished_amount = CASE
            WHEN finished_amount > 0 THEN finished_amount - 1
            ELSE 0
        END
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
            t.total_amount,
            t.scheduled_end,
            COALESCE(SUM(dc.finished_amount), 0) AS total_finished
        FROM tasks t
        LEFT JOIN daily_check dc ON t.id = dc.task_id
        WHERE t.id = ?
        GROUP BY t.id
    """, (task_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    total_amount = row["total_amount"] or 1
    scheduled_end = row["scheduled_end"]
    total_finished = row["total_finished"]

    # 若总目标为1且未设置结束日期，则不显示进度条
    if total_amount == 1 and scheduled_end is None:
        return None

    # 优先按总目标计算完成率
    rate = total_finished * 1.0 / total_amount if total_amount > 0 else 0.0

    result = [total_finished, total_amount, min(max(rate, 0.0), 1.0)]
    # 进度条最大显示为100%
    return result