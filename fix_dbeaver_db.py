#!/usr/bin/env python3
"""
Simple database recreator for DBeaver compatibility
"""
import os
import sys
import sqlite3
import shutil
from datetime import datetime

def fix_database_for_dbeaver():
    """Create a fresh, DBeaver-compatible database"""
    db_path = 'instance/credit_card_system.db'

    print("🔧 Fixing database for DBeaver compatibility...")

    # Ensure instance directory exists
    os.makedirs('instance', exist_ok=True)

    # Backup existing database if it exists
    if os.path.exists(db_path):
        backup_path = f'instance/credit_card_system_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        try:
            shutil.move(db_path, backup_path)
            print(f"📦 Moved existing database to: {backup_path}")
        except Exception as e:
            print(f"⚠️  Could not backup existing database: {e}")
            # Force remove the problematic file
            try:
                os.remove(db_path)
                print("🗑️  Removed corrupted database file")
            except:
                pass

    # Create fresh database with schema
    try:
        sys.path.append('.')
        from app.app import create_app
        from app.models import db

        print("🏗️  Creating fresh database with schema...")
        app = create_app()
        with app.app_context():
            db.create_all()

        # Verify the database is working
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        print(f"✅ Created database with {len(tables)} tables")
        print(f"📍 Database location: {os.path.abspath(db_path)}")

        # Set proper permissions
        os.chmod(db_path, 0o644)
        print("✅ Set proper file permissions")

        return True

    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def main():
    success = fix_database_for_dbeaver()

    if success:
        db_path = os.path.abspath('instance/credit_card_system.db')
        print(f"\n🎉 Database fixed successfully!")
        print(f"\n📋 DBeaver Connection Instructions:")
        print(f"1. Open DBeaver")
        print(f"2. New Database Connection > SQLite")
        print(f"3. Path: {db_path}")
        print(f"4. Click 'Test Connection'")
        print(f"5. Click 'OK' and 'Finish'")
        print(f"\n✅ The database should now open properly in DBeaver")
    else:
        print(f"\n❌ Failed to fix database. Try running:")
        print(f"python data-setup/comprehensive_setup.py --purge")

if __name__ == "__main__":
    main()
