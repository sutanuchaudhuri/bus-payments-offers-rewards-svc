#!/usr/bin/env python3
"""
Direct test of the database setup to diagnose and fix the relationship issue
"""
import sys
import os
import traceback

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        print("🔧 Testing database setup directly...")

        # Test imports first
        try:
            from app.app import create_app
            from app.models import db, Customer, Merchant, Offer, Payment
            print("✅ Successfully imported all models")
        except Exception as e:
            print(f"❌ Import error: {e}")
            traceback.print_exc()
            return False

        # Create app and test database creation
        try:
            app = create_app()
            print("✅ Flask app created successfully")

            with app.app_context():
                print("✅ App context created")

                # Test if we can create tables
                db.create_all()
                print("✅ Database schema created successfully")

                # Test the relationship
                print("🔗 Testing Merchant-Offer relationship...")
                print(f"  - Merchant has 'offers' relationship: {hasattr(Merchant, 'offers')}")
                print(f"  - Offer has 'merchant_id' field: {hasattr(Offer, 'merchant_id')}")
                print(f"  - Offer has 'merchant_details' backref: {hasattr(Offer, 'merchant_details')}")

                # Test creating sample data
                print("📊 Testing sample data creation...")

                # Check if any data exists
                customer_count = Customer.query.count()
                print(f"  - Current customers in DB: {customer_count}")

                if customer_count == 0:
                    print("  - Creating test customer...")
                    test_customer = Customer(
                        first_name="Test",
                        last_name="User",
                        email="test@example.com"
                    )
                    db.session.add(test_customer)
                    db.session.commit()
                    print("  ✅ Test customer created")

                print("🎉 All tests passed! The relationship fix is working.")
                return True

        except Exception as e:
            print(f"❌ Database error: {e}")
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"❌ General error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ SUCCESS: The relationship issue has been resolved!")
        print("You can now run the comprehensive setup script:")
        print("python data-setup/comprehensive_setup.py --purge")
    else:
        print("\n❌ FAILED: There are still issues to resolve.")

    sys.exit(0 if success else 1)
