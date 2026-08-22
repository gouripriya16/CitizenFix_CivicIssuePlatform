import sqlite3
import os



# DATABASE PATH

db_path = os.path.join(
    "instance",
    "citizenfix.db"
)



# CONNECT TO DATABASE


connection = sqlite3.connect(
    db_path
)

cursor = connection.cursor()


# GET EXISTING COLUMNS

cursor.execute(
    "PRAGMA table_info(issues)"
)

columns = [
    column[1]
    for column in cursor.fetchall()
]



# ADD CREATED_AT COLUMN

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

    print(
        "created_at column added."
    )


# ADD UPDATED_AT COLUMN

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

    print(
        "updated_at column added."
    )



# ADD IMAGE_FILENAME COLUMN

if "image_filename" not in columns:

    cursor.execute("""
        ALTER TABLE issues
        ADD COLUMN image_filename VARCHAR(255)
    """)

    print(
        "image_filename column added."
    )



# SAVE CHANGES

connection.commit()

# CLOSE DATABASE

connection.close()


print(
    "Database migration completed successfully."
)