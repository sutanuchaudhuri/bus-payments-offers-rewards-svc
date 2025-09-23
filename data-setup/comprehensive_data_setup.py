#!/usr/bin/env python3
"""
Comprehensive Data Setup Script for Bus Payments & Rewards System
Creates realistic sample data including customers, cards, merchants, offers, and transactions
NOTE: Run schema_setup.py first to create the database schema
"""

import sys
import os
import random
import uuid
from datetime import datetime, timedelta, date
from decimal import Decimal
from faker import Faker

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from app.models import *
from schema_setup import SchemaSetupManager

# Initialize Faker for generating realistic data
fake = Faker(['en_US', 'es_ES', 'pt_BR'])  # English, Spanish, Portuguese for Americas

class DataSetupManager:
    def __init__(self):
        self.app = create_app()
        self.customer_id = None
        self.credit_cards = []
        self.merchants = {
            'airlines': [],
            'hotels': [],
            'restaurants': [],
            'insurance': [],
            'cab_rental': []
        }
        self.offers = []

    def setup_all_data(self):
        """Main method to setup all data"""
        print("🚀 Starting comprehensive data setup...")

        with self.app.app_context():
            # Ensure database schema exists
            print("\n🗄️  Ensuring database schema is ready...")
            self.ensure_schema()

            # Optional: Clean existing data (uncomment if you want fresh data)
            print("\n🧹 Cleaning existing data...")
            self.clean_database()

            # 1. Create customer C0001
            print("\n1️⃣ Creating customer C0001...")
            self.create_customer_c0001()

            # 2. Add three credit cards
            print("\n2️⃣ Adding three credit cards...")
            self.add_credit_cards()

            # 3. Tokenize the cards
            print("\n3️⃣ Tokenizing credit cards...")
            self.tokenize_cards()

            # 4. Add 6 airlines
            print("\n4️⃣ Adding 6 airlines...")
            self.add_airlines()

            # 5. Add 20 hotel companies
            print("\n5️⃣ Adding 20 hotel companies...")
            self.add_hotels()

            # 6. Add 500 restaurants
            print("\n6️⃣ Adding 500 restaurants...")
            self.add_restaurants()

            # 7. Add 10 insurance companies
            print("\n7️⃣ Adding 10 insurance companies...")
            self.add_insurance_companies()

            # 8. Add 10 cab rental companies
            print("\n8️⃣ Adding 10 cab rental companies...")
            self.add_cab_rental_companies()

            # 9. Create 50 offers
            print("\n9️⃣ Creating 50 offers...")
            self.create_offers()

            # 10. Create 3000 transactions
            print("\n🔟 Creating 3000 transactions...")
            self.create_transactions()

            print("\n✅ Data setup completed successfully!")
            self.print_summary()

    def ensure_schema(self):
        """Ensure database schema exists by calling schema setup"""
        try:
            schema_manager = SchemaSetupManager()
            schema_manager.create_update_schema()
            print("✅ Database schema verified/created")
        except Exception as e:
            print(f"⚠️  Warning: Could not verify schema: {e}")

    def clean_database(self):
        """Clean all existing data from database tables"""
        try:
            # Delete in reverse order of dependencies
            db.session.query(Reward).delete()
            db.session.query(Payment).delete()
            db.session.query(Offer).delete()
            db.session.query(CardToken).delete()
            db.session.query(CreditCard).delete()
            db.session.query(Merchant).delete()
            db.session.query(Customer).delete()

            db.session.commit()
            print("✅ Database cleaned successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean database: {e}")
            db.session.rollback()

    def create_customer_c0001(self):
        """Create customer C0001 - Sutanu Chaudhuri"""
        # Check if customer already exists
        existing_customer = Customer.query.filter_by(email="sutanu.chaudhuri@example.com").first()
        if existing_customer:
            self.customer_id = existing_customer.id
            print(f"✅ Customer already exists: {existing_customer.first_name} {existing_customer.last_name} (ID: {existing_customer.id})")
            return

        customer = Customer(
            first_name="Sutanu",
            last_name="Chaudhuri",
            email="sutanu.chaudhuri@example.com",
            phone="+1-484-555-0123",
            date_of_birth=date(1982, 10, 10),
            address="426 Elton Farm, Glen Mills, PA 19342"
        )

        db.session.add(customer)
        db.session.commit()

        self.customer_id = customer.id
        print(f"✅ Created customer: {customer.first_name} {customer.last_name} (ID: {customer.id})")

    def add_credit_cards(self):
        """Add three specific credit cards"""
        # Check if credit cards already exist for this customer
        existing_cards = CreditCard.query.filter_by(customer_id=self.customer_id).all()
        if existing_cards:
            self.credit_cards = existing_cards
            print(f"✅ Found {len(existing_cards)} existing credit cards for customer")
            for card in existing_cards:
                print(f"   - {card.product_type.value} - ****{card.card_number[-4:]}")
            return

        cards_data = [
            {
                "card_number": "4111111111111111",  # Chase Sapphire Visa
                "card_holder_name": "Sutanu Chaudhuri",
                "expiry_month": 12,
                "expiry_year": 2028,
                "product_type": CreditCardProduct.PLATINUM,
                "card_type": CardType.VISA,
                "credit_limit": Decimal("15000.00"),
                "available_credit": Decimal("15000.00")
            },
            {
                "card_number": "5555555555554444",  # IHG Rewards Mastercard
                "card_holder_name": "Sutanu Chaudhuri",
                "expiry_month": 8,
                "expiry_year": 2027,
                "product_type": CreditCardProduct.GOLD,
                "card_type": CardType.MASTERCARD,
                "credit_limit": Decimal("10000.00"),
                "available_credit": Decimal("10000.00")
            },
            {
                "card_number": "4000000000000002",  # Amazon Visa
                "card_holder_name": "Sutanu Chaudhuri",
                "expiry_month": 6,
                "expiry_year": 2029,
                "product_type": CreditCardProduct.SILVER,
                "card_type": CardType.VISA,
                "credit_limit": Decimal("8000.00"),
                "available_credit": Decimal("8000.00")
            }
        ]

        for card_data in cards_data:
            # Check if this specific card number already exists
            existing_card = CreditCard.query.filter_by(card_number=card_data["card_number"]).first()
            if existing_card:
                self.credit_cards.append(existing_card)
                print(f"✅ Card already exists: {card_data['product_type'].value} - ****{card_data['card_number'][-4:]}")
                continue

            credit_card = CreditCard(
                customer_id=self.customer_id,
                **card_data
            )
            db.session.add(credit_card)
            db.session.commit()
            self.credit_cards.append(credit_card)
            print(f"✅ Added {card_data['product_type'].value} - ****{card_data['card_number'][-4:]}")

    def tokenize_cards(self):
        """Create tokens for all credit cards"""
        for card in self.credit_cards:
            # Check if token already exists for this card
            existing_token = CardToken.query.filter_by(card_id=card.id).first()
            if existing_token:
                print(f"✅ Token already exists for card ****{card.card_number[-4:]} -> ****{existing_token.token_id[-4:]}")
                continue

            # Generate a format-preserving token (same length and format as original card)
            token_number = self.generate_token(card.card_number)

            token = CardToken(
                token_id=token_number,
                card_id=card.id,
                customer_id=self.customer_id,
                expires_at=datetime.now() + timedelta(days=365)
            )
            db.session.add(token)
            print(f"✅ Tokenized card ****{card.card_number[-4:]} -> ****{token_number[-4:]}")

        db.session.commit()

    def generate_token(self, card_number):
        """Generate a format-preserving token"""
        # Keep first 6 and last 4 digits, randomize middle digits
        first_six = card_number[:6]
        last_four = card_number[-4:]
        middle_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return first_six + middle_digits + last_four

    def add_airlines(self):
        """Add 6 different airlines as merchants"""
        airlines = [
            {
                "name": "American Airlines",
                "merchant_id": "AA001",
                "description": "Major American airline providing domestic and international flights",
                "website": "https://www.aa.com",
                "contact_email": "customer.service@aa.com",
                "address": "4333 Amon Carter Blvd, Fort Worth, TX 76155"
            },
            {
                "name": "Delta Air Lines",
                "merchant_id": "DL001",
                "description": "Leading global airline with extensive route network and premium services",
                "website": "https://www.delta.com",
                "contact_email": "feedback@delta.com",
                "address": "1030 Delta Blvd, Atlanta, GA 30354"
            },
            {
                "name": "United Airlines",
                "merchant_id": "UA001",
                "description": "Major American airline with global reach and Star Alliance membership",
                "website": "https://www.united.com",
                "contact_email": "customer.care@united.com",
                "address": "233 S Wacker Dr, Chicago, IL 60606"
            },
            {
                "name": "Southwest Airlines",
                "merchant_id": "WN001",
                "description": "Low-cost carrier known for friendly service and no bag fees",
                "website": "https://www.southwest.com",
                "contact_email": "customer.relations@southwest.com",
                "address": "2702 Love Field Dr, Dallas, TX 75235"
            },
            {
                "name": "JetBlue Airways",
                "merchant_id": "B6001",
                "description": "Low-cost airline providing quality service with modern amenities",
                "website": "https://www.jetblue.com",
                "contact_email": "customer.relations@jetblue.com",
                "address": "27-01 Queens Plaza N, Long Island City, NY 11101"
            },
            {
                "name": "Alaska Airlines",
                "merchant_id": "AS001",
                "description": "Major American airline serving the West Coast and Alaska",
                "website": "https://www.alaskaair.com",
                "contact_email": "customer.relations@alaskaair.com",
                "address": "19300 International Blvd, Seattle, WA 98188"
            }
        ]

        for airline_data in airlines:
            merchant = Merchant(
                category=MerchantCategory.AIRLINE,
                phone=fake.phone_number(),
                **airline_data
            )
            db.session.add(merchant)
            self.merchants['airlines'].append(merchant)

        db.session.commit()
        print(f"✅ Added {len(airlines)} airlines")

    def add_hotels(self):
        """Add 20 hotel companies as merchants"""
        # Check if hotels already exist
        existing_hotels = Merchant.query.filter_by(category=MerchantCategory.HOTEL).all()
        if existing_hotels:
            self.merchants['hotels'] = existing_hotels
            print(f"✅ Found {len(existing_hotels)} existing hotels")
            return

        hotels = [
            "Marriott International", "Hilton Worldwide", "InterContinental Hotels Group",
            "Wyndham Hotels & Resorts", "Choice Hotels", "Best Western Hotels & Resorts",
            "Hyatt Hotels Corporation", "Radisson Hotel Group", "Accor", "Extended Stay America",
            "La Quinta Inns & Suites", "Red Roof Inn", "Motel 6", "Super 8", "Days Inn",
            "Hampton Inn & Suites", "Embassy Suites", "Courtyard by Marriott", "Residence Inn",
            "Homewood Suites"
        ]

        for i, hotel_name in enumerate(hotels):
            merchant = Merchant(
                name=hotel_name,
                merchant_id=f"HTL{i+1:03d}",
                description=f"{hotel_name} - Premium hospitality services with comfortable accommodations and excellent amenities",
                category=MerchantCategory.HOTEL,
                website=f"https://www.{hotel_name.lower().replace(' ', '').replace('&', 'and')}.com",
                contact_email=f"reservations@{hotel_name.lower().replace(' ', '').replace('&', 'and')}.com",
                phone=fake.phone_number(),
                address=fake.address()
            )

            db.session.add(merchant)

            self.merchants['hotels'].append(merchant)

        db.session.commit()
        print(f"✅ Added {len(hotels)} hotel companies")

    def add_restaurants(self):
        """Add 500 restaurants as merchants"""
        existing_restaurants = Merchant.query.filter_by(category=MerchantCategory.RESTAURANT).all()
        if existing_restaurants:
            self.merchants['restaurants'] = existing_restaurants
            print(f"✅ Found {len(existing_restaurants)} existing restaurants")
            return

        # Define cuisines and regions
        cuisines = {
            "Italian": ["Pasta", "Pizza", "Risotto", "Gelato"],
            "French": ["Fine dining", "Bistro", "Patisserie", "Wine bar"],
            "Spanish": ["Tapas", "Paella", "Seafood", "Iberian cuisine"],
            "Mexican": ["Tacos", "Enchiladas", "Margaritas", "Authentic Mexican"],
            "American": ["Burgers", "BBQ", "Steakhouse", "Diner food"],
            "Brazilian": ["Churrasco", "Feijoada", "Açaí", "Grilled meats"],
            "Argentine": ["Steakhouse", "Empanadas", "Wine", "Asado"],
            "Asian Fusion": ["Sushi", "Ramen", "Thai", "Vietnamese"],
            "Mediterranean": ["Greek", "Turkish", "Middle Eastern", "Healthy options"],
            "German": ["Beer garden", "Sausages", "Schnitzel", "Traditional German"]
        }

        regions = {
            "North America": ["New York, NY", "Los Angeles, CA", "Chicago, IL", "Toronto, ON", "Vancouver, BC"],
            "Europe": ["Paris, France", "Rome, Italy", "Barcelona, Spain", "London, UK", "Berlin, Germany"],
            "South America": ["São Paulo, Brazil", "Buenos Aires, Argentina", "Rio de Janeiro, Brazil", "Lima, Peru", "Bogotá, Colombia"]
        }

        restaurant_count = 0
        for region, cities in regions.items():
            restaurants_per_region = 500 // 3  # Distribute evenly across regions

            for i in range(restaurants_per_region):
                cuisine_type = random.choice(list(cuisines.keys()))
                city = random.choice(cities)

                restaurant_name = self.generate_restaurant_name(cuisine_type)
                specialties = random.sample(cuisines[cuisine_type], 2)

                merchant = Merchant(
                    name=restaurant_name,
                    merchant_id=f"RST{restaurant_count+1:03d}",
                    description=f"{cuisine_type} cuisine restaurant specializing in {', '.join(specialties)}. Located in {city}.",
                    category=MerchantCategory.RESTAURANT,
                    website=f"https://www.{restaurant_name.lower().replace(' ', '').replace('&', 'and')}.com",
                    contact_email=f"info@{restaurant_name.lower().replace(' ', '').replace('&', 'and')}.com",
                    phone=fake.phone_number(),
                    address=f"{fake.street_address()}, {city}"
                )
                db.session.add(merchant)
                self.merchants['restaurants'].append(merchant)
                restaurant_count += 1

        db.session.commit()
        print(f"✅ Added {restaurant_count} restaurants across 3 continents")

    def generate_restaurant_name(self, cuisine_type):
        """Generate realistic restaurant names based on cuisine type"""
        prefixes = {
            "Italian": ["La", "Il", "Bella", "Casa", "Ristorante"],
            "French": ["Le", "La", "Chez", "Café", "Bistro"],
            "Spanish": ["El", "La", "Casa", "Tapas", "Restaurante"],
            "Mexican": ["El", "La", "Casa", "Cantina", "Taqueria"],
            "American": ["The", "Big", "Classic", "All-American", "Downtown"],
            "Brazilian": ["Casa", "Churrascaria", "Sabor", "Tropical", "Rio"],
            "Argentine": ["El", "La", "Parrilla", "Asado", "Buenos"],
            "Asian Fusion": ["Golden", "Dragon", "Lotus", "Zen", "Tokyo"],
            "Mediterranean": ["Olive", "Santorini", "Mediterranean", "Aegean", "Cyprus"],
            "German": ["Das", "Der", "Oktoberfest", "Bavaria", "Alpine"]
        }

        suffixes = {
            "Italian": ["Roma", "Milano", "Venezia", "Trattoria", "Osteria"],
            "French": ["Paris", "Provence", "Brasserie", "Maison", "Table"],
            "Spanish": ["Barcelona", "Madrid", "Flamenco", "Olé", "Sevilla"],
            "Mexican": ["Azteca", "Maya", "Fiesta", "Guadalajara", "Cancun"],
            "American": ["Grill", "Diner", "Kitchen", "House", "Tavern"],
            "Brazilian": ["Brasil", "Copacabana", "Ipanema", "Carnival", "Amazonia"],
            "Argentine": ["Tango", "Pampas", "Aires", "Gaucho", "Mendoza"],
            "Asian Fusion": ["Garden", "Palace", "House", "Kitchen", "Express"],
            "Mediterranean": ["Coast", "Garden", "Taverna", "Grill", "Kitchen"],
            "German": ["Haus", "Brau", "Keller", "Garten", "Hof"]
        }

        prefix = random.choice(prefixes.get(cuisine_type, ["The"]))
        suffix = random.choice(suffixes.get(cuisine_type, ["Restaurant"]))

        return f"{prefix} {suffix}"

    def add_insurance_companies(self):
        """Add 10 insurance companies mentioning what insurance they provide"""
        # Check if insurance companies already exist
        existing_insurance = Merchant.query.filter_by(category=MerchantCategory.INSURANCE_COMPANY).all()
        if existing_insurance:
            self.merchants['insurance'] = existing_insurance
            print(f"✅ Found {len(existing_insurance)} existing insurance companies")
            return

        insurance_companies = [
            {
                "name": "SafeTravel Insurance",
                "description": "Comprehensive travel insurance covering trip cancellation, medical emergencies, and baggage protection for international and domestic travel",
                "specialty": "Travel Insurance"
            },
            {
                "name": "GlobalCare Medical",
                "description": "International health insurance providing worldwide medical coverage, emergency evacuation, and prescription drug benefits",
                "specialty": "Health Insurance"
            },
            {
                "name": "AutoGuard Protection",
                "description": "Full-coverage auto insurance including collision, comprehensive, liability, and roadside assistance services",
                "specialty": "Auto Insurance"
            },
            {
                "name": "HomeShield Insurance",
                "description": "Comprehensive homeowners insurance covering property damage, personal liability, and additional living expenses",
                "specialty": "Home Insurance"
            },
            {
                "name": "LifeSecure Assurance",
                "description": "Life insurance policies including term life, whole life, and universal life with competitive rates and flexible coverage",
                "specialty": "Life Insurance"
            },
            {
                "name": "BusinessProtect Solutions",
                "description": "Commercial insurance for businesses including general liability, professional indemnity, and cyber security coverage",
                "specialty": "Business Insurance"
            },
            {
                "name": "PetCare Insurance Plus",
                "description": "Pet insurance covering veterinary bills, surgery costs, and wellness care for dogs, cats, and exotic pets",
                "specialty": "Pet Insurance"
            },
            {
                "name": "RentalGuard Coverage",
                "description": "Renters insurance protecting personal property, liability coverage, and temporary living expenses for tenants",
                "specialty": "Renters Insurance"
            },
            {
                "name": "DisabilityShield Insurance",
                "description": "Disability insurance providing income protection for short-term and long-term disability situations",
                "specialty": "Disability Insurance"
            },
            {
                "name": "UmbrellaMax Protection",
                "description": "Umbrella insurance offering additional liability coverage beyond standard auto and home insurance limits",
                "specialty": "Umbrella Insurance"
            }
        ]

        for i, company_data in enumerate(insurance_companies):
            merchant = Merchant(
                name=company_data["name"],
                merchant_id=f"INS{i+1:03d}",
                description=company_data["description"],
                category=MerchantCategory.INSURANCE_COMPANY,
                website=f"https://www.{company_data['name'].lower().replace(' ', '')}.com",
                contact_email=f"claims@{company_data['name'].lower().replace(' ', '')}.com",
                phone=fake.phone_number(),
                address=fake.address()
            )
            db.session.add(merchant)
            self.merchants['insurance'].append(merchant)

        db.session.commit()
        print(f"✅ Added {len(insurance_companies)} insurance companies")

    def add_cab_rental_companies(self):
        """Add 10 cab rental companies mentioning their operating geography"""
        # Check if cab rental companies already exist
        existing_cab_rentals = Merchant.query.filter_by(category=MerchantCategory.AUTOMOTIVE_SERVICE).all()
        if existing_cab_rentals:
            self.merchants['cab_rental'] = existing_cab_rentals
            print(f"✅ Found {len(existing_cab_rentals)} existing cab rental companies")
            return

        cab_companies = [
            {
                "name": "MetroRide Services",
                "description": "Urban transportation and car rental services operating in major metropolitan areas across the East Coast including NYC, Philadelphia, Boston, and Washington DC",
                "geography": "East Coast USA"
            },
            {
                "name": "WestCoast Mobility",
                "description": "Premium car rental and ride services covering California, Oregon, and Washington with luxury and economy vehicle options",
                "geography": "West Coast USA"
            },
            {
                "name": "Heartland Auto Rental",
                "description": "Reliable car rental services serving the Midwest including Chicago, Detroit, Milwaukee, and Minneapolis with competitive rates",
                "geography": "Midwest USA"
            },
            {
                "name": "SunBelt Car Services",
                "description": "Car rental and transportation services operating across Texas, Arizona, Nevada, and New Mexico with 24/7 availability",
                "geography": "Southwest USA"
            },
            {
                "name": "Atlantic Canada Rentals",
                "description": "Regional car rental company serving Nova Scotia, New Brunswick, Prince Edward Island, and Newfoundland with local expertise",
                "geography": "Atlantic Canada"
            },
            {
                "name": "European City Cars",
                "description": "Urban mobility solutions operating in major European cities including London, Paris, Berlin, Rome, and Barcelona",
                "geography": "Europe"
            },
            {
                "name": "South American Express",
                "description": "Car rental and transportation services covering major cities in Brazil, Argentina, Chile, and Colombia",
                "geography": "South America"
            },
            {
                "name": "Rocky Mountain Rentals",
                "description": "Specialized car rental for mountain and outdoor adventures serving Colorado, Utah, Wyoming, and Montana",
                "geography": "Rocky Mountains"
            },
            {
                "name": "Coastal Florida Rides",
                "description": "Beach and city transportation services operating throughout Florida from Miami to Jacksonville with resort partnerships",
                "geography": "Florida"
            },
            {
                "name": "Great Lakes Auto",
                "description": "Regional car rental company serving the Great Lakes region including Michigan, Wisconsin, Minnesota, and parts of Canada",
                "geography": "Great Lakes Region"
            }
        ]

        for i, company_data in enumerate(cab_companies):
            merchant = Merchant(
                name=company_data["name"],
                merchant_id=f"CAB{i+1:03d}",
                description=company_data["description"],
                category=MerchantCategory.AUTOMOTIVE_SERVICE,
                website=f"https://www.{company_data['name'].lower().replace(' ', '')}.com",
                contact_email=f"rentals@{company_data['name'].lower().replace(' ', '')}.com",
                phone=fake.phone_number(),
                address=fake.address()
            )
            db.session.add(merchant)
            self.merchants['cab_rental'].append(merchant)

        db.session.commit()
        print(f"✅ Added {len(cab_companies)} cab rental companies")

    def create_offers(self):
        """Create 50 offers from different merchant categories"""
        offer_templates = {
            'airline': [
                ("5% Cashback on Flight Bookings", "Get 5% cashback on all domestic and international flight bookings", 5.0),
                ("Double Miles for Business Class", "Earn double reward points when booking business class flights", 0.0),
                ("Free Baggage with Premium Cards", "No baggage fees when using premium credit cards", 0.0),
                ("10% Off International Flights", "Save 10% on international flight bookings over $500", 10.0),
            ],
            'hotel': [
                ("Free Night Stay Reward", "Get one free night for every 10 nights booked", 0.0),
                ("15% Off Weekend Getaways", "Save 15% on weekend hotel bookings", 15.0),
                ("Complimentary Room Upgrade", "Free room upgrade subject to availability", 0.0),
                ("Late Checkout Special", "Enjoy late checkout until 2 PM at no extra charge", 0.0),
            ],
            'restaurant': [
                ("20% Off Dinner for Two", "Save 20% when dining for two people", 20.0),
                ("Free Appetizer with Entree", "Complimentary appetizer with any entree purchase", 0.0),
                ("Triple Points on Dining", "Earn 3x reward points on all restaurant purchases", 0.0),
                ("Buy One Get One Free Dessert", "Free dessert with purchase of any dessert", 0.0),
            ],
            'insurance': [
                ("10% Off Travel Insurance", "Save 10% on comprehensive travel insurance policies", 10.0),
                ("Free Policy Review", "Complimentary insurance policy review and consultation", 0.0),
                ("Multi-Policy Discount", "Save 15% when bundling multiple insurance policies", 15.0),
                ("First Month Free", "No premium for the first month of new policies", 0.0),
            ],
            'cab_rental': [
                ("25% Off Weekend Rentals", "Save 25% on car rentals for weekend trips", 25.0),
                ("Free GPS Navigation", "Complimentary GPS device with any rental", 0.0),
                ("Extended Rental Discounts", "Save 20% on rentals of 7 days or more", 20.0),
                ("Loyalty Member Upgrade", "Free vehicle upgrade for loyalty program members", 0.0),
            ]
        }

        categories_map = {
            'airline': (OfferCategory.TRAVEL, self.merchants['airlines']),
            'hotel': (OfferCategory.TRAVEL, self.merchants['hotels']),
            'restaurant': (OfferCategory.DINING, self.merchants['restaurants']),
            'insurance': (OfferCategory.INSURANCE, self.merchants['insurance']),
            'cab_rental': (OfferCategory.TRAVEL, self.merchants['cab_rental'])
        }

        offers_created = 0
        target_offers = 50

        for category_name, (offer_category, merchant_list) in categories_map.items():
            if not merchant_list:
                continue

            offers_per_category = min(target_offers // len(categories_map), len(offer_templates[category_name]))

            for i in range(offers_per_category):
                if offers_created >= target_offers:
                    break

                template = offer_templates[category_name][i % len(offer_templates[category_name])]
                merchant = random.choice(merchant_list)

                start_date = datetime.now() - timedelta(days=random.randint(30, 90))
                end_date = start_date + timedelta(days=random.randint(60, 180))

                offer = Offer(
                    offer_id=f"OFFER_{offers_created+1:03d}",  # Add the required offer_id
                    title=template[0],
                    description=template[1],
                    category=offer_category,
                    merchant_id=merchant.id,
                    discount_percentage=Decimal(str(template[2])) if template[2] > 0 else None,
                    max_discount_amount=Decimal(str(random.randint(50, 500))) if template[2] > 0 else None,
                    min_transaction_amount=Decimal(str(random.randint(25, 200))),
                    reward_points=random.randint(100, 1000) if template[2] == 0 else 0,
                    start_date=start_date,
                    expiry_date=end_date,
                    terms_and_conditions="Standard terms and conditions apply. Cannot be combined with other offers.",
                    max_usage_per_customer=random.randint(1, 5)
                )

                db.session.add(offer)
                self.offers.append(offer)
                offers_created += 1

        # Fill remaining offers with random selections
        while offers_created < target_offers:
            category_name = random.choice(list(categories_map.keys()))
            offer_category, merchant_list = categories_map[category_name]

            if merchant_list:
                template = random.choice(offer_templates[category_name])
                merchant = random.choice(merchant_list)

                start_date = datetime.now() - timedelta(days=random.randint(30, 90))
                end_date = start_date + timedelta(days=random.randint(60, 180))

                offer = Offer(
                    title=template[0],
                    offer_id=f"OFFER_{offers_created+1:03d}",  # Add the required offer_id
                    description=template[1],
                    category=offer_category,
                    merchant_id=merchant.id,
                    discount_percentage=Decimal(str(template[2])) if template[2] > 0 else None,
                    max_discount_amount=Decimal(str(random.randint(50, 500))) if template[2] > 0 else None,
                    min_transaction_amount=Decimal(str(random.randint(25, 200))),
                    reward_points=random.randint(100, 1000) if template[2] == 0 else 0,
                    start_date=start_date,
                    expiry_date=end_date,
                    terms_and_conditions="Standard terms and conditions apply. Cannot be combined with other offers.",
                    max_usage_per_customer=random.randint(1, 5)
                )

                db.session.add(offer)
                self.offers.append(offer)
                offers_created += 1

        db.session.commit()
        print(f"✅ Created {offers_created} offers across all merchant categories")

    def create_transactions(self):
        """Create 3000 transactions made by the customer in the last two years"""
        if not self.credit_cards:
            print("❌ No credit cards found. Cannot create transactions.")
            return

        # Flatten all merchants into a single list
        all_merchants = []
        for merchant_list in self.merchants.values():
            all_merchants.extend(merchant_list)

        if not all_merchants:
            print("❌ No merchants found. Cannot create transactions.")
            return

        transactions_created = 0
        target_transactions = 3000

        # Date range: last 2 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)  # 2 years

        for i in range(target_transactions):
            # Random transaction date in the last 2 years
            transaction_date = start_date + timedelta(
                days=random.randint(0, 730),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            # Select random credit card and merchant
            credit_card = random.choice(self.credit_cards)
            merchant = random.choice(all_merchants)

            # Generate realistic transaction amounts based on merchant category
            amount_ranges = {
                MerchantCategory.RESTAURANT: (15, 250),
                MerchantCategory.AIRLINE: (150, 2500),
                MerchantCategory.HOTEL: (80, 800),
                MerchantCategory.INSURANCE_COMPANY: (50, 500),
                MerchantCategory.AUTOMOTIVE_SERVICE: (25, 400),
                MerchantCategory.GAS_STATION: (20, 80),
                MerchantCategory.GROCERY_STORE: (30, 200)
            }

            min_amount, max_amount = amount_ranges.get(merchant.category, (10, 100))
            amount = Decimal(str(round(random.uniform(min_amount, max_amount), 2)))

            # Check if card has sufficient credit
            if amount > credit_card.available_credit:
                amount = credit_card.available_credit * Decimal('0.9')  # Use 90% of available credit

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

            # Update credit card available credit
            credit_card.available_credit -= amount

            # Create reward points (simplified calculation)
            multiplier_map = {
                CreditCardProduct.PLATINUM: 3.0,  # Chase Sapphire equivalent
                CreditCardProduct.GOLD: 2.0,      # IHG Rewards equivalent
                CreditCardProduct.SILVER: 1.5     # Amazon Visa equivalent
            }

            multiplier = multiplier_map.get(credit_card.product_type, 1.0)
            points_earned = int(float(amount) * multiplier)

            if points_earned > 0:
                reward = Reward(
                    customer_id=self.customer_id,
                    payment_id=payment.id,
                    points_earned=points_earned,
                    dollar_value=Decimal(str(points_earned * 0.01)),  # 1 point = 1 cent
                    status=RewardStatus.EARNED,
                    earned_date=transaction_date,
                    expiry_date=transaction_date + timedelta(days=365),
                    description=f"Rewards earned from {merchant.name} purchase"
                )
                db.session.add(reward)

            transactions_created += 1

            # Commit in batches for better performance
            if transactions_created % 100 == 0:
                db.session.commit()
                print(f"💳 Created {transactions_created} transactions...")

        db.session.commit()
        print(f"✅ Created {transactions_created} transactions over the last 2 years")

    def print_summary(self):
        """Print a summary of all created data"""
        print("\n" + "="*60)
        print("📊 DATA SETUP SUMMARY")
        print("="*60)

        with self.app.app_context():
            customer_count = Customer.query.count()
            card_count = CreditCard.query.count()
            token_count = CardToken.query.count()
            merchant_count = Merchant.query.count()
            offer_count = Offer.query.count()
            payment_count = Payment.query.count()
            reward_count = Reward.query.count()

            print(f"👤 Customers: {customer_count}")
            print(f"💳 Credit Cards: {card_count}")
            print(f"🔒 Card Tokens: {token_count}")
            print(f"🏢 Merchants: {merchant_count}")
            print(f"   └─ Airlines: {len(self.merchants['airlines'])}")
            print(f"   └─ Hotels: {len(self.merchants['hotels'])}")
            print(f"   └─ Restaurants: {len(self.merchants['restaurants'])}")
            print(f"   └─ Insurance: {len(self.merchants['insurance'])}")
            print(f"   └─ Car Rentals: {len(self.merchants['cab_rental'])}")
            print(f"🎁 Offers: {offer_count}")
            print(f"💰 Transactions: {payment_count}")
            print(f"⭐ Rewards: {reward_count}")
            print("="*60)

if __name__ == "__main__":
    data_manager = DataSetupManager()
    data_manager.setup_all_data()
