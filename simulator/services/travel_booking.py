"""
Travel Booking Simulator Service
Simulates flight booking APIs for travel offers
"""
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from decimal import Decimal
import random
import uuid

app = Flask(__name__)

# Mock flight data
AIRLINES = [
    {"code": "AA", "name": "American Airlines"},
    {"code": "UA", "name": "United Airlines"},
    {"code": "DL", "name": "Delta Airlines"},
    {"code": "SW", "name": "Southwest Airlines"},
    {"code": "JB", "name": "JetBlue Airways"},
]

AIRPORTS = {
    "NYC": {"city": "New York", "name": "John F. Kennedy International"},
    "LAX": {"city": "Los Angeles", "name": "Los Angeles International"},
    "CHI": {"city": "Chicago", "name": "O'Hare International"},
    "MIA": {"city": "Miami", "name": "Miami International"},
    "SFO": {"city": "San Francisco", "name": "San Francisco International"},
    "LAS": {"city": "Las Vegas", "name": "McCarran International"},
    "SEA": {"city": "Seattle", "name": "Seattle-Tacoma International"},
    "DEN": {"city": "Denver", "name": "Denver International"},
    "ATL": {"city": "Atlanta", "name": "Hartsfield-Jackson Atlanta International"},
    "BOS": {"city": "Boston", "name": "Logan International"},
}

def generate_flight_price(origin, destination, departure_date, return_date=None):
    """Generate realistic flight pricing"""
    base_price = random.randint(200, 800)
    
    # Distance factor
    distance_multiplier = random.uniform(1.0, 2.5)
    
    # Date factor (prices increase closer to departure)
    days_ahead = (departure_date - datetime.now().date()).days
    if days_ahead < 7:
        date_multiplier = 1.5
    elif days_ahead < 14:
        date_multiplier = 1.2
    else:
        date_multiplier = 1.0
    
    # Round trip discount
    trip_multiplier = 1.8 if return_date else 1.0
    
    final_price = base_price * distance_multiplier * date_multiplier * trip_multiplier
    return round(final_price, 2)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "travel-booking-simulator",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/airports', methods=['GET'])
def get_airports():
    """Get list of available airports"""
    return jsonify({
        "airports": [
            {"code": code, **details}
            for code, details in AIRPORTS.items()
        ]
    })

@app.route('/search/flights', methods=['GET'])
def search_flights():
    """Search for flights based on criteria"""
    origin = request.args.get('origin', '').upper()
    destination = request.args.get('destination', '').upper()
    departure_date = request.args.get('departure_date')
    return_date = request.args.get('return_date')
    passengers = int(request.args.get('passengers', 1))
    
    # Validation
    if not origin or not destination:
        return jsonify({"error": "Origin and destination are required"}), 400
    
    if origin not in AIRPORTS or destination not in AIRPORTS:
        return jsonify({"error": "Invalid airport code"}), 400
    
    try:
        departure_dt = datetime.strptime(departure_date, '%Y-%m-%d').date()
        return_dt = datetime.strptime(return_date, '%Y-%m-%d').date() if return_date else None
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Generate flight options
    flights = []
    for i in range(random.randint(3, 8)):
        airline = random.choice(AIRLINES)
        departure_time = f"{random.randint(6, 23):02d}:{random.choice(['00', '15', '30', '45'])}"
        duration_hours = random.randint(1, 8)
        duration_minutes = random.choice([0, 15, 30, 45])
        
        flight = {
            "flight_id": str(uuid.uuid4()),
            "airline": airline,
            "flight_number": f"{airline['code']}{random.randint(100, 9999)}",
            "origin": {
                "code": origin,
                **AIRPORTS[origin]
            },
            "destination": {
                "code": destination,
                **AIRPORTS[destination]
            },
            "departure": {
                "date": departure_date,
                "time": departure_time
            },
            "duration": f"{duration_hours}h {duration_minutes}m",
            "price_per_person": generate_flight_price(origin, destination, departure_dt, return_dt),
            "total_price": generate_flight_price(origin, destination, departure_dt, return_dt) * passengers,
            "seats_available": random.randint(5, 150),
            "cabin_class": "Economy"
        }
        flights.append(flight)
    
    # Sort by price
    flights.sort(key=lambda x: x['price_per_person'])
    
    return jsonify({
        "search_criteria": {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "passengers": passengers
        },
        "flights": flights,
        "count": len(flights)
    })

@app.route('/book/flight', methods=['POST'])
def book_flight():
    """Book a flight (simulation)"""
    data = request.get_json()
    
    required_fields = ['flight_id', 'passenger_details', 'payment_method']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Simulate booking process
    booking_reference = f"TB{random.randint(100000, 999999)}"
    
    return jsonify({
        "booking_reference": booking_reference,
        "status": "confirmed",
        "flight_details": {
            "flight_id": data['flight_id'],
            "booking_time": datetime.utcnow().isoformat(),
            "passengers": data['passenger_details']
        },
        "total_amount": data.get('total_price', 0),
        "payment_status": "processed",
        "confirmation_email_sent": True
    })

@app.route('/booking/<booking_reference>', methods=['GET'])
def get_booking_details(booking_reference):
    """Get booking details by reference"""
    # Simulate booking lookup
    return jsonify({
        "booking_reference": booking_reference,
        "status": "confirmed",
        "passenger_count": random.randint(1, 4),
        "total_amount": random.randint(300, 2000),
        "booking_date": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
        "travel_date": (datetime.utcnow() + timedelta(days=random.randint(1, 90))).date().isoformat()
    })

@app.route('/cancel/<booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a travel booking"""
    try:
        # Simulate cancellation processing
        # In real system, this would check booking status, calculate fees, process refunds
        success_rate = 0.9  # 90% success rate for simulation
        
        if random.random() < success_rate:
            cancellation_fee = random.randint(50, 200)
            return jsonify({
                "success": True,
                "booking_id": booking_id,
                "status": "cancelled",
                "cancellation_fee": cancellation_fee,
                "refund_amount": random.randint(200, 1500),
                "processing_time": "3-5 business days",
                "message": "Booking cancelled successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "booking_id": booking_id,
                "error": "Cancellation not allowed - flight departure within 2 hours",
                "message": "Please contact customer service"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Cancellation processing failed",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002, host='0.0.0.0')