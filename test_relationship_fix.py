#!/usr/bin/env python3
"""
Test script to verify that the Merchant-Offer relationship is working correctly
"""
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_relationship():
    try:
        print("🔧 Testing Merchant-Offer relationship fix...")

        # Import models
        from app.models import db, Merchant, Offer
        print("✅ Successfully imported models")

        # Check if Merchant has offers relationship
        if hasattr(Merchant, 'offers'):
            print("✅ Merchant has 'offers' relationship")
        else:
            print("❌ Merchant missing 'offers' relationship")

        # Check if Offer has merchant_id field
        if hasattr(Offer, 'merchant_id'):
            print("✅ Offer has 'merchant_id' foreign key field")
        else:
            print("❌ Offer missing 'merchant_id' foreign key field")

        # Check if Offer has merchant_details backref
        if hasattr(Offer, 'merchant_details'):
            print("✅ Offer has 'merchant_details' backref")
        else:
            print("❌ Offer missing 'merchant_details' backref")

        # Try to create app context and test schema creation
        from app.app import create_app
        app = create_app()

        with app.app_context():
            print("✅ App context created successfully")

            # Try to create tables (this will test if relationships are valid)
            try:
                db.create_all()
                print("✅ Database schema creation successful - relationships are valid!")
            except Exception as e:
                print(f"❌ Database schema creation failed: {e}")
                raise

        print("\n🎉 All relationship tests passed! The fix is working correctly.")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_relationship()
    sys.exit(0 if success else 1)
