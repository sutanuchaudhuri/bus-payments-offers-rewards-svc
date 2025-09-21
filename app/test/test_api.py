"""
Test API endpoints
"""
import unittest
import json
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from models import db

class TestAPIEndpoints(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and database"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.drop_all()
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
    
    def test_home_endpoint(self):
        """Test home endpoint"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Credit Card Payment System API')
    
    def test_customers_endpoint(self):
        """Test customers list endpoint"""
        response = self.client.get('/api/customers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('customers', data)
        self.assertIn('total', data)
    
    def test_merchants_endpoint(self):
        """Test merchants list endpoint"""
        response = self.client.get('/api/merchants')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('merchants', data)
    
    def test_offers_endpoint(self):
        """Test offers list endpoint"""
        response = self.client.get('/api/offers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('offers', data)

if __name__ == '__main__':
    unittest.main()