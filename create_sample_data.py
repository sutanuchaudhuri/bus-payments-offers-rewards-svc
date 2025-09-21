"""
Create sample data for testing booking and refund APIs
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from app.models import (
    db, Customer, CreditCard, Merchant, Offer, Payment, Reward,
    CustomerCategory, CreditRating, CreditCardProduct, MerchantCategory
)
from datetime import datetime, timedelta

def create_sample_data():
    """Create comprehensive sample data for testing"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating sample data for testing...")
            
            # Create sample customers
            customers = [
                Customer(
                    first_name="John",
                    last_name="Doe", 
                    email="john.doe@example.com",
                    phone="+1234567890",
                    address="123 Main St, New York, NY 10001",
                    date_of_birth=datetime(1985, 1, 15).date()
                ),
                Customer(
                    first_name="Jane",
                    last_name="Smith",
                    email="jane.smith@example.com", 
                    phone="+1234567891",
                    address="456 Oak Ave, Los Angeles, CA 90210",
                    date_of_birth=datetime(1990, 3, 22).date()
                ),
                Customer(
                    first_name="Mike",
                    last_name="Johnson",
                    email="mike.johnson@example.com",
                    phone="+1234567892", 
                    address="789 Pine St, Chicago, IL 60601",
                    date_of_birth=datetime(1982, 7, 10).date()
                )
            ]
            
            for customer in customers:
                db.session.add(customer)
            
            # Create sample merchants
            merchants = [
                Merchant(
                    merchant_id="DELTA_001",
                    name="Delta Airlines",
                    description="Major airline providing domestic and international flights",
                    category=MerchantCategory.AIRLINE,
                    contact_email="business@delta.com",
                    phone="+1800221212",
                    address="1030 Delta Blvd, Atlanta, GA 30320",
                    website="https://www.delta.com"
                ),
                Merchant(
                    merchant_id="HILTON_001",
                    name="Hilton Hotels",
                    description="Global hospitality company with luxury hotel chain",
                    category=MerchantCategory.HOTEL, 
                    contact_email="corporate@hilton.com",
                    phone="+1800445866",
                    address="7930 Jones Branch Dr, McLean, VA 22102",
                    website="https://www.hilton.com"
                ),
                Merchant(
                    merchant_id="AMAZON_001",
                    name="Amazon",
                    description="E-commerce and cloud computing company",
                    category=MerchantCategory.E_COMMERCE,
                    contact_email="merchant-support@amazon.com",
                    phone="+1206266000",
                    address="410 Terry Ave N, Seattle, WA 98109",
                    website="https://www.amazon.com"
                )
            ]
            
            for merchant in merchants:
                db.session.add(merchant)
            
            db.session.commit()  # Commit to get IDs
            
            # Create sample credit cards
            credit_cards = [
                CreditCard(
                    customer_id=1,
                    card_number="4111111111111111",
                    card_holder_name="JOHN DOE",
                    expiry_date=datetime(2027, 12, 31).date(),
                    cvv="123",
                    credit_limit=10000.00,
                    available_credit=8500.00,
                    product=CreditCardProduct.PLATINUM,
                    billing_address="123 Main St",
                    billing_city="New York",
                    billing_state="NY",
                    billing_zip="10001"
                ),
                CreditCard(
                    customer_id=2,
                    card_number="4222222222222222",
                    card_holder_name="JANE SMITH", 
                    expiry_date=datetime(2028, 6, 30).date(),
                    cvv="456",
                    credit_limit=15000.00,
                    available_credit=12000.00,
                    product=CreditCardProduct.GOLD,
                    billing_address="456 Oak Ave",
                    billing_city="Los Angeles",
                    billing_state="CA",
                    billing_zip="90210"
                )
            ]
            
            for card in credit_cards:
                db.session.add(card)
            
            # Create sample offers
            offers = [
                Offer(
                    merchant_id=1,
                    title="Delta Flight Booking Rewards",
                    description="Earn 3x points on Delta flights",
                    offer_type="CASHBACK",
                    reward_percentage=3.0,
                    max_reward_amount=500.00,
                    min_purchase_amount=100.00,
                    start_date=datetime.now().date(),
                    end_date=(datetime.now() + timedelta(days=365)).date(),
                    is_active=True
                ),
                Offer(
                    merchant_id=2,
                    title="Hilton Hotel Stays",
                    description="Get 5% cashback on hotel bookings",
                    offer_type="CASHBACK",
                    reward_percentage=5.0,
                    max_reward_amount=300.00,
                    min_purchase_amount=150.00,
                    start_date=datetime.now().date(),
                    end_date=(datetime.now() + timedelta(days=365)).date(),
                    is_active=True
                ),
                Offer(
                    merchant_id=3,
                    title="Amazon Shopping Bonus",
                    description="Extra 2% on Amazon purchases",
                    offer_type="CASHBACK", 
                    reward_percentage=2.0,
                    max_reward_amount=200.00,
                    min_purchase_amount=50.00,
                    start_date=datetime.now().date(),
                    end_date=(datetime.now() + timedelta(days=365)).date(),
                    is_active=True
                )
            ]
            
            for offer in offers:
                db.session.add(offer)
            
            # Create sample payments
            payments = [
                Payment(
                    customer_id=1,
                    credit_card_id=1,
                    merchant_id=1,
                    amount=450.00,
                    transaction_date=datetime.utcnow() - timedelta(days=5),
                    description="Flight booking - NYC to LAX",
                    status="COMPLETED",
                    payment_method="CREDIT_CARD",
                    transaction_id="TXN001",
                    authorization_code="AUTH001"
                ),
                Payment(
                    customer_id=2,
                    credit_card_id=2,
                    merchant_id=2,
                    amount=280.00,
                    transaction_date=datetime.utcnow() - timedelta(days=3),
                    description="Hotel reservation - 2 nights",
                    status="COMPLETED", 
                    payment_method="CREDIT_CARD",
                    transaction_id="TXN002",
                    authorization_code="AUTH002"
                ),
                Payment(
                    customer_id=1,
                    credit_card_id=1,
                    merchant_id=3,
                    amount=125.50,
                    transaction_date=datetime.utcnow() - timedelta(days=1),
                    description="Amazon shopping order",
                    status="COMPLETED",
                    payment_method="CREDIT_CARD", 
                    transaction_id="TXN003",
                    authorization_code="AUTH003"
                )
            ]
            
            for payment in payments:
                db.session.add(payment)
            
            # Create sample rewards
            rewards = [
                Reward(
                    customer_id=1,
                    payment_id=1,
                    offer_id=1,
                    points_earned=1350,  # 3% of $450
                    cashback_amount=13.50,
                    status="EARNED",
                    earned_date=datetime.utcnow() - timedelta(days=5)
                ),
                Reward(
                    customer_id=2,
                    payment_id=2, 
                    offer_id=2,
                    points_earned=1400,  # 5% of $280
                    cashback_amount=14.00,
                    status="REDEEMED",
                    earned_date=datetime.utcnow() - timedelta(days=3),
                    redeemed_date=datetime.utcnow() - timedelta(days=1)
                )
            ]
            
            for reward in rewards:
                db.session.add(reward)
            
            db.session.commit()
            
            print("Sample data created successfully!")
            print("Created:")
            print("- 3 customers")
            print("- 3 merchants")
            print("- 2 credit cards")
            print("- 3 offers")
            print("- 3 payments")
            print("- 2 rewards")
            
            return True
            
        except Exception as e:
            print(f"Error creating sample data: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    create_sample_data()