#!/usr/bin/env python3
"""
Complete Database Purge and Reload Script for Bus Payments & Rewards System
This script will:
1. Stop any running Flask application
2. Completely delete the database file
3. Recreate the schema from scratch
4. Load comprehensive sample data
"""

import sys
import os
import sqlite3
import subprocess
import psutil
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from app.models import db
from schema_setup import SchemaSetupManager
from comprehensive_data_setup import DataSetupManager

class DatabasePurgeAndReload:
    def __init__(self):
        self.app = create_app()
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'credit_card_system.db')
        self.app_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'instance', 'credit_card_system.db')

    def kill_running_flask_apps(self):
        """Kill any running Flask applications on ports 5001-5010"""
        print("🔍 Checking for running Flask applications...")

        killed_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check if process is Python and running Flask on our ports
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'run.py' in cmdline or ('flask' in cmdline and any(f':{port}' in cmdline for port in range(5001, 5011))):
                        print(f"🛑 Killing Flask process: PID {proc.info['pid']}")
                        proc.terminate()
                        killed_processes.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if killed_processes:
            print(f"✅ Killed {len(killed_processes)} Flask processes")
        else:
            print("ℹ️  No running Flask processes found")

    def purge_database(self):
        """Completely remove the database file"""
        print("\n🗑️  Purging existing database...")

        # List of possible database file locations
        db_paths = [
            self.db_path,
            self.app_db_path,
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credit_card_system.db'),
            os.path.join(os.path.dirname(__file__), 'credit_card_system.db')
        ]

        removed_files = []
        for db_path in db_paths:
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                    removed_files.append(db_path)
                    print(f"🗑️  Removed: {db_path}")
                except Exception as e:
                    print(f"⚠️  Could not remove {db_path}: {e}")

        if removed_files:
            print(f"✅ Purged {len(removed_files)} database files")
        else:
            print("ℹ️  No existing database files found")

    def create_instance_directories(self):
        """Create instance directories if they don't exist"""
        print("\n📁 Creating instance directories...")

        instance_dirs = [
            os.path.dirname(self.db_path),
            os.path.dirname(self.app_db_path)
        ]

        for instance_dir in instance_dirs:
            os.makedirs(instance_dir, exist_ok=True)
            print(f"📁 Created/verified: {instance_dir}")

    def create_fresh_schema(self):
        """Create a completely fresh database schema"""
        print("\n🏗️  Creating fresh database schema...")

        with self.app.app_context():
            try:
                # Drop all tables if they exist
                db.drop_all()

                # Create all tables from scratch
                db.create_all()

                # Verify tables were created
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()

                print(f"✅ Created {len(tables)} tables:")
                for table in sorted(tables):
                    print(f"   - {table}")

                return True

            except Exception as e:
                print(f"❌ Error creating schema: {e}")
                return False

    def load_comprehensive_data(self):
        """Load comprehensive sample data"""
        print("\n📊 Loading comprehensive sample data...")

        try:
            data_manager = DataSetupManager()
            with self.app.app_context():
                # Clean any existing data (just in case)
                data_manager.clean_database()

                # Load all the sample data
                data_manager.setup_all_data()

            return True

        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False

    def verify_database(self):
        """Verify the database has been properly created and populated"""
        print("\n🔍 Verifying database...")

        with self.app.app_context():
            try:
                from app.models import Customer, Merchant, Offer, Payment, CreditCard

                # Count records in key tables
                customer_count = Customer.query.count()
                merchant_count = Merchant.query.count()
                offer_count = Offer.query.count()
                payment_count = Payment.query.count()
                card_count = CreditCard.query.count()

                print(f"📊 Database verification:")
                print(f"   - Customers: {customer_count}")
                print(f"   - Merchants: {merchant_count}")
                print(f"   - Offers: {offer_count}")
                print(f"   - Payments: {payment_count}")
                print(f"   - Credit Cards: {card_count}")

                if all([customer_count > 0, merchant_count > 0, offer_count > 0]):
                    print("✅ Database verification successful!")
                    return True
                else:
                    print("⚠️  Database seems incomplete")
                    return False

            except Exception as e:
                print(f"❌ Database verification failed: {e}")
                return False

    def run_complete_purge_and_reload(self):
        """Execute the complete purge and reload process"""
        print("🚀 Starting complete database purge and reload...")
        print("=" * 60)

        try:
            # Step 1: Kill running Flask apps
            self.kill_running_flask_apps()

            # Step 2: Purge existing database
            self.purge_database()

            # Step 3: Create instance directories
            self.create_instance_directories()

            # Step 4: Create fresh schema
            if not self.create_fresh_schema():
                print("❌ Failed to create schema. Aborting.")
                return False

            # Step 5: Load comprehensive data
            if not self.load_comprehensive_data():
                print("❌ Failed to load data. Aborting.")
                return False

            # Step 6: Verify database
            if not self.verify_database():
                print("⚠️  Database verification had issues")

            print("\n" + "=" * 60)
            print("🎉 Complete database purge and reload successful!")
            print("\n📝 Next steps:")
            print("   1. Start the Flask application: python run.py")
            print("   2. Access Swagger docs: http://localhost:5001/api/docs/")
            print("   3. Test APIs using the Bruno collection")

            return True

        except Exception as e:
            print(f"\n💥 Fatal error during purge and reload: {e}")
            return False

def main():
    """Main execution function"""
    purge_reload = DatabasePurgeAndReload()
    success = purge_reload.run_complete_purge_and_reload()

    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
