"""
Database Migration Script
Recreates the database with new enhanced models for booking management system
"""
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from app.models import db

def migrate_database():
    """Create all tables with new enhanced models"""
    app = create_app()
    
    with app.app_context():
        try:
            # Import all models to ensure they're registered
            from app.models import (
                Customer, CreditCard, Merchant, Offer, CustomerOffer, Payment, Reward, 
                CustomerProfileHistory, CustomerCreditProfile, CreditCardProductDetails,
                Booking, Refund, TransactionDispute, RedemptionCancellation, OfferTerms,
                ProductTerms, PriceComparison
            )
            
            # Drop all existing tables
            print("Dropping existing tables...")
            db.drop_all()
            
            # Create all tables with new schema
            print("Creating tables with enhanced schema...")
            db.create_all()
            
            print("Database migration completed successfully!")
            print("New tables created:")
            print("- customer_credit_profile")
            print("- credit_card_product_details") 
            print("- booking")
            print("- refund")
            print("- transaction_dispute")
            print("- redemption_cancellation")
            print("- offer_terms")
            print("- product_terms")
            print("- price_comparison")
            
        except Exception as e:
            print(f"Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    return True

if __name__ == '__main__':
    migrate_database()