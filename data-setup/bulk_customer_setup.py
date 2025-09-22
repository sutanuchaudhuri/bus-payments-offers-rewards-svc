#!/usr/bin/env python3
"""
Bulk Customer Data Setup Script for Bus Payments & Rewards System
Creates 500 diverse customers with varied bonus structures, transaction patterns, and offer rewards
"""

import sys
import os
import random
import uuid
from datetime import datetime, timedelta, date
from decimal import Decimal
from faker import Faker
import json

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from app.models import *
from schema_setup import SchemaSetupManager

# Initialize Faker for generating realistic data
fake = Faker(['en_US', 'en_CA', 'es_MX', 'pt_BR', 'en_GB', 'fr_FR', 'de_DE', 'it_IT', 'es_ES'])

class BulkCustomerSetupManager:
    def __init__(self):
        self.app = create_app()
        self.customers = []
        self.all_merchants = []
        self.customer_cards = {}  # customer_id -> [cards]
        self.customer_transactions = {}  # customer_id -> [transactions]

        # Customer profile templates
        self.customer_profiles = [
            {
                "name": "Budget Conscious",
                "spending_range": (50, 300),
                "transaction_frequency": "low",  # 2-5 per month
                "preferred_categories": [MerchantCategory.GROCERY_STORE, MerchantCategory.GAS_STATION],
                "card_types": [CreditCardProduct.SILVER],
                "credit_limit_range": (2000, 5000)
            },
            {
                "name": "Regular Shopper",
                "spending_range": (100, 800),
                "transaction_frequency": "medium",  # 8-15 per month
                "preferred_categories": [MerchantCategory.RESTAURANT, MerchantCategory.GROCERY_STORE, MerchantCategory.RETAIL_STORE],
                "card_types": [CreditCardProduct.SILVER, CreditCardProduct.GOLD],
                "credit_limit_range": (5000, 12000)
            },
            {
                "name": "Business Traveler",
                "spending_range": (200, 2500),
                "transaction_frequency": "high",  # 15-25 per month
                "preferred_categories": [MerchantCategory.AIRLINE, MerchantCategory.HOTEL, MerchantCategory.RESTAURANT],
                "card_types": [CreditCardProduct.GOLD, CreditCardProduct.PLATINUM],
                "credit_limit_range": (10000, 25000)
            },
            {
                "name": "Luxury Spender",
                "spending_range": (500, 5000),
                "transaction_frequency": "high",  # 20-35 per month
                "preferred_categories": [MerchantCategory.AIRLINE, MerchantCategory.HOTEL, MerchantCategory.RETAIL_STORE],
                "card_types": [CreditCardProduct.PLATINUM],
                "credit_limit_range": (15000, 50000)
            },
            {
                "name": "Family Oriented",
                "spending_range": (150, 1200),
                "transaction_frequency": "medium",  # 10-20 per month
                "preferred_categories": [MerchantCategory.GROCERY_STORE, MerchantCategory.GAS_STATION, MerchantCategory.RESTAURANT],
                "card_types": [CreditCardProduct.SILVER, CreditCardProduct.GOLD],
                "credit_limit_range": (5000, 15000)
            },
            {
                "name": "Tech Professional",
                "spending_range": (200, 1500),
                "transaction_frequency": "medium",  # 12-18 per month
                "preferred_categories": [MerchantCategory.RETAIL_STORE, MerchantCategory.RESTAURANT, MerchantCategory.E_COMMERCE],
                "card_types": [CreditCardProduct.GOLD, CreditCardProduct.PLATINUM],
                "credit_limit_range": (8000, 20000)
            },
            {
                "name": "Young Professional",
                "spending_range": (80, 600),
                "transaction_frequency": "medium",  # 8-12 per month
                "preferred_categories": [MerchantCategory.RESTAURANT, MerchantCategory.ENTERTAINMENT_VENUE, MerchantCategory.RETAIL_STORE],
                "card_types": [CreditCardProduct.SILVER, CreditCardProduct.GOLD],
                "credit_limit_range": (3000, 10000)
            },
            {
                "name": "Insurance Buyer",
                "spending_range": (100, 800),
                "transaction_frequency": "low",  # 3-8 per month
                "preferred_categories": [MerchantCategory.INSURANCE_COMPANY, MerchantCategory.AUTOMOTIVE_SERVICE],
                "card_types": [CreditCardProduct.SILVER, CreditCardProduct.GOLD],
                "credit_limit_range": (4000, 12000)
            }
        ]

        # Bonus structures for different customer types
        self.bonus_structures = [
            {
                "name": "Welcome Bonus - 50K Points",
                "points": 50000,
                "conditions": "Spend $3,000 in first 3 months",
                "dollar_value": Decimal("500.00")
            },
            {
                "name": "Welcome Bonus - 75K Points",
                "points": 75000,
                "conditions": "Spend $5,000 in first 3 months",
                "dollar_value": Decimal("750.00")
            },
            {
                "name": "Welcome Bonus - 100K Points",
                "points": 100000,
                "conditions": "Spend $6,000 in first 3 months",
                "dollar_value": Decimal("1000.00")
            },
            {
                "name": "Cashback Bonus - $200",
                "points": 20000,
                "conditions": "Spend $1,000 in first 3 months",
                "dollar_value": Decimal("200.00")
            },
            {
                "name": "Travel Bonus - 60K Miles",
                "points": 60000,
                "conditions": "Spend $4,000 in first 3 months",
                "dollar_value": Decimal("720.00")
            }
        ]

    def setup_bulk_customers(self):
        """Main method to setup 500 customers with diverse profiles"""
        print("🚀 Starting bulk customer setup (500 customers)...")

        with self.app.app_context():
            # Ensure database schema exists
            print("\n🗄️  Ensuring database schema is ready...")
            self.ensure_schema()

            # Load existing merchants
            print("\n📍 Loading merchant data...")
            self.load_merchants()

            # Create 500 customers
            print("\n👥 Creating 500 diverse customers...")
            self.create_bulk_customers()

            # Create credit cards for customers
            print("\n💳 Creating credit cards for customers...")
            self.create_customer_credit_cards()

            # Create customer credit profiles
            print("\n📊 Creating customer credit profiles...")
            self.create_customer_credit_profiles()

            # Generate transactions for customers
            print("\n💰 Generating transactions (this may take a while)...")
            self.generate_customer_transactions()

            # Create customer-specific offers
            print("\n🎁 Creating personalized offers...")
            self.create_personalized_offers()

            # Generate rewards and bonuses
            print("\n⭐ Generating rewards and bonuses...")
            self.generate_customer_rewards()

            print("\n✅ Bulk customer setup completed successfully!")
            self.print_summary()

    def ensure_schema(self):
        """Ensure database schema exists by calling schema setup"""
        try:
            schema_manager = SchemaSetupManager()
            schema_manager.create_update_schema()
            print("✅ Database schema verified/created")
        except Exception as e:
            print(f"⚠️  Warning: Could not verify schema: {e}")

    def load_merchants(self):
        """Load existing merchants from database"""
        try:
            self.all_merchants = Merchant.query.all()
            if not self.all_merchants:
                print("⚠️  No merchants found! Please run merchant setup first.")
                return False
            print(f"✅ Loaded {len(self.all_merchants)} merchants")
            return True
        except Exception as e:
            print(f"❌ Error loading merchants: {e}")
            return False

    def create_bulk_customers(self):
        """Create 500 customers with diverse profiles"""
        countries = ['US', 'CA', 'MX', 'BR', 'GB', 'FR', 'DE', 'IT', 'ES', 'AU']

        for i in range(500):
            try:
                # Select random profile and country
                profile = random.choice(self.customer_profiles)
                country = random.choice(countries)

                # Set locale based on country
                if country == 'BR':
                    fake_locale = Faker('pt_BR')
                elif country == 'MX':
                    fake_locale = Faker('es_MX')
                elif country == 'FR':
                    fake_locale = Faker('fr_FR')
                elif country == 'DE':
                    fake_locale = Faker('de_DE')
                elif country == 'IT':
                    fake_locale = Faker('it_IT')
                elif country == 'ES':
                    fake_locale = Faker('es_ES')
                else:
                    fake_locale = fake

                # Generate customer data
                first_name = fake_locale.first_name()
                last_name = fake_locale.last_name()
                email = f"{first_name.lower()}.{last_name.lower()}@{fake_locale.domain_name()}"

                # Ensure unique email
                existing_customer = Customer.query.filter_by(email=email).first()
                if existing_customer:
                    email = f"{first_name.lower()}.{last_name.lower()}.{random.randint(100,999)}@{fake_locale.domain_name()}"

                customer = Customer(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=fake_locale.phone_number()[:20],  # Limit phone length
                    date_of_birth=fake_locale.date_of_birth(minimum_age=18, maximum_age=75),
                    address=fake_locale.address()[:500]  # Limit address length
                )

                db.session.add(customer)
                db.session.commit()

                # Store customer with profile info
                customer.profile_type = profile["name"]
                self.customers.append(customer)

                if (i + 1) % 50 == 0:
                    print(f"   Created {i + 1} customers...")

            except Exception as e:
                print(f"⚠️  Error creating customer {i + 1}: {e}")
                db.session.rollback()
                continue

        print(f"✅ Created {len(self.customers)} customers")

    def create_customer_credit_cards(self):
        """Create credit cards for each customer based on their profile"""
        card_issuers = ['Chase', 'Capital One', 'American Express', 'Citi', 'Bank of America', 'Wells Fargo']

        for customer in self.customers:
            try:
                # Get customer profile
                profile = next((p for p in self.customer_profiles if p["name"] == customer.profile_type), self.customer_profiles[0])

                # Number of cards (1-3 based on profile)
                num_cards = random.randint(1, min(3, len(profile["card_types"])))
                customer_cards = []

                for card_idx in range(num_cards):
                    # Select card type
                    card_type = random.choice(profile["card_types"])
                    card_brand = random.choice([CardType.VISA, CardType.MASTERCARD, CardType.AMERICAN_EXPRESS])

                    # Generate card number based on brand
                    if card_brand == CardType.VISA:
                        card_number = f"4{random.randint(100000000000000, 999999999999999)}"
                    elif card_brand == CardType.MASTERCARD:
                        card_number = f"5{random.randint(100000000000000, 999999999999999)}"
                    else:  # AMERICAN_EXPRESS
                        card_number = f"3{random.randint(10000000000000, 99999999999999)}"

                    # Ensure unique card number
                    while CreditCard.query.filter_by(card_number=card_number).first():
                        if card_brand == CardType.VISA:
                            card_number = f"4{random.randint(100000000000000, 999999999999999)}"
                        elif card_brand == CardType.MASTERCARD:
                            card_number = f"5{random.randint(100000000000000, 999999999999999)}"
                        else:
                            card_number = f"3{random.randint(10000000000000, 99999999999999)}"

                    # Credit limit based on profile
                    min_limit, max_limit = profile["credit_limit_range"]
                    credit_limit = Decimal(str(random.randint(min_limit, max_limit)))
                    available_credit = credit_limit * Decimal(str(random.uniform(0.7, 1.0)))  # 70-100% available

                    # Expiry date (1-5 years from now)
                    expiry_date = datetime.now() + timedelta(days=random.randint(365, 1825))

                    credit_card = CreditCard(
                        customer_id=customer.id,
                        card_number=card_number,
                        card_holder_name=f"{customer.first_name} {customer.last_name}",
                        expiry_month=expiry_date.month,
                        expiry_year=expiry_date.year,
                        product_type=card_type,
                        card_type=card_brand,
                        credit_limit=credit_limit,
                        available_credit=available_credit
                    )

                    db.session.add(credit_card)
                    customer_cards.append(credit_card)

                db.session.commit()
                self.customer_cards[customer.id] = customer_cards

            except Exception as e:
                print(f"⚠️  Error creating cards for customer {customer.id}: {e}")
                db.session.rollback()
                continue

        total_cards = sum(len(cards) for cards in self.customer_cards.values())
        print(f"✅ Created {total_cards} credit cards")

    def create_customer_credit_profiles(self):
        """Create credit profiles for customers"""
        for customer in self.customers:
            try:
                # Generate credit score based on customer profile
                profile = next((p for p in self.customer_profiles if p["name"] == customer.profile_type), self.customer_profiles[0])

                # Credit score ranges by profile
                if profile["name"] in ["Luxury Spender", "Business Traveler"]:
                    credit_score = random.randint(750, 850)  # Excellent
                elif profile["name"] in ["Tech Professional", "Regular Shopper"]:
                    credit_score = random.randint(700, 780)  # Good to Excellent
                elif profile["name"] in ["Young Professional", "Family Oriented"]:
                    credit_score = random.randint(650, 720)  # Fair to Good
                else:
                    credit_score = random.randint(580, 680)  # Fair

                # Determine credit rating
                if credit_score >= 800:
                    credit_rating = CreditRating.EXCELLENT
                elif credit_score >= 740:
                    credit_rating = CreditRating.VERY_GOOD
                elif credit_score >= 670:
                    credit_rating = CreditRating.GOOD
                elif credit_score >= 580:
                    credit_rating = CreditRating.FAIR
                else:
                    credit_rating = CreditRating.POOR

                # Generate other credit metrics
                annual_income = Decimal(str(random.randint(30000, 250000)))
                debt_to_income = Decimal(str(random.uniform(0.1, 0.4)))

                credit_profile = CustomerCreditProfile(
                    customer_id=customer.id,
                    credit_score=credit_score,
                    credit_rating=credit_rating,
                    category=CustomerCategory.PREMIUM if credit_score >= 750 else CustomerCategory.STANDARD,
                    annual_income=annual_income,
                    debt_to_income_ratio=debt_to_income,
                    years_of_credit_history=random.randint(1, 25),
                    number_of_credit_accounts=random.randint(2, 8),
                    recent_credit_inquiries=random.randint(0, 3),
                    payment_history_score=random.randint(credit_score - 50, credit_score + 20),
                    credit_utilization=Decimal(str(random.uniform(0.05, 0.35)))
                )

                db.session.add(credit_profile)

            except Exception as e:
                print(f"⚠️  Error creating credit profile for customer {customer.id}: {e}")
                continue

        db.session.commit()
        print(f"✅ Created credit profiles for {len(self.customers)} customers")

    def generate_customer_transactions(self):
        """Generate realistic transactions for each customer"""
        if not self.all_merchants:
            print("❌ No merchants available for transactions")
            return

        total_transactions = 0

        for customer in self.customers:
            try:
                customer_cards = self.customer_cards.get(customer.id, [])
                if not customer_cards:
                    continue

                # Get customer profile
                profile = next((p for p in self.customer_profiles if p["name"] == customer.profile_type), self.customer_profiles[0])

                # Determine transaction frequency
                if profile["transaction_frequency"] == "low":
                    monthly_transactions = random.randint(2, 5)
                elif profile["transaction_frequency"] == "medium":
                    monthly_transactions = random.randint(8, 18)
                else:  # high
                    monthly_transactions = random.randint(15, 35)

                # Generate transactions for last 12 months
                transactions = []
                for month in range(12):
                    month_start = datetime.now() - timedelta(days=30 * (month + 1))
                    month_end = datetime.now() - timedelta(days=30 * month)

                    for _ in range(monthly_transactions):
                        # Random transaction date within month
                        transaction_date = month_start + timedelta(
                            days=random.randint(0, 30),
                            hours=random.randint(6, 22),
                            minutes=random.randint(0, 59)
                        )

                        # Select merchant based on preferences
                        preferred_merchants = [m for m in self.all_merchants if m.category in profile["preferred_categories"]]
                        if not preferred_merchants:
                            preferred_merchants = self.all_merchants

                        merchant = random.choice(preferred_merchants)
                        credit_card = random.choice(customer_cards)

                        # Transaction amount based on profile and merchant category
                        min_amount, max_amount = profile["spending_range"]

                        # Adjust based on merchant category
                        if merchant.category == MerchantCategory.AIRLINE:
                            min_amount = max(min_amount, 150)
                            max_amount = min(max_amount * 3, 3000)
                        elif merchant.category == MerchantCategory.HOTEL:
                            min_amount = max(min_amount, 80)
                            max_amount = min(max_amount * 2, 1500)
                        elif merchant.category == MerchantCategory.GROCERY_STORE:
                            min_amount = max(min_amount, 20)
                            max_amount = min(max_amount, 300)
                        elif merchant.category == MerchantCategory.GAS_STATION:
                            min_amount = max(min_amount, 25)
                            max_amount = min(max_amount, 150)

                        amount = Decimal(str(round(random.uniform(min_amount, max_amount), 2)))

                        # Check credit limit
                        if amount > credit_card.available_credit:
                            amount = credit_card.available_credit * Decimal('0.9')

                        if amount <= 0:
                            continue

                        # Create payment
                        payment = Payment(
                            credit_card_id=credit_card.id,
                            amount=amount,
                            merchant_name=merchant.name,
                            merchant_category=merchant.category.value,
                            transaction_date=transaction_date,
                            status=PaymentStatus.COMPLETED,
                            reference_number=f"TXN-{transaction_date.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
                            description=f"Payment to {merchant.name}"
                        )

                        db.session.add(payment)
                        transactions.append(payment)

                        # Update available credit
                        credit_card.available_credit -= amount

                # Commit customer transactions in batch
                db.session.commit()
                self.customer_transactions[customer.id] = transactions
                total_transactions += len(transactions)

                if len(self.customer_transactions) % 25 == 0:
                    print(f"   Generated transactions for {len(self.customer_transactions)} customers...")

            except Exception as e:
                print(f"⚠️  Error generating transactions for customer {customer.id}: {e}")
                db.session.rollback()
                continue

        print(f"✅ Generated {total_transactions} transactions")

    def create_personalized_offers(self):
        """Create personalized offers based on customer spending patterns"""
        offer_templates = {
            MerchantCategory.AIRLINE: [
                ("5% Cashback on Flights", "Earn 5% cashback on all flight bookings", 5.0),
                ("Double Miles on International", "2x miles on international flights", 0.0),
                ("Free Baggage Bonus", "No baggage fees on flights", 0.0)
            ],
            MerchantCategory.HOTEL: [
                ("15% Off Hotel Stays", "Save 15% on hotel bookings", 15.0),
                ("Free Night After 5 Stays", "Get free night after 5 paid nights", 0.0),
                ("Late Checkout Perk", "Free late checkout until 2 PM", 0.0)
            ],
            MerchantCategory.RESTAURANT: [
                ("20% Off Dining", "Save 20% on restaurant purchases", 20.0),
                ("3x Points on Dining", "Earn triple points at restaurants", 0.0),
                ("Free Appetizer Deal", "Free appetizer with entree", 0.0)
            ],
            MerchantCategory.GROCERY_STORE: [
                ("5% Cashback Groceries", "5% back on grocery purchases", 5.0),
                ("Double Points Supermarket", "2x points at supermarkets", 0.0),
                ("$10 Off $50+ Purchase", "Save $10 on grocery orders $50+", 0.0)
            ],
            MerchantCategory.GAS_STATION: [
                ("3% Back on Gas", "3% cashback at gas stations", 3.0),
                ("5x Points on Fuel", "5x points on fuel purchases", 0.0),
                ("Free Car Wash", "Complimentary car wash with fill-up", 0.0)
            ]
        }

        total_offers = 0

        for customer in self.customers:
            try:
                # Get customer's transaction history
                customer_transactions = self.customer_transactions.get(customer.id, [])
                if not customer_transactions:
                    continue

                # Analyze spending patterns
                category_spending = {}
                for transaction in customer_transactions:
                    # Find merchant category
                    merchant = next((m for m in self.all_merchants if m.name == transaction.merchant_name), None)
                    if merchant:
                        category = merchant.category
                        category_spending[category] = category_spending.get(category, 0) + float(transaction.amount)

                # Create offers for top spending categories
                top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:3]

                for category, spending in top_categories:
                    if category in offer_templates:
                        template = random.choice(offer_templates[category])

                        # Find merchants in this category
                        category_merchants = [m for m in self.all_merchants if m.category == category]
                        if not category_merchants:
                            continue

                        merchant = random.choice(category_merchants)

                        start_date = datetime.now() - timedelta(days=random.randint(10, 60))
                        end_date = start_date + timedelta(days=random.randint(60, 120))

                        offer = Offer(
                            title=template[0],
                            description=template[1],
                            category=self.get_offer_category(category),
                            merchant_id=merchant.id,
                            discount_percentage=Decimal(str(template[2])) if template[2] > 0 else None,
                            max_discount_amount=Decimal(str(random.randint(25, 200))) if template[2] > 0 else None,
                            min_transaction_amount=Decimal(str(random.randint(25, 100))),
                            reward_points=random.randint(500, 2000) if template[2] == 0 else 0,
                            start_date=start_date,
                            expiry_date=end_date,
                            terms_and_conditions="Personalized offer based on spending history. Standard terms apply.",
                            max_usage_per_customer=random.randint(3, 10)
                        )

                        db.session.add(offer)

                        # Link offer to customer
                        customer_offer = CustomerOffer(
                            customer_id=customer.id,
                            offer_id=offer.id,
                            is_active=True
                        )
                        db.session.add(customer_offer)
                        total_offers += 1

            except Exception as e:
                print(f"⚠️  Error creating offers for customer {customer.id}: {e}")
                continue

        db.session.commit()
        print(f"✅ Created {total_offers} personalized offers")

    def get_offer_category(self, merchant_category):
        """Map merchant category to offer category"""
        mapping = {
            MerchantCategory.AIRLINE: OfferCategory.TRAVEL,
            MerchantCategory.RETAIL_STORE: OfferCategory.SHOPPING,
            MerchantCategory.ENTERTAINMENT_VENUE: OfferCategory.ENTERTAINMENT,
            MerchantCategory.GROCERY_STORE: OfferCategory.SHOPPING,
            MerchantCategory.GAS_STATION: OfferCategory.AUTOMOTIVE,
            MerchantCategory.RETAIL: OfferCategory.SHOPPING,
            MerchantCategory.ENTERTAINMENT: OfferCategory.ENTERTAINMENT,
            MerchantCategory.INSURANCE_COMPANY: OfferCategory.INSURANCE,
            MerchantCategory.AUTOMOTIVE_SERVICE: OfferCategory.AUTOMOTIVE
        }
        return mapping.get(merchant_category, OfferCategory.SHOPPING)

    def generate_customer_rewards(self):
        """Generate rewards and bonuses for customers"""
        total_rewards = 0
        total_bonuses = 0

        for customer in self.customers:
            try:
                customer_transactions = self.customer_transactions.get(customer.id, [])
                customer_cards = self.customer_cards.get(customer.id, [])

                if not customer_transactions or not customer_cards:
                    continue

                # Generate transaction-based rewards
                for transaction in customer_transactions:
                    # Find the card used
                    card = next((c for c in customer_cards if c.id == transaction.credit_card_id), None)
                    if not card:
                        continue

                    # Calculate points based on card type and merchant category
                    multiplier_map = {
                        CreditCardProduct.PLATINUM: 3.0,
                        CreditCardProduct.GOLD: 2.0,
                        CreditCardProduct.SILVER: 1.5
                    }

                    base_multiplier = multiplier_map.get(card.product_type, 1.0)

                    # Category bonuses
                    merchant = next((m for m in self.all_merchants if m.name == transaction.merchant_name), None)
                    if merchant:
                        if merchant.category in [MerchantCategory.AIRLINE, MerchantCategory.HOTEL]:
                            base_multiplier *= 2  # 2x for travel
                        elif merchant.category == MerchantCategory.RESTAURANT:
                            base_multiplier *= 1.5  # 1.5x for dining

                    points_earned = int(float(transaction.amount) * base_multiplier)

                    if points_earned > 0:
                        reward = Reward(
                            customer_id=customer.id,
                            payment_id=transaction.id,
                            points_earned=points_earned,
                            dollar_value=Decimal(str(points_earned * 0.01)),  # 1 point = 1 cent
                            status=RewardStatus.EARNED,
                            earned_date=transaction.transaction_date,
                            expiry_date=transaction.transaction_date + timedelta(days=365),
                            description=f"Points earned from {transaction.merchant_name}"
                        )
                        db.session.add(reward)
                        total_rewards += 1

                # Generate welcome bonus for some customers
                if random.random() < 0.6:  # 60% chance of welcome bonus
                    bonus_structure = random.choice(self.bonus_structures)

                    # Find first transaction date
                    if customer_transactions:
                        first_transaction = min(customer_transactions, key=lambda t: t.transaction_date)
                        bonus_date = first_transaction.transaction_date + timedelta(days=random.randint(30, 90))

                        bonus_reward = Reward(
                            customer_id=customer.id,
                            payment_id=None,
                            points_earned=bonus_structure["points"],
                            dollar_value=bonus_structure["dollar_value"],
                            status=RewardStatus.EARNED,
                            earned_date=bonus_date,
                            expiry_date=bonus_date + timedelta(days=730),  # 2 years
                            description=f"Welcome Bonus: {bonus_structure['name']} - {bonus_structure['conditions']}"
                        )
                        db.session.add(bonus_reward)
                        total_bonuses += 1

            except Exception as e:
                print(f"⚠️  Error generating rewards for customer {customer.id}: {e}")
                continue

        db.session.commit()
        print(f"✅ Generated {total_rewards} transaction rewards and {total_bonuses} welcome bonuses")

    def print_summary(self):
        """Print a summary of all created data"""
        print("\n" + "="*70)
        print("📊 BULK CUSTOMER SETUP SUMMARY")
        print("="*70)

        with self.app.app_context():
            customer_count = Customer.query.count()
            card_count = CreditCard.query.count()
            profile_count = CustomerCreditProfile.query.count()
            payment_count = Payment.query.count()
            reward_count = Reward.query.count()
            offer_count = Offer.query.count()
            customer_offer_count = CustomerOffer.query.count()

            print(f"👥 Total Customers: {customer_count}")
            print(f"💳 Total Credit Cards: {card_count}")
            print(f"📊 Credit Profiles: {profile_count}")
            print(f"💰 Total Transactions: {payment_count}")
            print(f"⭐ Total Rewards: {reward_count}")
            print(f"🎁 Total Offers: {offer_count}")
            print(f"🔗 Customer-Offer Links: {customer_offer_count}")

            print(f"\n📈 Customer Profile Distribution:")
            for profile in self.customer_profiles:
                profile_customers = [c for c in self.customers if c.profile_type == profile["name"]]
                print(f"   └─ {profile['name']}: {len(profile_customers)} customers")

            print(f"\n💳 Card Type Distribution:")
            for card_type in [CreditCardProduct.SILVER, CreditCardProduct.GOLD, CreditCardProduct.PLATINUM]:
                card_count = CreditCard.query.filter_by(product_type=card_type).count()
                print(f"   └─ {card_type.value}: {card_count} cards")

            print("="*70)

if __name__ == "__main__":
    bulk_manager = BulkCustomerSetupManager()
    bulk_manager.setup_bulk_customers()
