"""
Integration Routes for Simulator Services
Endpoints that query external simulator services for offer details
"""
from flask import Blueprint, request, jsonify
import requests
from datetime import datetime
import os
import sys

# Add simulator path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulator'))

integration_bp = Blueprint('integration', __name__)

# Simulator service URLs
SIMULATOR_SERVICES = {
    'travel': 'http://localhost:5002',
    'hotel': 'http://localhost:5003', 
    'shopping': 'http://localhost:5004'
}

def make_simulator_request(service, endpoint, method='GET', **kwargs):
    """Helper function to make requests to simulator services"""
    if service not in SIMULATOR_SERVICES:
        return {"error": f"Unknown simulator service: {service}"}, 400
    
    url = f"{SIMULATOR_SERVICES[service]}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, timeout=10, **kwargs)
        elif method.upper() == 'POST':
            response = requests.post(url, timeout=10, **kwargs)
        else:
            return {"error": f"Unsupported method: {method}"}, 400
        
        if response.status_code == 200:
            return response.json(), 200
        else:
            return {"error": f"Simulator service error: {response.status_code}"}, response.status_code
    
    except requests.exceptions.Timeout:
        return {"error": f"{service} service timeout"}, 504
    except requests.exceptions.ConnectionError:
        return {"error": f"{service} service unavailable"}, 503
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}, 500

@integration_bp.route('/simulator/status', methods=['GET'])
def check_simulator_status():
    """Check status of all simulator services"""
    status = {}
    
    for service_name, base_url in SIMULATOR_SERVICES.items():
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            status[service_name] = {
                "status": "healthy" if response.status_code == 200 else "error",
                "url": base_url,
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            status[service_name] = {
                "status": "unavailable",
                "url": base_url,
                "error": str(e)
            }
    
    return jsonify({
        "simulator_services": status,
        "timestamp": datetime.utcnow().isoformat()
    })

# TRAVEL INTEGRATION ENDPOINTS

@integration_bp.route('/offers/travel/airports', methods=['GET'])
def get_travel_airports():
    """Get available airports for travel offers"""
    result, status_code = make_simulator_request('travel', '/airports')
    return jsonify(result), status_code

@integration_bp.route('/offers/travel/search-flights', methods=['GET'])
def search_flights_for_offer():
    """Search flights for travel offers"""
    # Forward all query parameters
    params = request.args.to_dict()
    
    result, status_code = make_simulator_request(
        'travel', 
        '/search/flights',
        params=params
    )
    
    return jsonify(result), status_code

@integration_bp.route('/offers/travel/book-flight', methods=['POST'])
def book_flight_for_offer():
    """Book a flight through travel offer"""
    data = request.get_json()
    
    result, status_code = make_simulator_request(
        'travel',
        '/book/flight',
        method='POST',
        json=data
    )
    
    return jsonify(result), status_code

@integration_bp.route('/offers/travel/booking/<booking_reference>', methods=['GET'])
def get_travel_booking_details(booking_reference):
    """Get travel booking details"""
    result, status_code = make_simulator_request(
        'travel',
        f'/booking/{booking_reference}'
    )
    
    return jsonify(result), status_code

# HOTEL INTEGRATION ENDPOINTS

@integration_bp.route('/offers/hotel/cities', methods=['GET'])
def get_hotel_cities():
    """Get available cities for hotel offers"""
    result, status_code = make_simulator_request('hotel', '/cities')
    return jsonify(result), status_code

@integration_bp.route('/offers/hotel/search-hotels', methods=['GET'])
def search_hotels_for_offer():
    """Search hotels for accommodation offers"""
    params = request.args.to_dict()
    
    result, status_code = make_simulator_request(
        'hotel',
        '/search/hotels', 
        params=params
    )
    
    return jsonify(result), status_code

@integration_bp.route('/offers/hotel/book-hotel', methods=['POST'])
def book_hotel_for_offer():
    """Book a hotel through accommodation offer"""
    data = request.get_json()
    
    result, status_code = make_simulator_request(
        'hotel',
        '/book/hotel',
        method='POST',
        json=data
    )
    
    return jsonify(result), status_code

@integration_bp.route('/offers/hotel/booking/<booking_reference>', methods=['GET'])
def get_hotel_booking_details(booking_reference):
    """Get hotel booking details"""
    result, status_code = make_simulator_request(
        'hotel',
        f'/booking/{booking_reference}'
    )
    
    return jsonify(result), status_code

# SHOPPING INTEGRATION ENDPOINTS

@integration_bp.route('/offers/shopping/categories', methods=['GET'])
def get_shopping_categories():
    """Get product categories for shopping offers"""
    result, status_code = make_simulator_request('shopping', '/categories')
    return jsonify(result), status_code

@integration_bp.route('/offers/shopping/brands', methods=['GET'])
def get_shopping_brands():
    """Get product brands for shopping offers"""
    params = request.args.to_dict()
    
    result, status_code = make_simulator_request(
        'shopping',
        '/brands',
        params=params
    )
    
    return jsonify(result), status_code

@integration_bp.route('/offers/shopping/search', methods=['GET'])
def search_products_for_offer():
    """Search products for shopping offers"""
    params = request.args.to_dict()
    
    result, status_code = make_simulator_request(
        'shopping',
        '/products/search',
        params=params
    )
    
    return jsonify(result), status_code

@integration_bp.route('/offers/shopping/product/<product_id>', methods=['GET'])
def get_product_details_for_offer(product_id):
    """Get product details for shopping offers"""
    result, status_code = make_simulator_request(
        'shopping',
        f'/products/{product_id}'
    )
    
    return jsonify(result), status_code

@integration_bp.route('/offers/shopping/add-to-cart', methods=['POST'])
def add_to_cart_for_offer():
    """Add product to cart through shopping offer"""
    data = request.get_json()
    
    result, status_code = make_simulator_request(
        'shopping',
        '/cart/add',
        method='POST',
        json=data
    )
    
    return jsonify(result), status_code

@integration_bp.route('/offers/shopping/create-order', methods=['POST'])
def create_shopping_order():
    """Create order through shopping offer"""
    data = request.get_json()
    
    result, status_code = make_simulator_request(
        'shopping',
        '/order/create',
        method='POST',
        json=data
    )
    
    return jsonify(result), status_code

@integration_bp.route('/offers/shopping/order/<order_id>', methods=['GET'])
def get_shopping_order_status(order_id):
    """Get shopping order status"""
    result, status_code = make_simulator_request(
        'shopping',
        f'/order/{order_id}'
    )
    
    return jsonify(result), status_code

# COMBINED OFFER SEARCH ENDPOINTS

@integration_bp.route('/offers/search/travel-package', methods=['GET'])
def search_travel_package():
    """Search for combined flight + hotel packages"""
    origin = request.args.get('origin')
    destination = request.args.get('destination') 
    departure_date = request.args.get('departure_date')
    return_date = request.args.get('return_date')
    check_in = request.args.get('check_in', departure_date)
    check_out = request.args.get('check_out', return_date)
    passengers = request.args.get('passengers', 1)
    
    if not all([origin, destination, departure_date, return_date]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    # Search flights
    flight_params = {
        'origin': origin,
        'destination': destination, 
        'departure_date': departure_date,
        'return_date': return_date,
        'passengers': passengers
    }
    
    flights, flight_status = make_simulator_request('travel', '/search/flights', params=flight_params)
    
    # Search hotels (use destination city)
    city_map = {'NYC': 'new-york', 'LAX': 'los-angeles', 'MIA': 'miami', 'CHI': 'chicago'}
    hotel_city = city_map.get(destination, destination.lower())
    
    hotel_params = {
        'city': hotel_city,
        'check_in': check_in,
        'check_out': check_out,
        'guests': passengers,
        'rooms': 1
    }
    
    hotels, hotel_status = make_simulator_request('hotel', '/search/hotels', params=hotel_params)
    
    if flight_status == 200 and hotel_status == 200:
        # Combine and create packages
        packages = []
        if flights.get('flights') and hotels.get('hotels'):
            for flight in flights['flights'][:3]:  # Top 3 flights
                for hotel in hotels['hotels'][:3]:  # Top 3 hotels
                    package = {
                        "package_id": f"pkg_{flight['flight_id']}_{hotel['hotel_id']}",
                        "flight": flight,
                        "hotel": {
                            "hotel_id": hotel['hotel_id'],
                            "name": hotel['name'],
                            "star_rating": hotel['star_rating'],
                            "min_price": hotel['min_price'],
                            "rating": hotel['rating']
                        },
                        "total_price": flight['total_price'] + hotel['min_price'],
                        "savings": round((flight['total_price'] + hotel['min_price']) * 0.1, 2)  # 10% package discount
                    }
                    packages.append(package)
        
        # Sort by total price
        packages.sort(key=lambda x: x['total_price'])
        
        return jsonify({
            "travel_packages": packages[:6],  # Top 6 packages
            "search_criteria": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date,
                "passengers": passengers
            }
        })
    else:
        return jsonify({
            "error": "Unable to fetch travel package data",
            "flight_error": flights if flight_status != 200 else None,
            "hotel_error": hotels if hotel_status != 200 else None
        }), 500