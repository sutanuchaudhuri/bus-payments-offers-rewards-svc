#!/usr/bin/env python3
"""
Customer-Specific Offers Setup Script for Bus Payments & Rewards System
Creates 200 customer-specific offer activations by linking customers to offer templates
"""

import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from app.models import *
from schema_setup import SchemaSetupManager

# Initialize Faker for generating realistic data
fake = Faker()

class CustomerOffersSetupManager:
    def __init__(self):
        self.app = create_app()
        self.customers = []
        self.offers = []
        self.customer_offers_created = []

        # Customer engagement patterns
        self.engagement_patterns = {
            "high_engagement": {
                "activation_probability": 0.8,
                "usage_frequency": "high",  # 3-8 uses per month
                "avg_savings_multiplier": 1.5
            },
            "medium_engagement": {
                "activation_probability": 0.6,
                "usage_frequency": "medium",  # 1-4 uses per month
                "avg_savings_multiplier": 1.0
            },
            "low_engagement": {
                "activation_probability": 0.3,
                "usage_frequency": "low",  # 0-2 uses per month
                "avg_savings_multiplier": 0.7
            }
        }

    def setup_customer_offers(self):
        """Main method to setup 200 customer-specific offers"""
        print("🚀 Starting customer-specific offers setup (200 activations)...")

        with self.app.app_context():
            # Ensure database schema exists
            print("\n🗄️  Ensuring database schema is ready...")
            self.ensure_schema()

            # Load existing customers and offers
            print("\n👥 Loading existing customers...")
            self.load_customers()

            print("\n🎁 Loading existing offer templates...")
            self.load_offers()

            # Validate we have enough data
            if not self.validate_data():
                return False

            # Create customer-specific offers
            print("\n💫 Creating 200 customer-specific offer activations...")
            self.create_customer_specific_offers()

            # Generate usage data for activated offers
            print("\n📊 Generating usage data for activated offers...")
            self.generate_usage_data()

            print("\n✅ Customer-specific offers setup completed successfully!")
            self.print_summary()

    def ensure_schema(self):
        """Ensure database schema exists by calling schema setup"""
        try:
            schema_manager = SchemaSetupManager()
            schema_manager.create_update_schema()
            print("✅ Database schema verified/created")
        except Exception as e:
            print(f"⚠️  Warning: Could not verify schema: {e}")

    def load_customers(self):
        """Load existing customers from database"""
        try:
            self.customers = Customer.query.all()
            if not self.customers:
                print("⚠️  No customers found! Please run customer setup first.")
                return False
            print(f"✅ Loaded {len(self.customers)} customers")
            return True
        except Exception as e:
            print(f"❌ Error loading customers: {e}")
            return False

    def load_offers(self):
        """Load existing offer templates from database"""
        try:
            self.offers = Offer.query.filter_by(is_active=True).all()
            if not self.offers:
                print("⚠️  No active offers found! Please create offer templates first.")
                return False
            print(f"✅ Loaded {len(self.offers)} active offer templates")
            return True
        except Exception as e:
            print(f"❌ Error loading offers: {e}")
            return False

    def validate_data(self):
        """Validate we have enough customers and offers for the setup"""
        if len(self.customers) < 10:
            print(f"❌ Not enough customers ({len(self.customers)}). Need at least 10 customers.")
            return False

        if len(self.offers) < 5:
            print(f"❌ Not enough offers ({len(self.offers)}). Need at least 5 offer templates.")
            return False

        print(f"✅ Data validation passed: {len(self.customers)} customers, {len(self.offers)} offers")
        return True

    def create_customer_specific_offers(self):
        """Create 200 customer-specific offer activations"""
        target_activations = 200
        activations_created = 0
        attempts = 0
        max_attempts = target_activations * 3  # Prevent infinite loops

        while activations_created < target_activations and attempts < max_attempts:
            attempts += 1

            try:
                # Randomly select customer and offer
                customer = random.choice(self.customers)
                offer = random.choice(self.offers)

                # Check if this customer-offer combination already exists
                existing_activation = CustomerOffer.query.filter_by(
                    customer_id=customer.id,
                    offer_id=offer.id
                ).first()

                if existing_activation:
                    continue  # Skip if already exists

                # Determine customer engagement pattern
                engagement_type = self.get_customer_engagement_pattern(customer)
                pattern = self.engagement_patterns[engagement_type]

                # Apply activation probability
                if random.random() > pattern["activation_probability"]:
                    continue

                # Check if offer is valid for activation
                current_time = datetime.utcnow()
                if current_time < offer.start_date or current_time > offer.expiry_date:
                    continue

                # Create activation date (within the last 90 days or offer start date)
                latest_start = max(
                    offer.start_date,
                    current_time - timedelta(days=90)
                )
                activation_date = fake.date_time_between(
                    start_date=latest_start,
                    end_date=current_time
                )

                # Generate initial usage data
                days_since_activation = (current_time - activation_date).days
                usage_count = self.calculate_initial_usage(
                    days_since_activation,
                    pattern["usage_frequency"]
                )

                # Calculate total savings based on usage
                total_savings = self.calculate_total_savings(
                    offer,
                    usage_count,
                    pattern["avg_savings_multiplier"]
                )

                # Create CustomerOffer record
                customer_offer = CustomerOffer(
                    customer_id=customer.id,
                    offer_id=offer.id,
                    activation_date=activation_date,
                    usage_count=usage_count,
                    total_savings=total_savings,
                    is_active=True
                )

                db.session.add(customer_offer)
                self.customer_offers_created.append(customer_offer)
                activations_created += 1

                if activations_created % 20 == 0:
                    print(f"   Created {activations_created} customer offer activations...")

            except Exception as e:
                print(f"⚠️  Error creating customer offer activation {activations_created + 1}: {e}")
                db.session.rollback()
                continue

        # Commit all activations
        try:
            db.session.commit()
            print(f"✅ Successfully created {activations_created} customer-specific offer activations")
        except Exception as e:
            print(f"❌ Error committing customer offers: {e}")
            db.session.rollback()

    def get_customer_engagement_pattern(self, customer):
        """Determine customer engagement pattern based on customer profile"""
        # Simple heuristic based on customer ID and some randomness
        customer_hash = hash(customer.email) % 100

        if customer_hash < 20:
            return "high_engagement"
        elif customer_hash < 60:
            return "medium_engagement"
        else:
            return "low_engagement"

    def calculate_initial_usage(self, days_since_activation, usage_frequency):
        """Calculate usage count based on days since activation and frequency pattern"""
        if days_since_activation <= 0:
            return 0

        # Convert days to approximate months
        months_active = max(1, days_since_activation / 30)

        usage_ranges = {
            "high": (3, 8),    # 3-8 uses per month
            "medium": (1, 4),  # 1-4 uses per month
            "low": (0, 2)      # 0-2 uses per month
        }

        min_uses, max_uses = usage_ranges[usage_frequency]
        monthly_usage = random.randint(min_uses, max_uses)

        # Calculate total usage with some randomness
        total_usage = int(monthly_usage * months_active * random.uniform(0.7, 1.3))
        return max(0, total_usage)

    def calculate_total_savings(self, offer, usage_count, savings_multiplier):
        """Calculate total savings based on offer details and usage"""
        if usage_count == 0:
            return Decimal('0.00')

        # Base savings per use
        base_savings_per_use = Decimal('0.00')

        if offer.discount_percentage and offer.discount_percentage > 0:
            # Assume average transaction of $50-150 for calculation
            avg_transaction = Decimal(str(random.uniform(50, 150)))
            percentage_savings = avg_transaction * (offer.discount_percentage / 100)

            # Apply max discount limit if specified
            if offer.max_discount_amount:
                percentage_savings = min(percentage_savings, offer.max_discount_amount)

            base_savings_per_use = percentage_savings

        elif offer.max_discount_amount:
            # Fixed discount amount
            base_savings_per_use = offer.max_discount_amount

        elif offer.reward_points and offer.reward_points > 0:
            # Convert points to dollar value (assuming 1 point = $0.01)
            base_savings_per_use = Decimal(str(offer.reward_points * 0.01))

        else:
            # Default small savings for offers without clear monetary benefit
            base_savings_per_use = Decimal(str(random.uniform(5, 25)))

        # Apply usage count and engagement multiplier
        total_savings = base_savings_per_use * usage_count * Decimal(str(savings_multiplier))

        # Add some variance
        variance = random.uniform(0.8, 1.2)
        final_savings = total_savings * Decimal(str(variance))

        return round(final_savings, 2)

    def generate_usage_data(self):
        """Generate additional usage patterns for some customer offers"""
        print("   Generating realistic usage patterns...")

        # Select 30% of created offers for additional usage updates
        offers_to_update = random.sample(
            self.customer_offers_created,
            min(len(self.customer_offers_created) // 3, 60)
        )

        for customer_offer in offers_to_update:
            try:
                # Simulate continued usage after initial creation
                current_time = datetime.utcnow()
                days_since_last_update = random.randint(1, 30)

                # Add some additional usage
                additional_usage = random.randint(0, 5)
                customer_offer.usage_count += additional_usage

                # Recalculate savings
                offer = Offer.query.get(customer_offer.offer_id)
                if offer:
                    engagement_type = self.get_customer_engagement_pattern(
                        Customer.query.get(customer_offer.customer_id)
                    )
                    pattern = self.engagement_patterns[engagement_type]

                    additional_savings = self.calculate_total_savings(
                        offer,
                        additional_usage,
                        pattern["avg_savings_multiplier"]
                    )
                    customer_offer.total_savings += additional_savings

            except Exception as e:
                print(f"⚠️  Error updating usage for customer offer: {e}")
                continue

        try:
            db.session.commit()
            print(f"✅ Updated usage patterns for {len(offers_to_update)} customer offers")
        except Exception as e:
            print(f"❌ Error updating usage patterns: {e}")
            db.session.rollback()

    def print_summary(self):
        """Print a summary of all created customer offers"""
        print("\n" + "="*70)
        print("📊 CUSTOMER-SPECIFIC OFFERS SETUP SUMMARY")
        print("="*70)

        with self.app.app_context():
            total_customer_offers = CustomerOffer.query.count()
            active_customer_offers = CustomerOffer.query.filter_by(is_active=True).count()
            total_customers_with_offers = db.session.query(CustomerOffer.customer_id).distinct().count()
            total_offers_activated = db.session.query(CustomerOffer.offer_id).distinct().count()

            # Calculate aggregate statistics
            total_savings = db.session.query(
                db.func.sum(CustomerOffer.total_savings)
            ).scalar() or 0

            total_usage = db.session.query(
                db.func.sum(CustomerOffer.usage_count)
            ).scalar() or 0

            avg_savings_per_activation = total_savings / max(total_customer_offers, 1)
            avg_usage_per_activation = total_usage / max(total_customer_offers, 1)

            print(f"🎯 Total Customer Offer Activations: {total_customer_offers}")
            print(f"✅ Active Customer Offer Activations: {active_customer_offers}")
            print(f"👥 Customers with Activated Offers: {total_customers_with_offers}")
            print(f"🎁 Unique Offers Activated: {total_offers_activated}")
            print(f"💰 Total Customer Savings: ${total_savings:,.2f}")
            print(f"📈 Total Offer Usage Count: {total_usage:,}")
            print(f"📊 Average Savings per Activation: ${avg_savings_per_activation:.2f}")
            print(f"🔄 Average Usage per Activation: {avg_usage_per_activation:.1f}")

            print(f"\n📈 Engagement Distribution:")
            # Sample some customer offers to show engagement patterns
            sample_offers = CustomerOffer.query.limit(100).all()
            engagement_counts = {"high_engagement": 0, "medium_engagement": 0, "low_engagement": 0}

            for co in sample_offers:
                customer = Customer.query.get(co.customer_id)
                if customer:
                    engagement = self.get_customer_engagement_pattern(customer)
                    engagement_counts[engagement] += 1

            total_sample = sum(engagement_counts.values())
            if total_sample > 0:
                for engagement, count in engagement_counts.items():
                    percentage = (count / total_sample) * 100
                    print(f"   └─ {engagement.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")

            print(f"\n🎁 Top Activated Offers:")
            # Show top 5 most activated offers
            top_offers = db.session.query(
                CustomerOffer.offer_id,
                db.func.count(CustomerOffer.id).label('activation_count'),
                db.func.sum(CustomerOffer.total_savings).label('total_savings')
            ).group_by(CustomerOffer.offer_id).order_by(
                db.func.count(CustomerOffer.id).desc()
            ).limit(5).all()

            for offer_id, activation_count, savings in top_offers:
                offer = Offer.query.get(offer_id)
                if offer:
                    print(f"   └─ {offer.title}: {activation_count} activations, ${savings or 0:.2f} total savings")

            print("="*70)

if __name__ == "__main__":
    customer_offers_manager = CustomerOffersSetupManager()
    customer_offers_manager.setup_customer_offers()
