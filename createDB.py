import sqlite3

conn = sqlite3.connect("data/task.db")
cur = conn.cursor()

sql = """
    CREATE TABLE IF NOT EXISTS task_type (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT UNIQUE NOT NULL,
        color TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS task_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state_name TEXT UNIQUE NOT NULL,
        color TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        taskName TEXT UNIQUE NOT NULL,
        type_id INTEGER NOT NULL,
        state_id INTEGER NOT NULL,
        frequency TEXT CHECK (frequency IN ('weekday','once','daily','everyTwoDay','everyThreeDay','weekly','everyTwoWeek','monthly')),
        week_mask INTEGER DEFAULT 0 CHECK (week_mask BETWEEN 0 AND 127),
        scheduled_start DATE NOT NULL,
        scheduled_end DATE,
        total_amount INTEGER DEFAULT 100,
        priority INTEGER DEFAULT 0,
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
        state_id INTEGER,
        finished_amount INTEGER DEFAULT 0,

        UNIQUE(task_id, date),

        FOREIGN KEY (task_id) REFERENCES tasks(id),
        FOREIGN KEY (state_id) REFERENCES task_state(id)
    );

    CREATE TRIGGER IF NOT EXISTS trg_task_insert_daily
    AFTER INSERT ON tasks
    BEGIN
        DELETE FROM daily_check WHERE task_id = NEW.id;

        INSERT INTO daily_check (task_id, date, state_id)
        WITH RECURSIVE dates(d) AS (
            SELECT DATE(NEW.scheduled_start)
            UNION ALL
            SELECT DATE(d, '+1 day')
            FROM dates
            WHERE d < COALESCE(
                NEW.scheduled_end,
                DATE(NEW.scheduled_start, '+13 day')
            )
        )
        SELECT NEW.id, d, NEW.state_id
        FROM dates
        WHERE
            -- once
            (NEW.frequency = 'once' AND d = DATE(NEW.scheduled_start))

            OR
            -- daily
            (NEW.frequency = 'daily')

            OR
            -- everyTwoDay
            (NEW.frequency = 'everyTwoDay'
                AND (julianday(d) - julianday(NEW.scheduled_start)) % 2 = 0)

            OR
            -- everyThreeDay
            (NEW.frequency = 'everyThreeDay'
                AND (julianday(d) - julianday(NEW.scheduled_start)) % 3 = 0)

            OR
            -- weekly / weekday (bitmask control)
            ((NEW.frequency = 'weekly' OR NEW.frequency = 'weekday')
                AND ((NEW.week_mask >> CAST(strftime('%w', d) AS INTEGER)) & 1) = 1)

            OR
            -- everyTwoWeek
            (NEW.frequency = 'everyTwoWeek'
                AND ((julianday(d) - julianday(NEW.scheduled_start)) / 7) % 2 = 0
                AND ((NEW.week_mask >> CAST(strftime('%w', d) AS INTEGER)) & 1) = 1)

            OR
            -- monthly (same day-of-month)
            (NEW.frequency = 'monthly'
                AND strftime('%d', d) = strftime('%d', NEW.scheduled_start));
    END;

    CREATE TRIGGER IF NOT EXISTS trg_task_update_daily
    AFTER UPDATE OF scheduled_start, scheduled_end, frequency, week_mask ON tasks
    BEGIN
        DELETE FROM daily_check WHERE task_id = NEW.id;

        INSERT INTO daily_check (task_id, date, state_id)
        WITH RECURSIVE dates(d) AS (
            SELECT DATE(NEW.scheduled_start)
            UNION ALL
            SELECT DATE(d, '+1 day')
            FROM dates
            WHERE d < COALESCE(
                NEW.scheduled_end,
                DATE(NEW.scheduled_start, '+13 day')
            )
        )
        SELECT NEW.id, d, NEW.state_id
        FROM dates
        WHERE
            (NEW.frequency = 'once' AND d = DATE(NEW.scheduled_start))

            OR
            (NEW.frequency = 'daily')

            OR
            (NEW.frequency = 'everyTwoDay'
                AND (julianday(d) - julianday(NEW.scheduled_start)) % 2 = 0)

            OR
            (NEW.frequency = 'everyThreeDay'
                AND (julianday(d) - julianday(NEW.scheduled_start)) % 3 = 0)

            OR
            ((NEW.frequency = 'weekly' OR NEW.frequency = 'weekday')
                AND ((NEW.week_mask >> CAST(strftime('%w', d) AS INTEGER)) & 1) = 1)

            OR
            (NEW.frequency = 'everyTwoWeek'
                AND ((julianday(d) - julianday(NEW.scheduled_start)) / 7) % 2 = 0
                AND ((NEW.week_mask >> CAST(strftime('%w', d) AS INTEGER)) & 1) = 1)

            OR
            (NEW.frequency = 'monthly'
                AND strftime('%d', d) = strftime('%d', NEW.scheduled_start));
    END;

    CREATE TRIGGER IF NOT EXISTS trg_task_delete_daily
    AFTER DELETE ON tasks
    BEGIN
        DELETE FROM daily_check WHERE task_id = OLD.id;
    END;
"""

cur.executescript(sql)

# 开启外键约束
cur.execute("PRAGMA foreign_keys = ON;")

conn.commit()
cur.close()
conn.close()

print("Database initialized successfully.")