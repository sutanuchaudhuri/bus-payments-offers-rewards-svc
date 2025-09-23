#!/usr/bin/env python3
"""
Database Migration Script to handle schema changes
This script will properly migrate the database to include the new merchant_id column
"""

import sys
import os
import sqlite3
import traceback

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """Migrate the existing database to include new schema changes"""
    try:
        print("🔄 Starting database migration...")

        # Get database path from Flask config
        from app.app import create_app
        app = create_app()

        with app.app_context():
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                if not os.path.isabs(db_path):
                    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_path)

            print(f"📍 Database path: {db_path}")

            if not os.path.exists(db_path):
                print("❌ Database does not exist. Please run the setup script first.")
                return False

            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if the offers table exists and what columns it has
            cursor.execute("PRAGMA table_info(offers);")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            print(f"📋 Current offers table columns: {column_names}")

            # Check if merchant_id column exists
            if 'merchant_id' not in column_names:
                print("➕ Adding merchant_id column to offers table...")
                cursor.execute("ALTER TABLE offers ADD COLUMN merchant_id INTEGER;")
                print("✅ merchant_id column added")
            else:
                print("✅ merchant_id column already exists")

            # Check if min_transaction_amount column exists
            if 'min_transaction_amount' not in column_names:
                print("➕ Adding min_transaction_amount column to offers table...")
                cursor.execute("ALTER TABLE offers ADD COLUMN min_transaction_amount NUMERIC(10, 2);")
                print("✅ min_transaction_amount column added")
            else:
                print("✅ min_transaction_amount column already exists")

            # Commit changes
            conn.commit()
            conn.close()

            print("🎉 Database migration completed successfully!")
            return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("🔧 Database Migration Tool")
    print("="*50)

    success = migrate_database()

    if success:
        print("\n✅ Migration completed. You can now run:")
        print("python data-setup/comprehensive_setup.py --purge")
    else:
        print("\n❌ Migration failed. Please check the errors above.")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
