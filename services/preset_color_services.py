import sqlite3

DB_PATH = "data/task.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_preset_colors():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM preset_colors ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_preset_color(color_name, color_value):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO preset_colors (color_name, color_value) VALUES (?, ?)",
        (color_name, color_value)
    )
    conn.commit()
    conn.close()


def delete_preset_color(color_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM preset_colors WHERE id = ?", (color_id,))
    conn.commit()
    conn.close()