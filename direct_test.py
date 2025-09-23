#!/usr/bin/env python3
"""
Direct test to check database setup and diagnose any issues
"""
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🔧 Direct Database Test")
    print("=" * 40)

    try:
        # Test 1: Import check
        print("1. Testing imports...")
        from app.app import create_app
        from app.models import db, Customer, Merchant, Offer, Payment
        print("   ✅ Imports successful")

        # Test 2: App creation
        print("2. Creating Flask app...")
        app = create_app()
        print("   ✅ App created")

        # Test 3: Database connection
        print("3. Testing database connection...")
        with app.app_context():
            # Get database path
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"   📍 Database URI: {db_uri}")

            # Check if database file exists
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                if not os.path.isabs(db_path):
                    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)

                print(f"   📁 Database file path: {db_path}")
                print(f"   📄 Database file exists: {os.path.exists(db_path)}")

                if os.path.exists(db_path):
                    print(f"   📊 Database file size: {os.path.getsize(db_path)} bytes")

            # Test 4: Schema check
            print("4. Testing database schema...")
            try:
                db.create_all()
                print("   ✅ Schema creation successful")

                # Test 5: Basic queries
                print("5. Testing basic queries...")
                customer_count = Customer.query.count()
                merchant_count = Merchant.query.count()
                offer_count = Offer.query.count()
                payment_count = Payment.query.count()

                print(f"   👥 Customers: {customer_count}")
                print(f"   🏪 Merchants: {merchant_count}")
                print(f"   🎁 Offers: {offer_count}")
                print(f"   💰 Payments: {payment_count}")

                # Test 6: Relationship check
                if offer_count > 0:
                    print("6. Testing Merchant-Offer relationship...")
                    test_offer = Offer.query.first()
                    print(f"   🎁 First offer: '{test_offer.title}'")
                    print(f"   🔗 Has merchant_id: {test_offer.merchant_id}")

                    if test_offer.merchant_details:
                        print(f"   🏪 Connected merchant: {test_offer.merchant_details.name}")
                        print("   ✅ Merchant-Offer relationship working!")
                    else:
                        print("   ⚠️  No merchant relationship found")

                print("\n🎉 ALL TESTS PASSED!")
                print("The database setup is working correctly.")
                return True

            except Exception as e:
                print(f"   ❌ Schema/Query error: {e}")
                import traceback
                traceback.print_exc()
                return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 40)
    if success:
        print("✅ SUCCESS: Database is working correctly!")
    else:
        print("❌ FAILED: Issues found that need to be resolved.")

    sys.exit(0 if success else 1)
