#!/usr/bin/env python3
"""
Comprehensive Test Suite for Simulator Services Integration
Tests all simulator services and integration endpoints
"""
import requests
import json
import sys
from datetime import datetime, timedelta

# Service URLs
MAIN_APP = "http://localhost:5001"
TRAVEL_SERVICE = "http://localhost:5002"
HOTEL_SERVICE = "http://localhost:5003" 
SHOPPING_SERVICE = "http://localhost:5004"

class SimulatorTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test_endpoint(self, name, url, expected_keys=None, params=None):
        """Test a single endpoint"""
        try:
            print(f"🧪 Testing {name}...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check expected keys if provided
                if expected_keys:
                    missing_keys = [key for key in expected_keys if key not in data]
                    if missing_keys:
                        print(f"   ❌ Missing keys: {missing_keys}")
                        self.failed += 1
                        self.errors.append(f"{name}: Missing keys {missing_keys}")
                        return False
                
                print(f"   ✅ Success (Response: {len(json.dumps(data))} chars)")
                self.passed += 1
                return True
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                self.failed += 1
                self.errors.append(f"{name}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.failed += 1
            self.errors.append(f"{name}: {str(e)}")
            return False
    
    def test_travel_service(self):
        """Test Travel Booking Service"""
        print("\n🛫 TESTING TRAVEL BOOKING SERVICE")
        print("=" * 50)
        
        # Test health
        self.test_endpoint("Health Check", f"{TRAVEL_SERVICE}/health", ["status", "service"])
        
        # Test airports
        self.test_endpoint("Get Airports", f"{TRAVEL_SERVICE}/airports", ["airports"])
        
        # Test flight search
        params = {
            "origin": "NYC",
            "destination": "LAX", 
            "departure_date": "2025-10-15",
            "passengers": 2
        }
        self.test_endpoint("Search Flights", f"{TRAVEL_SERVICE}/search/flights", 
                         ["flights", "search_criteria"], params)
    
    def test_hotel_service(self):
        """Test Hotel Booking Service"""
        print("\n🏨 TESTING HOTEL BOOKING SERVICE")
        print("=" * 50)
        
        # Test health
        self.test_endpoint("Health Check", f"{HOTEL_SERVICE}/health", ["status", "service"])
        
        # Test cities
        self.test_endpoint("Get Cities", f"{HOTEL_SERVICE}/cities", ["cities"])
        
        # Test hotel search
        params = {
            "city": "new-york",
            "check_in": "2025-10-15",
            "check_out": "2025-10-17",
            "guests": 2
        }
        self.test_endpoint("Search Hotels", f"{HOTEL_SERVICE}/search/hotels",
                         ["hotels", "search_criteria"], params)
    
    def test_shopping_service(self):
        """Test Shopping Service"""
        print("\n🛒 TESTING SHOPPING SERVICE")
        print("=" * 50)
        
        # Test health
        self.test_endpoint("Health Check", f"{SHOPPING_SERVICE}/health", ["status", "service"])
        
        # Test categories
        self.test_endpoint("Get Categories", f"{SHOPPING_SERVICE}/categories", ["categories"])
        
        # Test brands
        self.test_endpoint("Get Brands", f"{SHOPPING_SERVICE}/brands", ["brands"])
        
        # Test product search
        params = {
            "category": "electronics",
            "q": "laptop",
            "limit": 5
        }
        self.test_endpoint("Search Products", f"{SHOPPING_SERVICE}/products/search",
                         ["products", "search_criteria"], params)
    
    def test_integration_endpoints(self):
        """Test Integration Endpoints in Main App"""
        print("\n🔗 TESTING INTEGRATION ENDPOINTS")
        print("=" * 50)
        
        # Test simulator status
        self.test_endpoint("Simulator Status", f"{MAIN_APP}/api/integration/simulator/status",
                         ["simulator_services"])
        
        # Test travel integration
        self.test_endpoint("Integration - Travel Airports", 
                         f"{MAIN_APP}/api/integration/offers/travel/airports", 
                         ["airports"])
        
        # Test hotel integration
        self.test_endpoint("Integration - Hotel Cities",
                         f"{MAIN_APP}/api/integration/offers/hotel/cities",
                         ["cities"])
        
        # Test shopping integration
        self.test_endpoint("Integration - Shopping Categories",
                         f"{MAIN_APP}/api/integration/offers/shopping/categories",
                         ["categories"])
        
        # Test travel flight search integration
        params = {
            "origin": "NYC",
            "destination": "MIA",
            "departure_date": "2025-11-01",
            "passengers": 1
        }
        self.test_endpoint("Integration - Search Flights",
                         f"{MAIN_APP}/api/integration/offers/travel/search-flights",
                         ["flights"], params)
        
        # Test shopping product search integration
        params = {
            "category": "fashion",
            "limit": 3
        }
        self.test_endpoint("Integration - Search Products",
                         f"{MAIN_APP}/api/integration/offers/shopping/search",
                         ["products"], params)
    
    def test_combined_endpoints(self):
        """Test Combined Functionality"""
        print("\n✈️🏨 TESTING COMBINED ENDPOINTS")
        print("=" * 50)
        
        # Test travel package search
        params = {
            "origin": "NYC",
            "destination": "MIA",
            "departure_date": "2025-11-15",
            "return_date": "2025-11-18",
            "passengers": 2
        }
        self.test_endpoint("Travel Package Search",
                         f"{MAIN_APP}/api/integration/offers/search/travel-package",
                         ["travel_packages"], params)
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 SIMULATOR SERVICES INTEGRATION TEST SUITE")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test individual services
        self.test_travel_service()
        self.test_hotel_service() 
        self.test_shopping_service()
        
        # Test integration endpoints (only if main app is running)
        try:
            requests.get(f"{MAIN_APP}/api/health", timeout=5)
            self.test_integration_endpoints()
            self.test_combined_endpoints()
        except:
            print(f"\n⚠️  Main app not running on {MAIN_APP}")
            print("   Skipping integration endpoint tests")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"🎯 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.errors:
            print(f"\n🐛 Errors:")
            for error in self.errors:
                print(f"   • {error}")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return self.failed == 0

def main():
    """Main test function"""
    tester = SimulatorTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 {tester.failed} tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()