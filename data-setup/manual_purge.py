#!/usr/bin/env python3
"""
Manual Database Purge and Reload Script
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def purge_database():
    """Remove existing database files"""
    print("🗑️  Purging existing database...")

    db_paths = [
        '../instance/credit_card_system.db',
        '../app/instance/credit_card_system.db',
        'credit_card_system.db'
    ]

    removed_count = 0
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"✅ Removed: {db_path}")
                removed_count += 1
            except Exception as e:
                print(f"⚠️  Could not remove {db_path}: {e}")

    if removed_count == 0:
        print("ℹ️  No existing database files found")
    else:
        print(f"✅ Purged {removed_count} database files")

def create_directories():
    """Create instance directories"""
    print("📁 Creating instance directories...")

    dirs = ['../instance', '../app/instance']
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"📁 Created/verified: {dir_path}")

def create_schema_and_load_data():
    """Create schema and load data"""
    print("🏗️  Creating schema and loading data...")

    try:
        from app.app import create_app
        from app.models import db

        app = create_app()
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database schema created")

            # Import and run data setup
            try:
                from comprehensive_data_setup import DataSetupManager
                data_manager = DataSetupManager()
                data_manager.setup_all_data()
                print("✅ Sample data loaded")

                # Verify data
                from app.models import Customer, Merchant, Offer
                customer_count = Customer.query.count()
                merchant_count = Merchant.query.count()
                offer_count = Offer.query.count()

                print(f"📊 Data verification:")
                print(f"   - Customers: {customer_count}")
                print(f"   - Merchants: {merchant_count}")
                print(f"   - Offers: {offer_count}")

                return True

            except Exception as e:
                print(f"⚠️  Error loading sample data: {e}")
                print("✅ Schema created successfully, but sample data loading failed")
                return True

    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        return False

def main():
    print("🚀 Starting manual database purge and reload...")
    print("=" * 60)

    # Step 1: Purge database
    purge_database()

    # Step 2: Create directories
    create_directories()

    # Step 3: Create schema and load data
    if create_schema_and_load_data():
        print("\n" + "=" * 60)
        print("🎉 Database purge and reload completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Start the Flask application: python run.py")
        print("   2. Access Swagger docs: http://localhost:5001/api/docs/")
    else:
        print("\n❌ Database purge and reload failed")
        return False

if __name__ == '__main__':
    main()
