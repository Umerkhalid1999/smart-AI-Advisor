#!/usr/bin/env python3
"""
Database migration script to add new profile fields to existing User table.
This script safely adds new columns without losing existing data.
"""

import sqlite3
import os
from datetime import datetime

def backup_database():
    """Create a backup of the current database"""
    if os.path.exists('instance/users.db'):
        backup_name = f'instance/users_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        import shutil
        shutil.copy2('instance/users.db', backup_name)
        print(f"✅ Database backed up to: {backup_name}")
        return backup_name
    return None

def migrate_database():
    """Add new columns to the user table"""
    
    # Create backup first
    backup_file = backup_database()
    
    # Connect to database
    db_path = 'instance/users.db'
    if not os.path.exists(db_path):
        print("❌ Database file not found. Creating new database...")
        # If no database exists, create new one with full schema
        from app import app, db
        with app.app_context():
            db.create_all()
            print("✅ New database created with full schema")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current table structure
        cursor.execute("PRAGMA table_info(user)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Current columns: {existing_columns}")
        
        # List of new columns to add
        new_columns = [
            ('profile_image', 'VARCHAR(255)', 'default-avatar.png'),
            ('full_name', 'VARCHAR(150)', None),
            ('phone', 'VARCHAR(20)', None),
            ('date_of_birth', 'DATE', None),
            ('bio', 'TEXT', None),
            ('student_id', 'VARCHAR(50)', None),
            ('department', 'VARCHAR(100)', None),
            ('year_of_study', 'VARCHAR(20)', None),
            ('title', 'VARCHAR(100)', None),
            ('specialization', 'VARCHAR(200)', None),
            ('office_location', 'VARCHAR(100)', None),
            ('office_hours', 'VARCHAR(200)', None),
            ('created_at', 'DATETIME', 'CURRENT_TIMESTAMP'),
            ('updated_at', 'DATETIME', 'CURRENT_TIMESTAMP'),
        ]
        
        # Add each column if it doesn't exist
        for column_name, column_type, default_value in new_columns:
            if column_name not in existing_columns:
                try:
                    if default_value and default_value != 'CURRENT_TIMESTAMP':
                        sql = f"ALTER TABLE user ADD COLUMN {column_name} {column_type} DEFAULT '{default_value}'"
                    elif default_value == 'CURRENT_TIMESTAMP':
                        sql = f"ALTER TABLE user ADD COLUMN {column_name} {column_type} DEFAULT CURRENT_TIMESTAMP"
                    else:
                        sql = f"ALTER TABLE user ADD COLUMN {column_name} {column_type}"
                    
                    cursor.execute(sql)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"⚠️  Warning adding {column_name}: {e}")
            else:
                print(f"⏭️  Column {column_name} already exists")
        
        # Set default values for existing users
        cursor.execute("UPDATE user SET profile_image = 'default-avatar.png' WHERE profile_image IS NULL")
        cursor.execute("UPDATE user SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        cursor.execute("UPDATE user SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(user)")
        final_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Final columns: {final_columns}")
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print(f"👥 Total users in database: {user_count}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if backup_file and os.path.exists(backup_file):
            print(f"🔄 You can restore from backup: {backup_file}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    print("=" * 50)
    migrate_database()
    print("=" * 50)
    print("🎉 Migration process completed!") 