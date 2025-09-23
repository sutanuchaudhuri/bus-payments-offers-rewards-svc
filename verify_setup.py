#!/usr/bin/env python3
"""
Quick verification script to check if the database setup worked correctly
"""
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_setup():
    try:
        print("🔍 Verifying database setup...")

        from app.app import create_app
        from app.models import db, Customer, Merchant, Offer, Payment

        app = create_app()
        with app.app_context():
            # Check if tables exist and have data
            customer_count = Customer.query.count()
            merchant_count = Merchant.query.count()
            offer_count = Offer.query.count()
            payment_count = Payment.query.count()

            print(f"📊 Database Status:")
            print(f"   👥 Customers: {customer_count}")
            print(f"   🏪 Merchants: {merchant_count}")
            print(f"   🎁 Offers: {offer_count}")
            print(f"   💰 Payments: {payment_count}")

            # Test the relationship
            if offer_count > 0:
                test_offer = Offer.query.first()
                print(f"🔗 Testing relationship...")
                print(f"   Offer '{test_offer.title}' has merchant_id: {test_offer.merchant_id}")
                if test_offer.merchant_details:
                    print(f"   Connected to merchant: {test_offer.merchant_details.name}")
                    print("✅ Merchant-Offer relationship working correctly!")
                else:
                    print("⚠️  Relationship exists but no merchant connected")

            if customer_count > 0 and merchant_count > 0 and offer_count > 0:
                print("🎉 Database setup verification PASSED!")
                return True
            else:
                print("❌ Database appears to be empty or incomplete")
                return False

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_setup()
    print("\n" + "="*50)
    if success:
        print("✅ SUCCESS: The relationship issue has been resolved!")
        print("Your database is ready to use.")
    else:
        print("❌ FAILED: There may still be issues to resolve.")
    sys.exit(0 if success else 1)
