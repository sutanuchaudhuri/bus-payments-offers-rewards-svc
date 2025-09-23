#!/usr/bin/env python3
"""
Fixed Comprehensive Database Setup Script for Bus Payments & Rewards System
This script can either create a new database or purge and recreate an existing one
with all the updated schema changes including alphanumeric IDs.
"""

import sys
import os
import argparse
import sqlite3
import traceback

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def safe_import_and_log():
    """Safely import required modules and log any issues"""
    try:
        from app.app import create_app
        from app.models import db
        print("✅ Core imports successful")
        return create_app, db
    except Exception as e:
        print(f"❌ Failed to import core modules: {e}")
        print(traceback.format_exc())
        return None, None

class ComprehensiveDatabaseSetup:
    def __init__(self, purge_existing=False):
        print("🔧 Initializing ComprehensiveDatabaseSetup...")

        # Safe import
        create_app_func, db_module = safe_import_and_log()
        if not create_app_func:
            raise Exception("Failed to import required modules")

        self.create_app = create_app_func
        self.db = db_module
        self.app = self.create_app()
        self.purge_existing = purge_existing
        self.db_path = None
        print("✅ Setup initialized successfully")

    def get_database_path(self):
        """Get the path to the SQLite database file"""
        try:
            with self.app.app_context():
                # Extract database path from SQLAlchemy URI
                db_uri = self.app.config['SQLALCHEMY_DATABASE_URI']
                if db_uri.startswith('sqlite:///'):
                    self.db_path = db_uri.replace('sqlite:///', '')
                    if not os.path.isabs(self.db_path):
                        # Make it absolute if it's relative
                        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), self.db_path)
            print(f"✅ Database path: {self.db_path}")
            return self.db_path
        except Exception as e:
            print(f"❌ Error getting database path: {e}")
            return None

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
        """Setup the database schema directly"""
        print("\n🗄️  Setting up database schema...")
        try:
            with self.app.app_context():
                # Drop all tables first to ensure clean schema
                print("🧹 Dropping existing tables to ensure clean schema...")
                self.db.drop_all()
                print("✅ Existing tables dropped")

                # Create all tables with new schema
                print("🏗️  Creating tables with updated schema...")
                self.db.create_all()
                print("✅ Database schema created successfully")
                return True
        except Exception as e:
            print(f"❌ Error creating database schema: {e}")
            print(traceback.format_exc())
            return False
        try:
                    Customer, CreditCard, Merchant, Offer, Payment, Reward,
                    CreditCardProduct, CardType, MerchantCategory, OfferCategory, PaymentStatus
                )
                from datetime import datetime, date, timedelta
                from decimal import Decimal
                import random

                # Check if data already exists
                if Customer.query.count() > 0:
                    print("📊 Data already exists. Skipping creation.")
                    return True

                # Create 10 sample customers
                print("👥 Creating sample customers...")
                customers = []
                for i in range(10):
                    customer = Customer(
                        first_name=f"Customer{i+1}",
                        last_name=f"LastName{i+1}",
                        email=f"customer{i+1}@example.com",
                        phone=f"+1-555-010{i:02d}",
                        date_of_birth=date(1980 + i, 1 + (i % 12), 1 + (i % 28)),
                        address=f"{100 + i*10} Main St, City{i+1}, State{i+1} 1000{i}"
                    )
                    customers.append(customer)
                    self.db.session.add(customer)

                self.db.session.flush()  # Get customer IDs

                # Create credit cards for customers (using correct enum values)
                print("💳 Creating credit cards...")
                card_types = [CardType.VISA, CardType.MASTERCARD, CardType.AMERICAN_EXPRESS]
                product_types = [CreditCardProduct.PLATINUM, CreditCardProduct.GOLD, CreditCardProduct.SILVER]

                for i, customer in enumerate(customers):
                    for j in range(2):  # 2 cards per customer
                        card = CreditCard(
                            customer_id=customer.id,
                            card_number=f"{4000 + i:04d}{0000 + j:04d}{0000 + i:04d}{j:04d}",
                            card_holder_name=f"{customer.first_name} {customer.last_name}",
                            expiry_month=12,
                            expiry_year=2028 + j,
                            product_type=product_types[j % len(product_types)],
                            card_type=card_types[j % len(card_types)],
                            credit_limit=Decimal(f"{5000 + i*1000 + j*2000}.00"),
                            available_credit=Decimal(f"{5000 + i*1000 + j*2000}.00")
                        )
                        self.db.session.add(card)

                # Create merchants (using correct enum values)
                print("🏢 Creating merchants...")
                merchant_data = [
                    ("Delta Airlines", MerchantCategory.AIRLINE, "Major airline carrier"),
                    ("American Airlines", MerchantCategory.AIRLINE, "Major airline carrier"),
                    ("United Airlines", MerchantCategory.AIRLINE, "Major airline carrier"),
                    ("Marriott Hotels", MerchantCategory.HOTEL, "International hotel chain"),
                    ("Hilton Hotels", MerchantCategory.HOTEL, "International hotel chain"),
                    ("Hyatt Hotels", MerchantCategory.HOTEL, "International hotel chain"),
                    ("Olive Garden", MerchantCategory.RESTAURANT, "Italian restaurant chain"),
                    ("McDonald's", MerchantCategory.RESTAURANT, "Fast food chain"),
                    ("Starbucks", MerchantCategory.RESTAURANT, "Coffee chain"),
                    ("State Farm", MerchantCategory.INSURANCE_COMPANY, "Insurance company"),
                    ("Geico", MerchantCategory.INSURANCE_COMPANY, "Insurance company"),
                    ("Enterprise Rent-A-Car", MerchantCategory.AUTOMOTIVE_SERVICE, "Car rental service"),
                    ("Hertz", MerchantCategory.AUTOMOTIVE_SERVICE, "Car rental service"),
                ]

                merchants = []
                for name, category, description in merchant_data:
                    merchant = Merchant(
                        merchant_id=f"MERCH_{len(merchants)+1:03d}",
                        name=name,
                        category=category,
                        description=description
                    )
                    merchants.append(merchant)
                    self.db.session.add(merchant)

                self.db.session.flush()  # Get merchant IDs

                # Create offers (using correct field names from the actual Offer model)
                print("🎁 Creating offers...")
                offer_templates = [
                    ("5% Cashback on Airlines", "Get 5% cashback on all airline bookings", OfferCategory.TRAVEL, Decimal("5.00")),
                    ("10% Off Hotels", "Save 10% on hotel bookings", OfferCategory.TRAVEL, Decimal("10.00")),
                    ("3x Points on Restaurants", "Earn 3x points on restaurant purchases", OfferCategory.DINING, 300),
                    ("15% Off Car Rentals", "Save 15% on car rental bookings", OfferCategory.TRAVEL, Decimal("15.00")),
                    ("2% Cashback on Insurance", "Get 2% cashback on insurance payments", OfferCategory.INSURANCE, Decimal("2.00")),
                ]

                offers = []
                for i, (title, description, offer_category, value) in enumerate(offer_templates):
                    merchant = merchants[i % len(merchants)]

                    # Determine if this is a discount or points offer
                    is_points_offer = isinstance(value, int)

                    offer = Offer(
                        offer_id=f"OFFER_{len(offers)+1:03d}",
                        title=title,
                        description=description,
                        category=offer_category,
                        merchant_id=merchant.id,  # Add the merchant_id foreign key
                        discount_percentage=None if is_points_offer else value,
                        reward_points=value if is_points_offer else 0,
                        start_date=datetime.now(),
                        expiry_date=datetime.now() + timedelta(days=90),
                        is_active=True,
                        terms_and_conditions=f"Terms and conditions for {title}",
                        max_usage_per_customer=5
                    )
                    offers.append(offer)
                    self.db.session.add(offer)

                # Create sample payments
                print("💰 Creating sample payments...")
                self.db.session.flush()  # Ensure all previous objects have IDs
                cards = CreditCard.query.all()  # Get all created credit cards

                for i in range(50):  # 50 sample payments
                    customer = random.choice(customers)
                    merchant = random.choice(merchants)
                    # Get a random credit card for this customer
                    customer_cards = [card for card in cards if card.customer_id == customer.id]
                    if not customer_cards:
                        continue  # Skip if no cards for this customer

                    card = random.choice(customer_cards)
                    amount = Decimal(f"{random.randint(50, 500)}.{random.randint(0, 99):02d}")

                    payment = Payment(
                        credit_card_id=card.id,  # Use credit_card_id instead of customer_id and merchant_id
                        amount=amount,
                        merchant_name=merchant.name,  # Use merchant_name field
                        merchant_category=merchant.category.value,  # Use merchant_category field
                        reference_number=f"PAY_{i+1:06d}",  # Use reference_number instead of payment_id
                        description=f"Payment to {merchant.name}",
                        status=PaymentStatus.COMPLETED,
                        transaction_date=datetime.now() - timedelta(days=random.randint(0, 30))
                    )
                    self.db.session.add(payment)

                # Commit all changes
                self.db.session.commit()
                print("✅ Sample data created successfully")
                return True

        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
            print(traceback.format_exc())
            try:
                self.db.session.rollback()
            except:
                pass
            return False

    def print_database_summary(self):
        """Print a summary of the database contents"""
        try:
            with self.app.app_context():
                from app.models import Customer, CreditCard, Merchant, Offer, Payment, Reward

                customer_count = Customer.query.count()
                card_count = CreditCard.query.count()
                merchant_count = Merchant.query.count()
                offer_count = Offer.query.count()
                payment_count = Payment.query.count()

                print("\n" + "="*70)
                print("📊 DATABASE SETUP SUMMARY")
                print("="*70)
                print(f"👥 Total Customers: {customer_count}")
                print(f"💳 Total Credit Cards: {card_count}")
                print(f"🏪 Total Merchants: {merchant_count}")
                print(f"🎁 Total Offers: {offer_count}")
                print(f"💰 Total Payments: {payment_count}")
                print(f"📍 Database Location: {self.db_path}")
                print("="*70)

        except Exception as e:
            print(f"⚠️  Could not generate summary: {e}")
            print(traceback.format_exc())

    def run_setup(self):
        """Main setup method that orchestrates the entire process"""
        print("🚀 Bus Payments & Rewards System - Comprehensive Database Setup")
        print("="*70)

        try:
            # Get database path
            if not self.get_database_path():
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

            # Step 2: Create sample data
            if not self.create_sample_data():
                return False

            # Print summary
            self.print_database_summary()

            print("\n🎉 Database setup completed successfully!")
            print("\nYou can now start the application with:")
            print("python run.py")

            return True

        except Exception as e:
            print(f"❌ Setup failed with error: {e}")
            print(traceback.format_exc())
            return False

def main():
    try:
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

    except Exception as e:
        print(f"❌ Failed to start setup: {e}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
