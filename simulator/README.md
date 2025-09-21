# Simulator Services Integration

This folder contains simulator services that mock external APIs for travel, hotel, and shopping offers. The main application can query these services to provide real-time pricing and availability information to customers.

## Architecture Overview

```
Main App (Port 5001) → Integration Endpoints → Simulator Services
├── Travel Booking Service (Port 5002)
├── Hotel Booking Service (Port 5003)
└── Shopping Service (Port 5004)
```

## Services

### 1. Travel Booking Service (Port 5002)
Simulates airline booking APIs for travel offers.

**Features:**
- Airport listings
- Flight search with dynamic pricing
- Flight booking simulation
- Booking management

**Key Endpoints:**
- `GET /airports` - List available airports
- `GET /search/flights` - Search flights by criteria
- `POST /book/flight` - Book a flight
- `GET /booking/{reference}` - Get booking details

### 2. Hotel Booking Service (Port 5003)
Simulates hotel booking APIs for accommodation offers.

**Features:**
- City and hotel listings
- Hotel search with room availability
- Dynamic pricing based on season/demand
- Hotel booking simulation

**Key Endpoints:**
- `GET /cities` - List available cities
- `GET /search/hotels` - Search hotels by criteria
- `POST /book/hotel` - Book a hotel
- `GET /booking/{reference}` - Get booking details

### 3. Shopping Service (Port 5004)
Simulates e-commerce APIs for shopping offers.

**Features:**
- Product catalog with categories and brands
- Product search with filters
- Shopping cart simulation
- Order creation and tracking

**Key Endpoints:**
- `GET /categories` - List product categories
- `GET /products/search` - Search products
- `POST /cart/add` - Add to cart
- `POST /order/create` - Create order

## Integration Endpoints

The main application provides integration endpoints that query the simulator services:

### Base URL: `http://localhost:5001/api/integration`

#### Status & Health
- `GET /simulator/status` - Check all simulator services status

#### Travel Integration
- `GET /offers/travel/airports` - Get airports for travel offers
- `GET /offers/travel/search-flights` - Search flights for travel offers
- `POST /offers/travel/book-flight` - Book flight through offer
- `GET /offers/travel/booking/{reference}` - Get travel booking details

#### Hotel Integration
- `GET /offers/hotel/cities` - Get cities for hotel offers
- `GET /offers/hotel/search-hotels` - Search hotels for offers
- `POST /offers/hotel/book-hotel` - Book hotel through offer
- `GET /offers/hotel/booking/{reference}` - Get hotel booking details

#### Shopping Integration
- `GET /offers/shopping/categories` - Get shopping categories for offers
- `GET /offers/shopping/search` - Search products for offers
- `POST /offers/shopping/add-to-cart` - Add product to cart
- `POST /offers/shopping/create-order` - Create order through offer
- `GET /offers/shopping/order/{id}` - Get order status

#### Combined Services
- `GET /offers/search/travel-package` - Search combined flight + hotel packages

## Quick Start

### 1. Start Simulator Services
```bash
cd simulator
./start_simulators.sh
```

This will start all three simulator services:
- Travel Booking Service on port 5002
- Hotel Booking Service on port 5003  
- Shopping Service on port 5004

### 2. Start Main Application
```bash
python run.py
```

### 3. Test Integration
```bash
python test_simulators.py
```

## Usage Examples

### Travel Offer Integration

```bash
# Get available airports
curl "http://localhost:5001/api/integration/offers/travel/airports"

# Search flights for NYC to LAX
curl "http://localhost:5001/api/integration/offers/travel/search-flights?origin=NYC&destination=LAX&departure_date=2025-11-15&passengers=2"

# Search travel packages (flight + hotel)
curl "http://localhost:5001/api/integration/offers/search/travel-package?origin=NYC&destination=MIA&departure_date=2025-11-15&return_date=2025-11-18&passengers=2"
```

### Hotel Offer Integration

```bash
# Get available cities
curl "http://localhost:5001/api/integration/offers/hotel/cities"

# Search hotels in New York
curl "http://localhost:5001/api/integration/offers/hotel/search-hotels?city=new-york&check_in=2025-11-15&check_out=2025-11-17&guests=2"
```

### Shopping Offer Integration

```bash
# Get product categories
curl "http://localhost:5001/api/integration/offers/shopping/categories"

# Search electronics
curl "http://localhost:5001/api/integration/offers/shopping/search?category=electronics&q=laptop&limit=5"
```

## Offer Use Cases

### 1. Travel Offers
When a customer has a TRAVEL offer:
1. Customer requests travel information
2. App queries travel simulator for flights
3. Customer selects preferred flight
4. Offer discount is applied
5. Booking is processed through simulator

### 2. Hotel Offers
When a customer has accommodation offers:
1. Customer searches for hotels in destination
2. App queries hotel simulator for availability
3. Real-time pricing with offer discounts
4. Customer books through the offer

### 3. Shopping Offers
When a customer has shopping offers:
1. Customer browses product categories
2. App queries shopping simulator for products
3. Offer-specific discounts are displayed
4. Customer purchases through the offer

### 4. Combined Offers
For premium offers (travel packages):
1. Customer searches for vacation packages
2. App queries both travel and hotel simulators
3. Combined packages with additional savings
4. Single booking for flight + hotel

## Management Commands

### Start Services
```bash
cd simulator
./start_simulators.sh
```

### Stop Services  
```bash
cd simulator
./stop_simulators.sh
```

### Check Status
```bash
# Via script
python simulator/simulator_manager.py status

# Via API
curl "http://localhost:5001/api/integration/simulator/status"
```

### Individual Service Testing
```bash
# Test travel service directly
curl "http://localhost:5002/health"

# Test hotel service directly  
curl "http://localhost:5003/health"

# Test shopping service directly
curl "http://localhost:5004/health"
```

## Configuration

### Ports
- Main App: 5001
- Travel Service: 5002
- Hotel Service: 5003
- Shopping Service: 5004

### Data
All services use mock data with realistic:
- Pricing algorithms
- Seasonal variations
- Dynamic inventory
- Random availability

### Customization
To add new services or modify existing ones:
1. Create new service in `simulator/services/`
2. Add integration endpoints in `app/routes/integration.py`
3. Register new blueprint in `app/app.py`
4. Update startup scripts

## Error Handling

The integration layer includes:
- Service timeout handling (10s timeout)
- Connection error recovery
- Graceful degradation when services are unavailable
- Detailed error reporting

## Performance

Each simulator service:
- Responds within 100-500ms typically
- Supports concurrent requests
- Uses minimal memory footprint
- Provides realistic response times

## Future Enhancements

Potential additions:
- Car rental service simulator
- Restaurant booking simulator
- Event ticket simulator
- Loyalty program simulator
- Payment processing simulator
- Notification service simulator