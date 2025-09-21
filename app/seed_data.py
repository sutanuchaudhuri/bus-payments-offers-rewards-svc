import sys
import os

# Add the parent directory to Python path for app imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models import (
    db, Customer, Merchant, CreditCard, Payment, Offer, Reward, 
    MerchantOfferHistory, CustomerProfileHistory, CustomerOffer, OfferCategory, 
    MerchantCategory, CreditCardProduct, PaymentStatus, RewardStatus
)
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

def create_sample_data():
    """Create sample data for testing the API"""
    
    print("Creating sample data...")
    
    # Create sample customers
    customers_data = [
        {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@email.com',
            'phone': '+1-555-0101',
            'date_of_birth': date(1985, 3, 15),
            'address': '123 Main St, New York, NY 10001'
        },
        {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@email.com',
            'phone': '+1-555-0102',
            'date_of_birth': date(1990, 7, 22),
            'address': '456 Oak Ave, Los Angeles, CA 90001'
        },
        {
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'email': 'bob.johnson@email.com',
            'phone': '+1-555-0103',
            'date_of_birth': date(1982, 12, 8),
            'address': '789 Pine Rd, Chicago, IL 60601'
        },
        {
            'first_name': 'Alice',
            'last_name': 'Williams',
            'email': 'alice.williams@email.com',
            'phone': '+1-555-0104',
            'date_of_birth': date(1988, 5, 30),
            'address': '321 Elm St, Houston, TX 77001'
        }
    ]
    
    customers = []
    for customer_data in customers_data:
        customer = Customer(**customer_data)
        db.session.add(customer)
        customers.append(customer)
    
    db.session.commit()
    print(f"Created {len(customers)} customers")
    
    # Create sample merchants
    merchants_data = [
        {
            'merchant_id': 'AMZN001',
            'name': 'Amazon',
            'description': 'Online retail marketplace',
            'category': MerchantCategory.E_COMMERCE,
            'website': 'https://amazon.com',
            'contact_email': 'business@amazon.com',
            'phone': '+1-206-266-1000'
        },
        {
            'merchant_id': 'SBUX001',
            'name': 'Starbucks',
            'description': 'Coffee chain and roastery',
            'category': MerchantCategory.RESTAURANT,
            'website': 'https://starbucks.com',
            'contact_email': 'partners@starbucks.com',
            'phone': '+1-800-782-7282'
        },
        {
            'merchant_id': 'UNCI001',
            'name': 'United Airlines',
            'description': 'Major American airline',
            'category': MerchantCategory.AIRLINE,
            'website': 'https://united.com',
            'contact_email': 'customer.care@united.com',
            'phone': '+1-800-864-8331'
        },
        {
            'merchant_id': 'SHEL001',
            'name': 'Shell',
            'description': 'Gas stations and fuel provider',
            'category': MerchantCategory.GAS_STATION,
            'website': 'https://shell.us',
            'contact_email': 'customer.service@shell.com',
            'phone': '+1-800-248-4257'
        },
        {
            'merchant_id': 'MARR001',
            'name': 'Marriott',
            'description': 'Luxury hotel chain',
            'category': MerchantCategory.HOTEL,
            'website': 'https://marriott.com',
            'contact_email': 'customer.care@marriott.com',
            'phone': '+1-800-627-7468'
        },
        {
            'merchant_id': 'TARG001',
            'name': 'Target',
            'description': 'Retail chain store',
            'category': MerchantCategory.RETAIL_STORE,
            'website': 'https://target.com',
            'contact_email': 'guest.relations@target.com',
            'phone': '+1-800-440-0680'
        },
        {
            'merchant_id': 'UBER001',
            'name': 'Uber',
            'description': 'Ride-sharing and delivery service',
            'category': MerchantCategory.E_COMMERCE,
            'website': 'https://uber.com',
            'contact_email': 'support@uber.com',
            'phone': '+1-800-353-8237'
        },
        {
            'merchant_id': 'WHOL001',
            'name': 'Whole Foods Market',
            'description': 'Organic grocery store chain',
            'category': MerchantCategory.GROCERY_STORE,
            'website': 'https://wholefoodsmarket.com',
            'contact_email': 'customer.questions@wholefoods.com',
            'phone': '+1-844-936-8255'
        },
        {
            'merchant_id': 'NETF001',
            'name': 'Netflix',
            'description': 'Streaming entertainment service',
            'category': MerchantCategory.SUBSCRIPTION_SERVICE,
            'website': 'https://netflix.com',
            'contact_email': 'help@netflix.com',
            'phone': '+1-866-579-7172'
        },
        {
            'merchant_id': 'EQUI001',
            'name': 'Equinox',
            'description': 'Premium fitness club',
            'category': MerchantCategory.FITNESS_CENTER,
            'website': 'https://equinox.com',
            'contact_email': 'member.services@equinox.com',
            'phone': '+1-212-774-6363'
        }
    ]
    
    merchants = []
    for merchant_data in merchants_data:
        merchant = Merchant(**merchant_data)
        db.session.add(merchant)
        merchants.append(merchant)
    
    db.session.commit()
    print(f"Created {len(merchants)} merchants")
    
    # Create sample credit cards
    credit_cards_data = [
        {
            'customer_id': customers[0].id,
            'card_number': '4111111111111111',
            'card_holder_name': 'John Doe',
            'expiry_month': 12,
            'expiry_year': 2026,
            'product_type': CreditCardProduct.PLATINUM,
            'credit_limit': Decimal('10000.00'),
            'available_credit': Decimal('8500.00')
        },
        {
            'customer_id': customers[0].id,
            'card_number': '4222222222222222',
            'card_holder_name': 'John Doe',
            'expiry_month': 8,
            'expiry_year': 2025,
            'product_type': CreditCardProduct.GOLD,
            'credit_limit': Decimal('5000.00'),
            'available_credit': Decimal('4200.00')
        },
        {
            'customer_id': customers[1].id,
            'card_number': '4333333333333333',
            'card_holder_name': 'Jane Smith',
            'expiry_month': 6,
            'expiry_year': 2027,
            'product_type': CreditCardProduct.GOLD,
            'credit_limit': Decimal('7500.00'),
            'available_credit': Decimal('6800.00')
        },
        {
            'customer_id': customers[2].id,
            'card_number': '4444444444444444',
            'card_holder_name': 'Bob Johnson',
            'expiry_month': 3,
            'expiry_year': 2026,
            'product_type': CreditCardProduct.SILVER,
            'credit_limit': Decimal('3000.00'),
            'available_credit': Decimal('2500.00')
        },
        {
            'customer_id': customers[3].id,
            'card_number': '4555555555555555',
            'card_holder_name': 'Alice Williams',
            'expiry_month': 10,
            'expiry_year': 2025,
            'product_type': CreditCardProduct.BASIC,
            'credit_limit': Decimal('2000.00'),
            'available_credit': Decimal('1800.00')
        }
    ]
    
    credit_cards = []
    for card_data in credit_cards_data:
        credit_card = CreditCard(**card_data)
        db.session.add(credit_card)
        credit_cards.append(credit_card)
    
    db.session.commit()
    print(f"Created {len(credit_cards)} credit cards")
    
    # Create sample offers
    now = datetime.utcnow()
    offers_data = [
        {
            'title': '5% Cashback on Travel Bookings',
            'description': 'Earn 5% cashback on all travel purchases including flights, hotels, and car rentals.',
            'category': OfferCategory.TRAVEL,
            'merchant_id': merchants[2].id,  # United Airlines
            'discount_percentage': Decimal('5.00'),
            'max_discount_amount': Decimal('200.00'),
            'min_transaction_amount': Decimal('100.00'),
            'reward_points': 500,
            'start_date': now - timedelta(days=30),
            'expiry_date': now + timedelta(days=60),
            'terms_and_conditions': 'Valid on United Airlines bookings only. Maximum 5 transactions per month.',
            'is_active': True,
            'max_usage_per_customer': 5
        },
        {
            'title': 'Amazon 10% Discount',
            'description': 'Get 10% discount on Amazon purchases up to $100.',
            'category': OfferCategory.SHOPPING,
            'merchant_id': merchants[0].id,  # Amazon
            'discount_percentage': Decimal('10.00'),
            'max_discount_amount': Decimal('100.00'),
            'min_transaction_amount': Decimal('50.00'),
            'reward_points': 200,
            'start_date': now - timedelta(days=15),
            'expiry_date': now + timedelta(days=45),
            'terms_and_conditions': 'Valid on Amazon.com purchases only. Excludes gift cards.',
            'is_active': True,
            'max_usage_per_customer': 3
        },
        {
            'title': 'Starbucks Dining Rewards',
            'description': 'Earn double points on all Starbucks purchases.',
            'category': OfferCategory.DINING,
            'merchant_id': merchants[1].id,  # Starbucks
            'discount_percentage': None,
            'max_discount_amount': None,
            'min_transaction_amount': Decimal('5.00'),
            'reward_points': 100,  # Bonus points
            'start_date': now - timedelta(days=7),
            'expiry_date': now + timedelta(days=90),
            'terms_and_conditions': 'Valid at Starbucks locations. Points are doubled automatically.',
            'is_active': True,
            'max_usage_per_customer': 20
        },
        {
            'title': 'Shell Gas Station 3% Cashback',
            'description': 'Get 3% cashback on all Shell gas purchases.',
            'category': OfferCategory.FUEL,
            'merchant_id': merchants[3].id,  # Shell
            'discount_percentage': Decimal('3.00'),
            'max_discount_amount': Decimal('25.00'),
            'min_transaction_amount': Decimal('20.00'),
            'reward_points': 50,
            'start_date': now,
            'expiry_date': now + timedelta(days=30),
            'terms_and_conditions': 'Valid at participating Shell stations only.',
            'is_active': True,
            'max_usage_per_customer': 10
        },
        {
            'title': 'Marriott Hotel Luxury Stay Bonus',
            'description': 'Earn bonus points and 5% discount on Marriott stays.',
            'category': OfferCategory.TRAVEL,
            'merchant_id': merchants[4].id,  # Marriott
            'discount_percentage': Decimal('5.00'),
            'max_discount_amount': Decimal('150.00'),
            'min_transaction_amount': Decimal('200.00'),
            'reward_points': 1000,
            'start_date': now,
            'expiry_date': now + timedelta(days=120),
            'terms_and_conditions': 'Valid at participating Marriott properties worldwide.',
            'is_active': True,
            'max_usage_per_customer': 5
        },
        {
            'title': 'Target Shopping Spree',
            'description': 'Get 7% discount on Target purchases over $75.',
            'category': OfferCategory.SHOPPING,
            'merchant_id': merchants[5].id,  # Target
            'discount_percentage': Decimal('7.00'),
            'max_discount_amount': Decimal('50.00'),
            'min_transaction_amount': Decimal('75.00'),
            'reward_points': 150,
            'start_date': now - timedelta(days=5),
            'expiry_date': now + timedelta(days=60),
            'terms_and_conditions': 'Valid at Target stores and online. Excludes pharmacy and gift cards.',
            'is_active': True,
            'max_usage_per_customer': 4
        },
        {
            'title': 'Whole Foods Grocery Rewards',
            'description': 'Earn extra points on organic grocery purchases.',
            'category': OfferCategory.GROCERY,
            'merchant_id': merchants[7].id,  # Whole Foods
            'discount_percentage': None,
            'max_discount_amount': None,
            'min_transaction_amount': Decimal('30.00'),
            'reward_points': 200,
            'start_date': now - timedelta(days=10),
            'expiry_date': now + timedelta(days=75),
            'terms_and_conditions': 'Valid on organic products only. Minimum $30 purchase required.',
            'is_active': True,
            'max_usage_per_customer': 15
        },
        {
            'title': 'Netflix Subscription Discount',
            'description': 'Get 20% off your first 3 months of Netflix Premium.',
            'category': OfferCategory.SUBSCRIPTION,
            'merchant_id': merchants[8].id,  # Netflix
            'discount_percentage': Decimal('20.00'),
            'max_discount_amount': Decimal('30.00'),
            'min_transaction_amount': Decimal('15.00'),
            'reward_points': 75,
            'start_date': now + timedelta(days=2),
            'expiry_date': now + timedelta(days=90),
            'terms_and_conditions': 'Valid for new Premium subscriptions only. Limited time offer.',
            'is_active': True,
            'max_usage_per_customer': 1
        },
        {
            'title': 'Equinox Fitness Membership Bonus',
            'description': 'Get bonus rewards on Equinox membership fees.',
            'category': OfferCategory.SPORTS_FITNESS,
            'merchant_id': merchants[9].id,  # Equinox
            'discount_percentage': None,
            'max_discount_amount': None,
            'min_transaction_amount': Decimal('150.00'),
            'reward_points': 500,
            'start_date': now - timedelta(days=3),
            'expiry_date': now + timedelta(days=45),
            'terms_and_conditions': 'Valid on monthly membership fees only.',
            'is_active': True,
            'max_usage_per_customer': 6
        },
        {
            'title': 'Generic Entertainment Cashback',
            'description': 'Get 4% cashback on entertainment purchases.',
            'category': OfferCategory.ENTERTAINMENT,
            'merchant_id': None,  # Generic offer
            'merchant_name': 'Entertainment Venues',
            'discount_percentage': Decimal('4.00'),
            'max_discount_amount': Decimal('40.00'),
            'min_transaction_amount': Decimal('25.00'),
            'reward_points': 100,
            'start_date': now - timedelta(days=20),
            'expiry_date': now + timedelta(days=80),
            'terms_and_conditions': 'Valid at movie theaters, concerts, and entertainment venues.',
            'is_active': True,
            'max_usage_per_customer': 8
        }
    ]
    
    offers = []
    for offer_data in offers_data:
        offer = Offer(**offer_data)
        db.session.add(offer)
        offers.append(offer)
    
    db.session.commit()
    print(f"Created {len(offers)} offers")
    
    # Activate some offers for customers
    activations_data = [
        {'customer_id': customers[0].id, 'offer_id': offers[0].id},
        {'customer_id': customers[0].id, 'offer_id': offers[1].id},
        {'customer_id': customers[1].id, 'offer_id': offers[2].id},
        {'customer_id': customers[2].id, 'offer_id': offers[0].id},
        {'customer_id': customers[2].id, 'offer_id': offers[3].id},
        {'customer_id': customers[3].id, 'offer_id': offers[1].id},
        {'customer_id': customers[3].id, 'offer_id': offers[2].id}
    ]
    
    customer_offers = []
    for activation_data in activations_data:
        customer_offer = CustomerOffer(
            customer_id=activation_data['customer_id'],
            offer_id=activation_data['offer_id'],
            activation_date=now - timedelta(days=random.randint(1, 20)),
            usage_count=random.randint(0, 2),
            total_savings=Decimal(str(random.uniform(5.0, 50.0))),
            is_active=True
        )
        db.session.add(customer_offer)
        customer_offers.append(customer_offer)
    
    db.session.commit()
    print(f"Created {len(customer_offers)} offer activations")
    
    # Create sample payments
    merchant_names = [merchant.name for merchant in merchants]
    merchant_categories = [
        'DINING', 'SHOPPING', 'TRAVEL', 'FUEL', 'GROCERY',
        'ENTERTAINMENT', 'FITNESS', 'SUBSCRIPTION', 'RETAIL'
    ]
    
    payments = []
    for i in range(30):  # Create 30 sample payments
        card = random.choice(credit_cards)
        merchant_name = random.choice(merchant_names)
        category = random.choice(merchant_categories)
        amount = Decimal(str(random.uniform(15.0, 500.0))).quantize(Decimal('0.01'))
        
        payment = Payment(
            credit_card_id=card.id,
            amount=amount,
            merchant_name=merchant_name,
            merchant_category=category,
            transaction_date=now - timedelta(days=random.randint(1, 90)),
            status=PaymentStatus.COMPLETED,
            reference_number=f"PAY-{datetime.now().strftime('%Y%m%d')}-{i:04d}",
            description=f"Payment to {merchant_name}"
        )
        db.session.add(payment)
        payments.append(payment)
        
        # Update available credit
        card.available_credit -= amount
    
    db.session.commit()
    print(f"Created {len(payments)} payments")
    
    # Create sample rewards based on payments
    rewards = []
    for payment in payments:
        # Calculate reward points based on card type
        multipliers = {
            'PLATINUM': 3.0,
            'GOLD': 2.0,
            'SILVER': 1.5,
            'BASIC': 1.0
        }
        
        card = payment.credit_card
        multiplier = multipliers.get(card.product_type.value, 1.0)
        
        # Bonus points for dining and travel
        if payment.merchant_category in ['DINING', 'TRAVEL']:
            multiplier *= 1.5
        
        base_points = int(float(payment.amount))
        reward_points = int(base_points * multiplier)
        dollar_value = Decimal(str(reward_points * 0.01))
        
        reward = Reward(
            customer_id=card.customer_id,
            payment_id=payment.id,
            points_earned=reward_points,
            dollar_value=dollar_value,
            status=RewardStatus.EARNED,
            earned_date=payment.transaction_date,
            expiry_date=payment.transaction_date + timedelta(days=730),  # 2 years
            description=f"Reward for {payment.merchant_name} purchase"
        )
        db.session.add(reward)
        rewards.append(reward)
    
    # Add some manual rewards
    manual_rewards_data = [
        {
            'customer_id': customers[0].id,
            'points_earned': 1000,
            'description': 'Welcome bonus for new customer',
            'expiry_date': now + timedelta(days=365)
        },
        {
            'customer_id': customers[1].id,
            'points_earned': 500,
            'description': 'Birthday bonus points',
            'expiry_date': now + timedelta(days=365)
        },
        {
            'customer_id': customers[2].id,
            'points_earned': 750,
            'description': 'Referral bonus',
            'expiry_date': now + timedelta(days=365)
        }
    ]
    
    for reward_data in manual_rewards_data:
        reward = Reward(
            customer_id=reward_data['customer_id'],
            points_earned=reward_data['points_earned'],
            dollar_value=Decimal(str(reward_data['points_earned'] * 0.01)),
            status=RewardStatus.EARNED,
            earned_date=now - timedelta(days=random.randint(1, 30)),
            expiry_date=reward_data['expiry_date'],
            description=reward_data['description']
        )
        db.session.add(reward)
        rewards.append(reward)
    
    db.session.commit()
    print(f"Created {len(rewards)} rewards")
    
    # Redeem some rewards
    for i in range(5):
        reward = random.choice([r for r in rewards if r.status == RewardStatus.EARNED])
        redeem_points = random.randint(1, min(reward.points_earned, 200))
        
        reward.points_redeemed = redeem_points
        reward.redeemed_date = now - timedelta(days=random.randint(1, 15))
        
        if reward.points_redeemed >= reward.points_earned:
            reward.status = RewardStatus.REDEEMED
    
    db.session.commit()
    print("Redeemed some sample rewards")
    
    print("\nSample data created successfully!")
    print("\nSummary:")
    print(f"- Customers: {len(customers)}")
    print(f"- Merchants: {len(merchants)}")
    print(f"- Credit Cards: {len(credit_cards)}")
    print(f"- Offers: {len(offers)}")
    print(f"- Offer Activations: {len(customer_offers)}")
    print(f"- Payments: {len(payments)}")
    print(f"- Rewards: {len(rewards)}")
    
    print("\nSample API calls to test:")
    print("1. GET /api/customers - List all customers")
    print("2. GET /api/merchants - List all merchants")
    print("3. GET /api/customers/1 - Get customer details")
    print("4. GET /api/payments?customer_id=1 - Get customer payments")
    print("5. GET /api/offers - List all offers")
    print("6. GET /api/rewards/customer/1 - Get customer rewards")
    print("7. GET /api/merchants/1/history - Get merchant offer usage history")
    print("8. GET /api/profile-history/customer/1 - Get customer profile history")
    print("9. GET /api/merchants/1/analytics - Get merchant analytics")
    print("10. POST /api/payments - Make a payment (will auto-apply offers)")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Drop all tables and recreate
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating database tables...")
        db.create_all()
        
        create_sample_data()