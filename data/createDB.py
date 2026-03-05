import sqlite3

conn = sqlite3.connect("data/task.db")
cur = conn.cursor()

sql = """
    CREATE TABLE IF NOT EXISTS task_type (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT UNIQUE NOT NULL,
        type_color TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS task_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state_name TEXT UNIQUE NOT NULL,
        state_color TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS preset_colors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        color_name TEXT UNIQUE NOT NULL,
        color_value TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT UNIQUE NOT NULL,
        type_id INTEGER NOT NULL,
        state_id INTEGER NOT NULL,

        frequency TEXT CHECK (
            frequency IN (
                'weekday','once','daily',
                'everyTwoDay','everyThreeDay',
                'weekly','everyTwoWeek','monthly'
            )
        ),

        week_mask INTEGER DEFAULT 0 CHECK (week_mask BETWEEN 0 AND 127),

        scheduled_start DATE NOT NULL,
        scheduled_end DATE,

        is_active INTEGER DEFAULT 1,     -- 终止控制
        total_amount INTEGER DEFAULT 1,
        daily_target INTEGER DEFAULT 1,  -- 每日目标完成数
        priority INTEGER DEFAULT 5,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (type_id) REFERENCES task_type(id),
        FOREIGN KEY (state_id) REFERENCES task_state(id)
    );

    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        content TEXT,
        solved INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (task_id) REFERENCES tasks(id)
    );

    CREATE TABLE IF NOT EXISTS daily_check (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        date DATE NOT NULL,

        snapshot_state_id INTEGER NOT NULL,
        finished_amount INTEGER DEFAULT 0,

        UNIQUE(task_id, date),

        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
        FOREIGN KEY (snapshot_state_id) REFERENCES task_state(id)
    );
"""


cur.executescript(sql)

# 预设一个空状态（灰色）
cur.execute("""
    INSERT OR IGNORE INTO task_state (state_name, state_color)
    VALUES (?, ?)
""", ("未设置", "#808080"))

# 预设一个空类型（灰色）
cur.execute("""
    INSERT OR IGNORE INTO task_type (type_name, type_color)
    VALUES (?, ?)
""", ("未设置", "#808080"))

# 开启外键约束
cur.execute("PRAGMA foreign_keys = ON;")

conn.commit()
cur.close()
conn.close()

print("Database initialized successfully.")