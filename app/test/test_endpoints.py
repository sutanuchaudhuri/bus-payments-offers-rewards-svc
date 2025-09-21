#!/usr/bin/env python3
"""
Quick test script to verify API endpoints are working
"""
import requests
import json
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://localhost:5001/api"

def test_endpoint(method, endpoint, data=None):
    """Test an API endpoint and print the results"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{method} {endpoint}")
    print("-" * 50)
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        print(f"Status: {response.status_code}")
        
        if response.status_code < 400:
            result = response.json()
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def main():
    print("Testing Bus Payments Offers Rewards API")
    print("=" * 60)
    
    # Test health check
    test_endpoint("GET", "/health")
    
    # Test customers
    test_endpoint("GET", "/customers")
    
    # Test merchants
    test_endpoint("GET", "/merchants")
    
    # Test offers
    test_endpoint("GET", "/offers")
    
    # Test rewards for customer 1
    test_endpoint("GET", "/rewards/customer/1")
    
    # Test payment history for customer 1
    test_endpoint("GET", "/payments?customer_id=1")
    
    # Test customer profile history
    test_endpoint("GET", "/profile-history/customer/1")
    
    # Test merchant analytics
    test_endpoint("GET", "/merchants/1/analytics")
    
    print("\n" + "=" * 60)
    print("API testing completed!")
    print(f"Visit {BASE_URL.replace('/api', '')} to access the running application")

if __name__ == "__main__":
    main()