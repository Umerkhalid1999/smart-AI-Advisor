import os
import sqlite3
import shutil
from pathlib import Path


def reset_all_databases():
    # Delete both database files if they exist
    db_paths = [
        Path("C:/Users/hp/Desktop/Advisor-student (3)/Advisor-student/instance/users.db"),
        Path("C:/Users/hp/Desktop/Advisor-student (3)/Advisor-student/users.db"),
        Path("C:/Users/hp/Desktop/Advisor-student (3)/users.db"),
        Path("instance/users.db"),
        Path("users.db")
    ]

    for path in db_paths:
        if path.exists():
            print(f"Removing database at: {path}")
            os.remove(path)

    # Create the instance directory if it doesn't exist
    instance_dir = Path("C:/Users/hp/Desktop/Advisor-student (3)/Advisor-student/instance")
    if not instance_dir.exists():
        os.makedirs(instance_dir)
        print(f"Created directory: {instance_dir}")

    # Create a fresh database in the instance folder
    db_path = instance_dir / "users.db"
    print(f"Creating new database at: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create user table with role column
    cursor.execute('''
    CREATE TABLE user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password VARCHAR(200) NOT NULL,
        role VARCHAR(20) DEFAULT 'student'
    )
    ''')

    # Create chat_message table
    cursor.execute('''
    CREATE TABLE chat_message (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        read BOOLEAN DEFAULT 0,
        FOREIGN KEY (sender_id) REFERENCES user (id),
        FOREIGN KEY (receiver_id) REFERENCES user (id)
    )
    ''')

    conn.commit()
    conn.close()

    print(f"Created fresh database at: {db_path}")
    print("WARNING: All previous users and data have been lost.")


if __name__ == "__main__":
    confirm = input("This will RESET ALL databases and DELETE ALL DATA. Type 'yes' to confirm: ")
    if confirm.lower() == 'yes':
        reset_all_databases()
        print("Database reset complete. You can now run your Flask application.")
    else:
        print("Database reset cancelled.")