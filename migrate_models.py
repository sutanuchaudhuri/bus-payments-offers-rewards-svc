#!/usr/bin/env python3
"""
Database migration script to update the models schema
Adds missing columns to the offers table
"""
import sys
import os
import sqlite3
from datetime import datetime

# Add the current directory to Python path for app imports
sys.path.insert(0, os.path.dirname(__file__))

def migrate_database():
    """Migrate the database to add missing columns to offers table"""
    db_path = 'instance/credit_card_system.db'

    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("🔄 Starting database migration...")

        # Check if merchant_id column exists in offers table
        cursor.execute("PRAGMA table_info(offers)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'merchant_id' not in columns:
            print("➕ Adding merchant_id column to offers table...")
            cursor.execute("ALTER TABLE offers ADD COLUMN merchant_id INTEGER")
            print("✅ Added merchant_id column")
        else:
            print("ℹ️  merchant_id column already exists")

        if 'min_transaction_amount' not in columns:
            print("➕ Adding min_transaction_amount column to offers table...")
            cursor.execute("ALTER TABLE offers ADD COLUMN min_transaction_amount DECIMAL(10,2)")
            print("✅ Added min_transaction_amount column")
        else:
            print("ℹ️  min_transaction_amount column already exists")

        # Commit changes
        conn.commit()
        print("✅ Database migration completed successfully!")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print("🚀 Starting database schema migration...")
    success = migrate_database()

    if success:
        print("\n✅ Migration completed! You can now start the application.")
        print("Run: python run.py")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
