import sqlite3


DATABASE = "instance/citizenfix.db"


connection = sqlite3.connect(DATABASE)

cursor = connection.cursor()


try:

    cursor.execute(
        "ALTER TABLE issues ADD COLUMN priority VARCHAR(20) "
        "NOT NULL DEFAULT 'Medium'"
    )

    print(
        "Priority column added successfully."
    )

except sqlite3.OperationalError as error:

    if "duplicate column name" in str(error):

        print(
            "Priority column already exists."
        )

    else:

        raise


connection.commit()

connection.close()


print(
    "Priority database migration completed successfully."
)