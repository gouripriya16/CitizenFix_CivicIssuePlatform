import sqlite3
import os


db_path = os.path.join(
    "instance",
    "citizenfix.db"
)


connection = sqlite3.connect(db_path)

cursor = connection.cursor()


cursor.execute("PRAGMA table_info(issues)")

columns = [
    column[1]
    for column in cursor.fetchall()
]


if "created_at" not in columns:

    cursor.execute("""
        ALTER TABLE issues
        ADD COLUMN created_at DATETIME
    """)

    cursor.execute("""
        UPDATE issues
        SET created_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
    """)

    print("created_at column added.")


if "updated_at" not in columns:

    cursor.execute("""
        ALTER TABLE issues
        ADD COLUMN updated_at DATETIME
    """)

    cursor.execute("""
        UPDATE issues
        SET updated_at = created_at
        WHERE updated_at IS NULL
    """)

    print("updated_at column added.")


connection.commit()

connection.close()

print("Database migration completed successfully.")