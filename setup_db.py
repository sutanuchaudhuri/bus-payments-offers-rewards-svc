#!/usr/bin/env python3
"""
Simple Database Setup Script
"""
import sys
import os
import traceback

# Add current directory to path
sys.path.append('.')

def main():
    try:
        print("Starting database setup...")

        # Import Flask app and models
        print("Importing Flask app...")
        from app.app import create_app
        print("Flask app imported successfully")

        print("Importing models...")
        from app.models import db
        print("Models imported successfully")

        # Create Flask app
        print("Creating Flask app...")
        app = create_app()
        print("Flask app created successfully")

        with app.app_context():
            print("Creating database tables...")
            # Create all database tables
            db.create_all()
            print("Database tables created successfully")

            # Use simplified data setup instead of comprehensive setup
            print("Setting up sample data...")
            from simple_data_setup import create_sample_data

            success = create_sample_data()
            if not success:
                raise Exception("Data setup failed")

            print("Data setup completed")

            # Verify data was loaded
            print("Verifying data...")
            from app.models import Customer, Merchant, Offer, Payment, Reward

            customer_count = Customer.query.count()
            merchant_count = Merchant.query.count()
            offer_count = Offer.query.count()
            payment_count = Payment.query.count()

            # Write results to a file so we can verify
            with open('setup_results.txt', 'w') as f:
                f.write("Database Setup Results:\n")
                f.write("======================\n")
                f.write(f"Customers: {customer_count}\n")
                f.write(f"Merchants: {merchant_count}\n")
                f.write(f"Offers: {offer_count}\n")
                f.write(f"Payments: {payment_count}\n")
                f.write("Setup completed successfully!\n")

            print(f"Setup completed! Customers: {customer_count}, Merchants: {merchant_count}, Offers: {offer_count}, Payments: {payment_count}")

        return True

    except Exception as e:
        error_msg = f"Error: {e}\n{traceback.format_exc()}"
        print(error_msg)
        with open('setup_error.txt', 'w') as f:
            f.write(error_msg)
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
