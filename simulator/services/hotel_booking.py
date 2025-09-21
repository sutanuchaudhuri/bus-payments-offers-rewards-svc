"""
Hotel Booking Simulator Service
Simulates hotel booking APIs for travel and accommodation offers
"""
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from decimal import Decimal
import random
import uuid

app = Flask(__name__)

# Mock hotel data
HOTEL_CHAINS = [
    {"id": "marriott", "name": "Marriott International"},
    {"id": "hilton", "name": "Hilton Hotels & Resorts"},
    {"id": "hyatt", "name": "Hyatt Hotels Corporation"},
    {"id": "ihg", "name": "InterContinental Hotels Group"},
    {"id": "accor", "name": "Accor Hotels"},
    {"id": "wyndham", "name": "Wyndham Hotels & Resorts"},
]

CITIES = {
    "new-york": {
        "name": "New York",
        "state": "NY",
        "country": "USA",
        "hotels": [
            {"name": "Grand Central Hotel", "stars": 4, "base_price": 250},
            {"name": "Times Square Luxury", "stars": 5, "base_price": 400},
            {"name": "Manhattan Business Inn", "stars": 3, "base_price": 180},
            {"name": "Brooklyn Bridge Suites", "stars": 4, "base_price": 220},
            {"name": "Central Park View", "stars": 5, "base_price": 500},
        ]
    },
    "los-angeles": {
        "name": "Los Angeles",
        "state": "CA",
        "country": "USA",
        "hotels": [
            {"name": "Hollywood Star Hotel", "stars": 4, "base_price": 200},
            {"name": "Beverly Hills Luxury", "stars": 5, "base_price": 600},
            {"name": "Santa Monica Beach Resort", "stars": 4, "base_price": 280},
            {"name": "Downtown LA Business", "stars": 3, "base_price": 150},
            {"name": "Sunset Strip Boutique", "stars": 4, "base_price": 320},
        ]
    },
    "miami": {
        "name": "Miami",
        "state": "FL",
        "country": "USA",
        "hotels": [
            {"name": "South Beach Resort", "stars": 5, "base_price": 350},
            {"name": "Miami Beach Hotel", "stars": 4, "base_price": 200},
            {"name": "Downtown Miami Suites", "stars": 3, "base_price": 120},
            {"name": "Ocean Drive Luxury", "stars": 5, "base_price": 450},
            {"name": "Coral Gables Inn", "stars": 3, "base_price": 140},
        ]
    },
    "chicago": {
        "name": "Chicago",
        "state": "IL",
        "country": "USA",
        "hotels": [
            {"name": "Magnificent Mile Hotel", "stars": 4, "base_price": 180},
            {"name": "River North Luxury", "stars": 5, "base_price": 380},
            {"name": "Loop Business Center", "stars": 3, "base_price": 130},
            {"name": "Navy Pier Suites", "stars": 4, "base_price": 210},
            {"name": "Millennium Park View", "stars": 4, "base_price": 250},
        ]
    }
}

ROOM_TYPES = [
    {"type": "standard", "name": "Standard Room", "multiplier": 1.0, "occupancy": 2},
    {"type": "deluxe", "name": "Deluxe Room", "multiplier": 1.3, "occupancy": 2},
    {"type": "suite", "name": "Suite", "multiplier": 1.8, "occupancy": 4},
    {"type": "executive", "name": "Executive Room", "multiplier": 1.5, "occupancy": 2},
    {"type": "family", "name": "Family Room", "multiplier": 1.6, "occupancy": 4},
]

AMENITIES = [
    "Free WiFi", "Pool", "Gym", "Spa", "Restaurant", "Room Service", 
    "Business Center", "Concierge", "Valet Parking", "Pet Friendly",
    "Airport Shuttle", "Breakfast Included"
]

def generate_hotel_price(base_price, room_type, check_in_date, check_out_date):
    """Generate realistic hotel pricing"""
    nights = (check_out_date - check_in_date).days
    room_multiplier = next(rt['multiplier'] for rt in ROOM_TYPES if rt['type'] == room_type)
    
    # Seasonal pricing
    month = check_in_date.month
    if month in [12, 1, 6, 7, 8]:  # Peak seasons
        seasonal_multiplier = 1.4
    elif month in [3, 4, 5, 9, 10]:  # Shoulder seasons
        seasonal_multiplier = 1.1
    else:  # Off season
        seasonal_multiplier = 0.9
    
    # Weekend pricing
    is_weekend = check_in_date.weekday() >= 5
    weekend_multiplier = 1.2 if is_weekend else 1.0
    
    # Advance booking discount
    days_ahead = (check_in_date - datetime.now().date()).days
    if days_ahead > 30:
        advance_multiplier = 0.9
    elif days_ahead < 7:
        advance_multiplier = 1.3
    else:
        advance_multiplier = 1.0
    
    nightly_rate = base_price * room_multiplier * seasonal_multiplier * weekend_multiplier * advance_multiplier
    total_price = nightly_rate * nights
    
    return round(nightly_rate, 2), round(total_price, 2)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "hotel-booking-simulator",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/cities', methods=['GET'])
def get_cities():
    """Get list of available cities"""
    return jsonify({
        "cities": [
            {"city_code": code, **details}
            for code, details in CITIES.items()
        ]
    })

@app.route('/search/hotels', methods=['GET'])
def search_hotels():
    """Search for hotels based on criteria"""
    city = request.args.get('city', '').lower().replace(' ', '-')
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    guests = int(request.args.get('guests', 2))
    rooms = int(request.args.get('rooms', 1))
    
    # Validation
    if not city or not check_in or not check_out:
        return jsonify({"error": "City, check_in, and check_out dates are required"}), 400
    
    if city not in CITIES:
        return jsonify({"error": "City not available"}), 400
    
    try:
        check_in_dt = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_dt = datetime.strptime(check_out, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    if check_in_dt >= check_out_dt:
        return jsonify({"error": "Check-out date must be after check-in date"}), 400
    
    # Generate hotel options
    city_data = CITIES[city]
    hotels = []
    
    for hotel_data in city_data['hotels']:
        chain = random.choice(HOTEL_CHAINS)
        hotel_amenities = random.sample(AMENITIES, random.randint(4, 8))
        
        # Generate room options for this hotel
        available_rooms = []
        for room_type_data in random.sample(ROOM_TYPES, random.randint(2, 4)):
            if room_type_data['occupancy'] >= guests:
                nightly_rate, total_price = generate_hotel_price(
                    hotel_data['base_price'], 
                    room_type_data['type'], 
                    check_in_dt, 
                    check_out_dt
                )
                
                available_rooms.append({
                    "room_id": str(uuid.uuid4()),
                    "room_type": room_type_data['type'],
                    "room_name": room_type_data['name'],
                    "occupancy": room_type_data['occupancy'],
                    "nightly_rate": nightly_rate,
                    "total_price": total_price * rooms,
                    "rooms_available": random.randint(1, 10),
                    "bed_type": random.choice(["King", "Queen", "Twin", "Double"]),
                    "size_sqft": random.randint(200, 800)
                })
        
        if available_rooms:  # Only include hotels with available rooms
            hotel = {
                "hotel_id": str(uuid.uuid4()),
                "name": hotel_data['name'],
                "chain": chain,
                "star_rating": hotel_data['stars'],
                "location": {
                    "city": city_data['name'],
                    "state": city_data['state'],
                    "country": city_data['country'],
                    "address": f"{random.randint(100, 9999)} {random.choice(['Main St', 'Park Ave', 'Broadway', 'Ocean Dr', 'Sunset Blvd'])}"
                },
                "amenities": hotel_amenities,
                "rating": round(random.uniform(3.5, 4.8), 1),
                "review_count": random.randint(50, 2000),
                "available_rooms": available_rooms,
                "distance_to_center": round(random.uniform(0.5, 15.0), 1),
                "check_in_time": "3:00 PM",
                "check_out_time": "11:00 AM"
            }
            hotels.append(hotel)
    
    # Sort by lowest price
    for hotel in hotels:
        hotel['min_price'] = min(room['total_price'] for room in hotel['available_rooms'])
    
    hotels.sort(key=lambda x: x['min_price'])
    
    return jsonify({
        "search_criteria": {
            "city": city,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "rooms": rooms,
            "nights": (check_out_dt - check_in_dt).days
        },
        "hotels": hotels,
        "count": len(hotels)
    })

@app.route('/book/hotel', methods=['POST'])
def book_hotel():
    """Book a hotel room (simulation)"""
    data = request.get_json()
    
    required_fields = ['hotel_id', 'room_id', 'guest_details', 'payment_method']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Simulate booking process
    booking_reference = f"HB{random.randint(100000, 999999)}"
    
    return jsonify({
        "booking_reference": booking_reference,
        "status": "confirmed",
        "hotel_booking": {
            "hotel_id": data['hotel_id'],
            "room_id": data['room_id'],
            "booking_time": datetime.utcnow().isoformat(),
            "guest_details": data['guest_details'],
            "check_in": data.get('check_in'),
            "check_out": data.get('check_out')
        },
        "total_amount": data.get('total_price', 0),
        "payment_status": "processed",
        "confirmation_email_sent": True,
        "cancellation_policy": "Free cancellation until 24 hours before check-in"
    })

@app.route('/booking/<booking_reference>', methods=['GET'])
def get_booking_details(booking_reference):
    """Get hotel booking details by reference"""
    return jsonify({
        "booking_reference": booking_reference,
        "status": "confirmed",
        "guest_count": random.randint(1, 4),
        "total_amount": random.randint(150, 1500),
        "booking_date": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
        "check_in": (datetime.utcnow() + timedelta(days=random.randint(1, 90))).date().isoformat(),
        "check_out": (datetime.utcnow() + timedelta(days=random.randint(2, 95))).date().isoformat(),
        "nights": random.randint(1, 7)
    })

@app.route('/cancel/<booking_id>', methods=['POST'])
def cancel_hotel_booking(booking_id):
    """Cancel a hotel booking"""
    try:
        # Simulate cancellation processing
        success_rate = 0.85  # 85% success rate for simulation
        
        if random.random() < success_rate:
            # Check time until check-in for fee calculation
            days_until_checkin = random.randint(1, 30)
            
            if days_until_checkin >= 7:
                cancellation_fee = 0  # Free cancellation
            elif days_until_checkin >= 2:
                cancellation_fee = random.randint(25, 75)  # Moderate fee
            else:
                cancellation_fee = random.randint(100, 200)  # High fee
            
            original_amount = random.randint(150, 1200)
            refund_amount = max(0, original_amount - cancellation_fee)
            
            return jsonify({
                "success": True,
                "booking_id": booking_id,
                "status": "cancelled",
                "original_amount": original_amount,
                "cancellation_fee": cancellation_fee,
                "refund_amount": refund_amount,
                "processing_time": "2-4 business days",
                "message": "Hotel booking cancelled successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "booking_id": booking_id,
                "error": "Cancellation not allowed - within 24-hour window",
                "message": "No-show fee will apply. Please contact hotel directly."
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Cancellation processing failed",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003, host='0.0.0.0')