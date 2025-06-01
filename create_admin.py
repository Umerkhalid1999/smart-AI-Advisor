#!/usr/bin/env python3
"""
Script to create a database administrator user
Run this script to create your first admin user
"""

import sys
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def create_admin_user():
    """Create a database administrator user"""
    
    print("=== Create Database Administrator ===\n")
    
    # Get admin details
    username = input("Enter admin username: ").strip()
    if not username:
        print("Error: Username cannot be empty")
        return False
    
    email = input("Enter admin email: ").strip()
    if not email:
        print("Error: Email cannot be empty")
        return False
    
    password = input("Enter admin password: ").strip()
    if not password:
        print("Error: Password cannot be empty")
        return False
    
    full_name = input("Enter admin full name (optional): ").strip()
    
    # Create the admin user
    with app.app_context():
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"Error: Username '{username}' already exists")
            return False
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            print(f"Error: Email '{email}' already registered")
            return False
        
        # Create the admin user
        hashed_password = generate_password_hash(password)
        admin_user = User(
            username=username,
            email=email,
            password=hashed_password,
            role='admin',
            full_name=full_name if full_name else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"\n✅ Success! Admin user '{username}' created successfully!")
            print(f"📧 Email: {email}")
            print(f"🔐 Role: Database Administrator")
            print(f"\nYou can now login with these credentials to access the admin dashboard.")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin user: {str(e)}")
            return False

if __name__ == "__main__":
    print("Student-Advisor System - Admin User Creator")
    print("==========================================\n")
    
    try:
        if create_admin_user():
            print("\n🎉 Admin user creation completed!")
        else:
            print("\n❌ Admin user creation failed!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}") 