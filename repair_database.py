#!/usr/bin/env python3
"""
Database repair and verification script
Fixes common SQLite database issues and ensures DBeaver compatibility
"""
import os
import sqlite3
import shutil
from datetime import datetime
import sys

def check_and_repair_database():
    """Check database integrity and repair if needed"""
    db_path = 'instance/credit_card_system.db'
    backup_path = f'instance/credit_card_system_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

    print("🔧 Database Repair and Verification Tool")
    print("=" * 50)

    # Check if instance directory exists
    if not os.path.exists('instance'):
        print("📁 Creating instance directory...")
        os.makedirs('instance', exist_ok=True)

    # Check if database file exists
    if not os.path.exists(db_path):
        print("❌ Database file does not exist!")
        print("🔧 Creating new database...")
        create_fresh_database(db_path)
        return True

    print(f"📍 Database path: {os.path.abspath(db_path)}")
    print(f"📊 File size: {os.path.getsize(db_path)} bytes")

    # Create backup before any repairs
    try:
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup created: {backup_path}")
    except Exception as e:
        print(f"⚠️  Could not create backup: {e}")

    # Test database connectivity
    try:
        print("🔍 Testing database connectivity...")
        conn = sqlite3.connect(db_path)

        # Check database integrity
        print("🔍 Checking database integrity...")
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        integrity_result = cursor.fetchone()[0]

        if integrity_result == "ok":
            print("✅ Database integrity: OK")
        else:
            print(f"❌ Database integrity issues: {integrity_result}")
            conn.close()
            return repair_corrupted_database(db_path, backup_path)

        # Check if database has tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("⚠️  Database is empty (no tables found)")
            conn.close()
            create_fresh_database(db_path)
            return True

        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} records")

        # Test a simple query
        cursor.execute("SELECT 1")
        cursor.fetchone()

        conn.close()
        print("✅ Database is fully functional and ready for DBeaver")
        return True

    except sqlite3.DatabaseError as e:
        print(f"❌ Database error: {e}")
        if 'conn' in locals():
            conn.close()
        return repair_corrupted_database(db_path, backup_path)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def repair_corrupted_database(db_path, backup_path):
    """Attempt to repair a corrupted database"""
    print("🔧 Attempting to repair corrupted database...")

    try:
        # Try to dump and restore the database
        temp_sql = 'instance/temp_dump.sql'

        # Dump the database
        with open(temp_sql, 'w') as f:
            conn = sqlite3.connect(db_path)
            for line in conn.iterdump():
                f.write('%s\n' % line)
            conn.close()

        # Remove corrupted database
        os.remove(db_path)

        # Restore from dump
        conn = sqlite3.connect(db_path)
        with open(temp_sql, 'r') as f:
            conn.executescript(f.read())
        conn.close()

        # Clean up
        os.remove(temp_sql)

        print("✅ Database repaired successfully!")
        return True

    except Exception as e:
        print(f"❌ Repair failed: {e}")
        print("🔧 Creating fresh database...")
        return create_fresh_database(db_path)

def create_fresh_database(db_path):
    """Create a fresh database with proper schema"""
    try:
        print("🔧 Creating fresh database with schema...")

        # Import and initialize the Flask app
        sys.path.append('.')
        from app.app import create_app
        from app.models import db

        app = create_app()
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database schema created successfully")

        # Verify the new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        print(f"✅ Created {len(tables)} tables in fresh database")
        return True

    except Exception as e:
        print(f"❌ Failed to create fresh database: {e}")
        return False

def fix_permissions():
    """Fix file permissions for database access"""
    db_path = 'instance/credit_card_system.db'

    try:
        if os.path.exists(db_path):
            # Set read/write permissions for user
            os.chmod(db_path, 0o644)
            print("✅ Database permissions fixed")

        # Ensure instance directory has proper permissions
        if os.path.exists('instance'):
            os.chmod('instance', 0o755)
            print("✅ Instance directory permissions fixed")

    except Exception as e:
        print(f"⚠️  Could not fix permissions: {e}")

def main():
    """Main repair function"""
    print("🚀 Starting database repair process...")

    # Fix permissions first
    fix_permissions()

    # Check and repair database
    success = check_and_repair_database()

    if success:
        print("\n🎉 Database repair completed successfully!")
        print("\n📋 Next steps:")
        print("1. Try opening the database in DBeaver again")
        print("2. If you still have issues, restart DBeaver")
        print("3. Use this path in DBeaver:")
        db_path = os.path.abspath('instance/credit_card_system.db')
        print(f"   {db_path}")

        # Provide DBeaver connection instructions
        print("\n🔗 DBeaver Connection Instructions:")
        print("1. Create New Connection > SQLite")
        print("2. Path: Browse to the database file above")
        print("3. Test Connection")
        print("4. Finish")

    else:
        print("\n❌ Database repair failed!")
        print("Consider running the data setup scripts to create a fresh database:")
        print("python data-setup/comprehensive_setup.py --purge")

if __name__ == "__main__":
    main()
