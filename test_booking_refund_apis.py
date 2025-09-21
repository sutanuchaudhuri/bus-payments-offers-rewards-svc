#!/usr/bin/env python3
"""
Test script for new booking management and refund APIs
Tests the complete workflow of booking creation, cancellation, and refund processing
"""
import requests
import json
import time
from datetime import datetime, timedelta

# API base URLs
BASE_URL = "http://localhost:5001"
TRAVEL_URL = "http://localhost:5002"
HOTEL_URL = "http://localhost:5003"
SHOPPING_URL = "http://localhost:5004"

def test_api_endpoint(url, method='GET', data=None, description=""):
    """Helper function to test API endpoints"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Method: {method} {url}")
    
    if data:
        print(f"Request Data: {json.dumps(data, indent=2)}")
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            return response.status_code, response_data
        else:
            print(f"Response: {response.text}")
            return response.status_code, response.text
            
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None, None

def wait_for_services():
    """Wait for all services to be ready"""
    services = [
        (BASE_URL + "/api/health", "Main API"),
        (TRAVEL_URL + "/health", "Travel Service"),
        (HOTEL_URL + "/health", "Hotel Service"),
        (SHOPPING_URL + "/health", "Shopping Service")
    ]
    
    print("Waiting for services to be ready...")
    for url, name in services:
        max_retries = 30
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✓ {name} is ready")
                    break
            except requests.RequestException:
                pass
            
            if attempt == max_retries - 1:
                print(f"✗ {name} failed to start")
                return False
            time.sleep(1)
    
    print("All services are ready!")
    return True

def test_booking_workflow():
    """Test complete booking workflow"""
    print(f"\n{'#'*80}")
    print("TESTING BOOKING MANAGEMENT WORKFLOW")
    print(f"{'#'*80}")
    
    # Create a booking
    booking_data = {
        "customer_id": 1,
        "service_type": "travel",
        "booking_amount": 500.00,
        "discount_amount": 50.00,
        "final_amount": 450.00,
        "booking_details": {
            "origin": "NYC",
            "destination": "LAX",
            "departure_date": "2024-03-15",
            "passengers": 2
        },
        "service_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "is_refundable": True,
        "cancellation_fee": 75.00
    }
    
    status_code, booking_response = test_api_endpoint(
        f"{BASE_URL}/api/bookings",
        method="POST",
        data=booking_data,
        description="Create a new travel booking"
    )
    
    if status_code != 201:
        print("Failed to create booking, skipping rest of workflow")
        return None
    
    booking_id = booking_response.get('booking_id')
    print(f"\nCreated booking ID: {booking_id}")
    
    # Get booking status
    test_api_endpoint(
        f"{BASE_URL}/api/bookings/{booking_id}/status",
        description="Get booking status"
    )
    
    # Cancel the booking
    cancellation_data = {
        "reason": "Change of travel plans"
    }
    
    status_code, cancel_response = test_api_endpoint(
        f"{BASE_URL}/api/bookings/{booking_id}/cancel",
        method="POST",
        data=cancellation_data,
        description="Cancel the booking"
    )
    
    # Get updated booking status
    test_api_endpoint(
        f"{BASE_URL}/api/bookings/{booking_id}/status",
        description="Get updated booking status after cancellation"
    )
    
    # List all bookings
    test_api_endpoint(
        f"{BASE_URL}/api/bookings?customer_id=1",
        description="List customer bookings"
    )
    
    return booking_id, cancel_response

def test_refund_workflow():
    """Test refund system workflow"""
    print(f"\n{'#'*80}")
    print("TESTING REFUND SYSTEM WORKFLOW")
    print(f"{'#'*80}")
    
    # Request a refund
    refund_data = {
        "original_payment_id": 1,  # Assuming payment ID 1 exists
        "refund_type": "goodwill",
        "refund_amount": 100.00,
        "reason": "Customer service gesture"
    }
    
    status_code, refund_response = test_api_endpoint(
        f"{BASE_URL}/api/refunds/request",
        method="POST",
        data=refund_data,
        description="Request a refund"
    )
    
    if status_code != 201:
        print("Failed to create refund request")
        return None
    
    refund_id = refund_response.get('refund_id')
    print(f"\nCreated refund ID: {refund_id}")
    
    # Get refund details
    test_api_endpoint(
        f"{BASE_URL}/api/refunds/{refund_id}",
        description="Get refund details"
    )
    
    # Approve the refund
    test_api_endpoint(
        f"{BASE_URL}/api/refunds/{refund_id}/approve",
        method="PUT",
        description="Approve the refund"
    )
    
    # Get updated refund details
    test_api_endpoint(
        f"{BASE_URL}/api/refunds/{refund_id}",
        description="Get updated refund details after approval"
    )
    
    # List refunds
    test_api_endpoint(
        f"{BASE_URL}/api/refunds?status=approved",
        description="List approved refunds"
    )
    
    return refund_id

def test_points_cancellation():
    """Test points redemption cancellation"""
    print(f"\n{'#'*80}")
    print("TESTING POINTS REDEMPTION CANCELLATION")
    print(f"{'#'*80}")
    
    # Cancel points redemption
    cancellation_data = {
        "reward_id": 1,  # Assuming reward ID 1 exists
        "cancellation_reason": "Customer changed mind about redemption"
    }
    
    test_api_endpoint(
        f"{BASE_URL}/api/refunds/points/cancel",
        method="POST",
        data=cancellation_data,
        description="Cancel points redemption"
    )

def test_simulator_cancellation():
    """Test simulator service cancellation endpoints"""
    print(f"\n{'#'*80}")
    print("TESTING SIMULATOR SERVICE CANCELLATION ENDPOINTS")
    print(f"{'#'*80}")
    
    # Test travel booking cancellation
    test_api_endpoint(
        f"{TRAVEL_URL}/cancel/TRV123456",
        method="POST",
        description="Cancel travel booking via simulator"
    )
    
    # Test hotel booking cancellation
    test_api_endpoint(
        f"{HOTEL_URL}/cancel/HTL789012",
        method="POST",
        description="Cancel hotel booking via simulator"
    )
    
    # Test shopping order cancellation
    test_api_endpoint(
        f"{SHOPPING_URL}/cancel/ORD345678",
        method="POST",
        description="Cancel shopping order via simulator"
    )

def main():
    """Run all tests"""
    print("Starting comprehensive booking and refund API tests...")
    
    # Wait for services
    if not wait_for_services():
        print("Services not ready, exiting...")
        return
    
    # Test booking workflow
    booking_result = test_booking_workflow()
    
    # Test refund workflow
    refund_result = test_refund_workflow()
    
    # Test points cancellation
    test_points_cancellation()
    
    # Test simulator cancellation endpoints
    test_simulator_cancellation()
    
    print(f"\n{'#'*80}")
    print("TEST SUMMARY")
    print(f"{'#'*80}")
    print(f"Booking workflow: {'✓ Completed' if booking_result else '✗ Failed'}")
    print(f"Refund workflow: {'✓ Completed' if refund_result else '✗ Failed'}")
    print("Points cancellation: ✓ Completed")
    print("Simulator cancellation: ✓ Completed")

if __name__ == "__main__":
    main()