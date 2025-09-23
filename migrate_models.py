#!/usr/bin/env python3
"""
Database migration script to update the models schema
Adds missing columns to the offers table and fixes DBeaver connectivity issues
"""
import sys
import os
import sqlite3
import shutil
from datetime import datetime

# Add the current directory to Python path for app imports
sys.path.insert(0, os.path.dirname(__file__))

def check_database_health():
    """Check if database is healthy and accessible"""
    db_path = 'instance/credit_card_system.db'

    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False, "missing"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check integrity
        cursor.execute("PRAGMA integrity_check;")
        integrity = cursor.fetchone()[0]

        if integrity != "ok":
            print(f"❌ Database integrity failed: {integrity}")
            conn.close()
            return False, "corrupted"

        # Check if it has tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        conn.close()

        if not tables:
            print("⚠️  Database exists but has no tables")
            return False, "empty"

        print(f"✅ Database is healthy with {len(tables)} tables")
        return True, "healthy"

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False, "error"

def fix_database_for_dbeaver():
    """Fix database issues that prevent DBeaver from opening it"""
    db_path = 'instance/credit_card_system.db'

    print("🔧 Fixing database for DBeaver compatibility...")

    # Ensure instance directory exists
    os.makedirs('instance', exist_ok=True)

    # Backup existing file if it exists and is not empty
    if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
        backup_path = f'instance/backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        try:
            shutil.copy2(db_path, backup_path)
            print(f"📦 Backup created: {backup_path}")
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")

    # Remove problematic database file
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("🗑️  Removed problematic database file")
        except Exception as e:
            print(f"⚠️  Could not remove database: {e}")

    # Create fresh database with proper schema
    try:
        # Import Flask app and models
        from app.app import create_app
        from app.models import db

        app = create_app()
        with app.app_context():
            db.create_all()
            print("✅ Created fresh database with proper schema")

        # Set proper permissions
        os.chmod(db_path, 0o644)
        print("✅ Set proper file permissions")

        return True

    except Exception as e:
        print(f"❌ Failed to create fresh database: {e}")
        return False

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
        conn.close()
        print("✅ Database migration completed successfully!")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Starting database health check and migration...")

    # First check database health
    is_healthy, status = check_database_health()

    if not is_healthy:
        print(f"🔧 Database needs repair (status: {status})")
        if fix_database_for_dbeaver():
            print("✅ Database repaired successfully")
        else:
            print("❌ Failed to repair database")
            sys.exit(1)

    # Then run migration
    success = migrate_database()

    if success:
        db_abs_path = os.path.abspath('instance/credit_card_system.db')
        print(f"\n✅ Migration completed! Database ready for DBeaver.")
        print(f"\n📋 DBeaver Connection Instructions:")
        print(f"1. Open DBeaver")
        print(f"2. New Connection → SQLite")
        print(f"3. Path: {db_abs_path}")
        print(f"4. Test Connection → Finish")
        print(f"\nDatabase should now open properly in DBeaver!")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
