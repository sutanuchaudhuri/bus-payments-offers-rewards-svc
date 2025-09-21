"""
Test configuration and fixtures
"""
import pytest
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from models import db, Customer, Merchant, CreditCard, Payment, Offer

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def sample_customer():
    """Create sample customer for testing"""
    customer = Customer(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        phone="+1-555-0123"
    )
    db.session.add(customer)
    db.session.commit()
    return customer

@pytest.fixture
def sample_merchant():
    """Create sample merchant for testing"""
    from models import MerchantCategory
    merchant = Merchant(
        merchant_id="TEST_MERCHANT_001",
        name="Test Merchant",
        description="A test merchant",
        category=MerchantCategory.RESTAURANT
    )
    db.session.add(merchant)
    db.session.commit()
    return merchant