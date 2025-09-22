#!/usr/bin/env python3
"""
Database Schema Setup Script for Bus Payments & Rewards System
Creates or updates database schema without populating data
"""

import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from app.models import db
from sqlalchemy import inspect, text

class SchemaSetupManager:
    def __init__(self):
        self.app = create_app()

    def setup_schema(self):
        """Main method to create or update database schema"""
        print("🗄️  Starting database schema setup...")

        with self.app.app_context():
            # Check if database exists and has tables
            self.check_database_status()

            # Create or update schema
            self.create_update_schema()

            # Verify schema creation
            self.verify_schema()

            print("\n✅ Database schema setup completed successfully!")

    def check_database_status(self):
        """Check current database status"""
        print("\n🔍 Checking current database status...")

        try:
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()

            if existing_tables:
                print(f"📋 Found {len(existing_tables)} existing tables:")
                for table in sorted(existing_tables):
                    print(f"   - {table}")
            else:
                print("📭 No existing tables found - fresh database")

        except Exception as e:
            print(f"⚠️  Could not inspect database: {e}")
            print("📭 Treating as fresh database")

    def create_update_schema(self):
        """Create or update database schema"""
        print("\n🏗️  Creating/updating database schema...")

        try:
            # Create all tables based on models
            db.create_all()
            print("✅ Database schema created/updated successfully")

        except Exception as e:
            print(f"❌ Error creating/updating schema: {e}")
            raise

    def verify_schema(self):
        """Verify that all expected tables were created"""
        print("\n🔍 Verifying schema creation...")

        expected_tables = [
            'customers',
            'credit_cards',
            'card_tokens',
            'merchants',
            'offers',
            'payments',
            'rewards'
        ]

        try:
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()

            print("📋 Schema verification results:")
            all_tables_exist = True

            for table in expected_tables:
                if table in existing_tables:
                    print(f"   ✅ {table}")
                else:
                    print(f"   ❌ {table} - MISSING")
                    all_tables_exist = False

            if all_tables_exist:
                print("✅ All expected tables are present")
            else:
                print("⚠️  Some tables are missing")

            # Show additional tables not in expected list
            extra_tables = [t for t in existing_tables if t not in expected_tables]
            if extra_tables:
                print(f"\n📋 Additional tables found:")
                for table in extra_tables:
                    print(f"   + {table}")

        except Exception as e:
            print(f"❌ Error verifying schema: {e}")

    def show_table_info(self):
        """Show detailed information about tables and their columns"""
        print("\n📊 Detailed table information:")

        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            for table_name in sorted(tables):
                print(f"\n📋 Table: {table_name}")
                columns = inspector.get_columns(table_name)

                for column in columns:
                    nullable = "NULL" if column['nullable'] else "NOT NULL"
                    default = f" DEFAULT {column['default']}" if column['default'] else ""
                    print(f"   - {column['name']}: {column['type']} {nullable}{default}")

                # Show indexes
                indexes = inspector.get_indexes(table_name)
                if indexes:
                    print("   Indexes:")
                    for index in indexes:
                        unique = "UNIQUE " if index['unique'] else ""
                        print(f"   - {unique}INDEX {index['name']} on {index['column_names']}")

                # Show foreign keys
                foreign_keys = inspector.get_foreign_keys(table_name)
                if foreign_keys:
                    print("   Foreign Keys:")
                    for fk in foreign_keys:
                        print(f"   - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

        except Exception as e:
            print(f"❌ Error getting table information: {e}")

    def drop_schema(self):
        """Drop all tables (use with caution)"""
        print("\n🗑️  WARNING: This will drop all tables and data!")
        confirmation = input("Type 'DROP ALL TABLES' to confirm: ")

        if confirmation == "DROP ALL TABLES":
            try:
                db.drop_all()
                print("✅ All tables dropped successfully")
            except Exception as e:
                print(f"❌ Error dropping tables: {e}")
        else:
            print("❌ Operation cancelled")

    def backup_schema(self):
        """Create a backup of the current schema structure"""
        print("\n💾 Creating schema backup...")

        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"schema_backup_{timestamp}.sql"

            with open(backup_file, 'w') as f:
                f.write(f"-- Schema backup created on {datetime.now()}\n")
                f.write("-- Bus Payments & Rewards System Database Schema\n\n")

                for table_name in sorted(tables):
                    f.write(f"-- Table: {table_name}\n")

                    # Get CREATE TABLE statement (simplified)
                    columns = inspector.get_columns(table_name)
                    f.write(f"CREATE TABLE {table_name} (\n")

                    column_defs = []
                    for column in columns:
                        nullable = "NULL" if column['nullable'] else "NOT NULL"
                        default = f" DEFAULT {column['default']}" if column['default'] else ""
                        column_defs.append(f"    {column['name']} {column['type']} {nullable}{default}")

                    f.write(",\n".join(column_defs))
                    f.write("\n);\n\n")

            print(f"✅ Schema backup saved to: {backup_file}")

        except Exception as e:
            print(f"❌ Error creating schema backup: {e}")

def main():
    """Main function with command line argument support"""
    import argparse

    parser = argparse.ArgumentParser(description='Database Schema Setup Manager')
    parser.add_argument('action', choices=['create', 'info', 'drop', 'backup'],
                       default='create', nargs='?',
                       help='Action to perform (default: create)')

    args = parser.parse_args()

    schema_manager = SchemaSetupManager()

    if args.action == 'create':
        schema_manager.setup_schema()
    elif args.action == 'info':
        with schema_manager.app.app_context():
            schema_manager.check_database_status()
            schema_manager.show_table_info()
    elif args.action == 'drop':
        with schema_manager.app.app_context():
            schema_manager.drop_schema()
    elif args.action == 'backup':
        with schema_manager.app.app_context():
            schema_manager.backup_schema()

if __name__ == "__main__":
    main()
