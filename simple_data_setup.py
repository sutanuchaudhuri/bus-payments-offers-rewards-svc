#!/usr/bin/env python3
"""
Simplified Data Setup Script - Alternative to comprehensive_data_setup.py
This script creates basic sample data without complex dependencies
"""
import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add current directory to path
sys.path.append('.')

def create_sample_data():
    """Create basic sample data for testing"""
    try:
        print("🚀 Starting simplified data setup...")

        # Import Flask app and models
        from app.app import create_app
        from app.models import (
            db, Customer, CreditCard, Merchant, Offer, Payment, Reward,
            CreditCardProduct, CardType, MerchantCategory, OfferType, PaymentStatus
        )

        app = create_app()

        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            print("✅ Database tables created/verified")

            # Check if data already exists
            if Customer.query.count() > 0:
                print("📊 Data already exists. Skipping setup.")
                print(f"   - Customers: {Customer.query.count()}")
                print(f"   - Merchants: {Merchant.query.count()}")
                print(f"   - Offers: {Offer.query.count()}")
                print(f"   - Payments: {Payment.query.count()}")
                return True

            # 1. Create sample customer
            print("👤 Creating sample customer...")
            customer = Customer(
                first_name="Sutanu",
                last_name="Chaudhuri",
                email="sutanu.chaudhuri@example.com",
                phone="+1-484-555-0123",
                date_of_birth=date(1982, 10, 10),
                address="426 Elton Farm, Glen Mills, PA 19342"
            )
            db.session.add(customer)
            db.session.flush()  # Get the ID

            # 2. Create sample credit cards
            print("💳 Creating sample credit cards...")
            cards = [
                {
                    "card_number": "4111111111111111",
                    "card_holder_name": "Sutanu Chaudhuri",
                    "expiry_month": 12,
                    "expiry_year": 2028,
                    "product_type": CreditCardProduct.PLATINUM,
                    "card_type": CardType.VISA,
                    "credit_limit": Decimal("15000.00")
                },
                {
                    "card_number": "5555555555554444",
                    "card_holder_name": "Sutanu Chaudhuri",
                    "expiry_month": 8,
                    "expiry_year": 2027,
                    "product_type": CreditCardProduct.GOLD,
                    "card_type": CardType.MASTERCARD,
                    "credit_limit": Decimal("10000.00")
                }
            ]

            for card_data in cards:
                credit_card = CreditCard(
                    customer_id=customer.id,
                    available_credit=card_data["credit_limit"],
                    **card_data
                )
                db.session.add(credit_card)

            # 3. Create sample merchants
            print("🏢 Creating sample merchants...")
            merchants = [
                {
                    "name": "Delta Airlines",
                    "category": MerchantCategory.AIRLINE,
                    "description": "Major airline carrier"
                },
                {
                    "name": "Marriott Hotels",
                    "category": MerchantCategory.HOTEL,
                    "description": "International hotel chain"
                },
                {
                    "name": "Olive Garden",
                    "category": MerchantCategory.RESTAURANT,
                    "description": "Italian restaurant chain"
                },
                {
                    "name": "State Farm",
                    "category": MerchantCategory.INSURANCE,
                    "description": "Insurance company"
                },
                {
                    "name": "Enterprise Rent-A-Car",
                    "category": MerchantCategory.CAB_RENTAL,
                    "description": "Car rental service"
                }
            ]

            merchant_objects = []
            for merchant_data in merchants:
                merchant = Merchant(**merchant_data)
                db.session.add(merchant)
                merchant_objects.append(merchant)

            db.session.flush()  # Get merchant IDs

            # 4. Create sample offers
            print("🎁 Creating sample offers...")
            offers = [
                {
                    "merchant_id": merchant_objects[0].id,  # Delta
                    "title": "5% Cashback on Flights",
                    "description": "Get 5% cashback on all flight bookings",
                    "offer_type": OfferType.CASHBACK,
                    "value": Decimal("5.00"),
                    "valid_from": datetime.now(),
                    "valid_until": datetime.now() + timedelta(days=90),
                    "is_active": True
                },
                {
                    "merchant_id": merchant_objects[1].id,  # Marriott
                    "title": "10% Off Hotel Stays",
                    "description": "Save 10% on hotel bookings",
                    "offer_type": OfferType.DISCOUNT,
                    "value": Decimal("10.00"),
                    "valid_from": datetime.now(),
                    "valid_until": datetime.now() + timedelta(days=60),
                    "is_active": True
                }
            ]

            offer_objects = []
            for offer_data in offers:
                offer = Offer(**offer_data)
                db.session.add(offer)
                offer_objects.append(offer)

            # 5. Create sample payments
            print("💰 Creating sample payments...")
            payments = [
                {
                    "customer_id": customer.id,
                    "merchant_id": merchant_objects[0].id,
                    "amount": Decimal("250.00"),
                    "description": "Flight booking - LAX to JFK",
                    "status": PaymentStatus.COMPLETED
                },
                {
                    "customer_id": customer.id,
                    "merchant_id": merchant_objects[1].id,
                    "amount": Decimal("180.00"),
                    "description": "Hotel booking - 2 nights",
                    "status": PaymentStatus.COMPLETED
                }
            ]

            for payment_data in payments:
                payment = Payment(**payment_data)
                db.session.add(payment)

            # Commit all changes
            db.session.commit()

            # Verify data
            print("✅ Data setup completed successfully!")
            print(f"   - Customers: {Customer.query.count()}")
            print(f"   - Credit Cards: {CreditCard.query.count()}")
            print(f"   - Merchants: {Merchant.query.count()}")
            print(f"   - Offers: {Offer.query.count()}")
            print(f"   - Payments: {Payment.query.count()}")

            return True

    except Exception as e:
        print(f"❌ Error during data setup: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = create_sample_data()
    if success:
        print("🎉 Setup completed successfully!")
    else:
        print("💥 Setup failed!")
    sys.exit(0 if success else 1)
