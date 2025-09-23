#!/usr/bin/env python3
"""
Comprehensive Database Setup Script for Bus Payments & Rewards System
This script can either create a new database or purge and recreate an existing one
with all the updated schema changes including alphanumeric IDs.
"""

import sys
import os
import argparse
import sqlite3
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from app.models import db
from schema_setup import SchemaSetupManager
from bulk_customer_setup import BulkCustomerSetupManager
from customer_offers_setup import CustomerOffersSetupManager

class ComprehensiveDatabaseSetup:
    def __init__(self, purge_existing=False):
        self.app = create_app()
        self.purge_existing = purge_existing
        self.db_path = None

    def get_database_path(self):
        """Get the path to the SQLite database file"""
        with self.app.app_context():
            # Extract database path from SQLAlchemy URI
            db_uri = self.app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                self.db_path = db_uri.replace('sqlite:///', '')
                if not os.path.isabs(self.db_path):
                    # Make it absolute if it's relative
                    self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), self.db_path)
        return self.db_path

    def backup_existing_database(self):
        """Create a backup of the existing database before purging"""
        if not self.db_path or not os.path.exists(self.db_path):
            return None

        backup_path = f"{self.db_path}.backup_{int(__import__('time').time())}"
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"⚠️  Warning: Could not backup database: {e}")
            return None

    def purge_database(self):
        """Remove the existing database file"""
        if self.db_path and os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
                print(f"✅ Existing database purged: {self.db_path}")
                return True
            except Exception as e:
                print(f"❌ Error purging database: {e}")
                return False
        return True

    def check_database_exists(self):
        """Check if database exists and has tables"""
        if not self.db_path or not os.path.exists(self.db_path):
            return False

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            return len(tables) > 0
        except Exception:
            return False

    def setup_database_schema(self):
        """Setup the database schema using SchemaSetupManager"""
        print("\n🗄️  Setting up database schema...")
        try:
            schema_manager = SchemaSetupManager()
            with self.app.app_context():
                schema_manager.create_update_schema()
            print("✅ Database schema created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating database schema: {e}")
            return False

    def setup_bulk_customers(self):
        """Setup bulk customers using BulkCustomerSetupManager"""
        print("\n👥 Setting up bulk customers (500 customers)...")
        try:
            bulk_manager = BulkCustomerSetupManager()
            with self.app.app_context():
                bulk_manager.setup_bulk_customers()
            print("✅ Bulk customers setup completed")
            return True
        except Exception as e:
            print(f"❌ Error setting up bulk customers: {e}")
            return False

    def setup_customer_offers(self):
        """Setup customer-specific offers using CustomerOffersSetupManager"""
        print("\n🎁 Setting up customer-specific offers (200 activations)...")
        try:
            offers_manager = CustomerOffersSetupManager()
            with self.app.app_context():
                offers_manager.setup_customer_offers()
            print("✅ Customer offers setup completed")
            return True
        except Exception as e:
            print(f"❌ Error setting up customer offers: {e}")
            return False

    def print_database_summary(self):
        """Print a summary of the database contents"""
        try:
            with self.app.app_context():
                from app.models import Customer, CreditCard, Merchant, Offer, CustomerOffer, Payment, Reward

                customer_count = Customer.query.count()
                card_count = CreditCard.query.count()
                merchant_count = Merchant.query.count()
                offer_count = Offer.query.count()
                customer_offer_count = CustomerOffer.query.count()
                payment_count = Payment.query.count()
                reward_count = Reward.query.count()

                print("\n" + "="*70)
                print("📊 DATABASE SETUP SUMMARY")
                print("="*70)
                print(f"👥 Total Customers: {customer_count}")
                print(f"💳 Total Credit Cards: {card_count}")
                print(f"🏪 Total Merchants: {merchant_count}")
                print(f"🎁 Total Offer Templates: {offer_count}")
                print(f"🔗 Total Customer Offer Activations: {customer_offer_count}")
                print(f"💰 Total Transactions: {payment_count}")
                print(f"⭐ Total Rewards: {reward_count}")
                print(f"📍 Database Location: {self.db_path}")
                print("="*70)

        except Exception as e:
            print(f"⚠️  Could not generate summary: {e}")

    def run_setup(self):
        """Main setup method that orchestrates the entire process"""
        print("🚀 Bus Payments & Rewards System - Comprehensive Database Setup")
        print("="*70)

        # Get database path
        self.get_database_path()
        if not self.db_path:
            print("❌ Could not determine database path")
            return False

        print(f"📍 Database path: {self.db_path}")

        # Check if database exists
        db_exists = self.check_database_exists()
        if db_exists and not self.purge_existing:
            print("\n⚠️  Database already exists with tables!")
            print("Use --purge flag to recreate the database, or --help for options")
            return False

        # Handle existing database
        if db_exists and self.purge_existing:
            print("\n🗑️  Purging existing database...")
            # Create backup first
            backup_path = self.backup_existing_database()
            if not self.purge_database():
                return False

        # Setup process
        print(f"\n🔧 {'Recreating' if self.purge_existing else 'Creating'} database with updated schema...")

        # Step 1: Setup schema
        if not self.setup_database_schema():
            return False

        # Step 2: Setup bulk customers
        if not self.setup_bulk_customers():
            return False

        # Step 3: Setup customer offers
        if not self.setup_customer_offers():
            return False

        # Print summary
        self.print_database_summary()

        print("\n🎉 Database setup completed successfully!")
        print("\nYou can now start the application with:")
        print("python run.py")

        return True

def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Database Setup for Bus Payments & Rewards System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python comprehensive_setup.py                    # Create new database (fails if exists)
  python comprehensive_setup.py --purge           # Recreate database (backup existing)
  python comprehensive_setup.py --force-purge     # Recreate without backup
        """
    )

    parser.add_argument(
        '--purge',
        action='store_true',
        help='Purge existing database and recreate (creates backup first)'
    )

    parser.add_argument(
        '--force-purge',
        action='store_true',
        help='Purge existing database without creating backup'
    )

    args = parser.parse_args()

    if args.force_purge:
        args.purge = True

    setup = ComprehensiveDatabaseSetup(purge_existing=args.purge)

    # Override backup behavior for force purge
    if args.force_purge:
        setup.backup_existing_database = lambda: None

    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
