# Credit Card Payment System API

A comprehensive Flask-based API system for credit card payment simulations with merchants, offers, rewards, and profile history tracking.

## Project Structure

```
bus-payments-offers-rewards-svc/
├── app/                    # Main application directory
│   ├── app.py             # Flask application setup
│   ├── models.py          # Database models
│   ├── seed_data.py       # Sample data generator
│   ├── static/            # Static files
│   │   └── swagger.yaml   # API documentation
│   ├── routes/            # API blueprints
│   │   ├── customers.py   # Customer management
│   │   ├── payments.py    # Payment processing
│   │   ├── offers.py      # Offer management
│   │   ├── rewards.py     # Rewards system
│   │   ├── merchants.py   # Merchant management
│   │   └── profile_history.py # Profile history
│   └── test/              # Test files
│       ├── conftest.py    # Test configuration
│       ├── test_api.py    # API tests
│       └── test_endpoints.py # Endpoint testing script
├── bruno/                 # Bruno API collection
│   ├── bruno.json         # Collection configuration
│   ├── environments/      # Environment variables
│   ├── Health/            # Health check tests
│   ├── Customers/         # Customer API tests
│   ├── Merchants/         # Merchant API tests
│   ├── Payments/          # Payment API tests
│   ├── Offers/            # Offer API tests
│   ├── Rewards/           # Reward API tests
│   └── Profile History/   # Profile history tests
├── run.py                 # Application runner
├── requirements.txt       # Dependencies
├── README.md             # Documentation
└── .env.example          # Environment template
```

## Features

- **Customer Management**: CRUD operations for customers and credit card products
- **Merchant Database**: Comprehensive merchant management with categories and analytics
- **Payment Processing**: Make payments, view payment history with time period filtering, automatic offer application
- **Offers System**: Manage offers with 20+ categories, merchant-specific offers, expiry dates, and activation
- **Rewards Program**: Points accumulation, redemption, and dollar value conversion
- **Merchant Offer History**: Track merchant offer usage and performance analytics
- **Customer Profile History**: Detailed tracking of customer's merchant offer usage with amount saved
- **Analytics**: Spending analytics, merchant performance, and reward balance tracking

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database with sample data**:
   ```bash
   cd app && python seed_data.py
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

4. **Access the API**:
   - Main application: http://localhost:5001
   - Swagger documentation: http://localhost:5001/api/docs
   - Health check: http://localhost:5001/api/health

5. **Test the APIs**:
   ```bash
   cd app/test && python test_endpoints.py
   ```

6. **Use Bruno Collection**:
   - Install Bruno: https://www.usebruno.com/
   - Open the `bruno` folder as a collection
   - Test all endpoints with sample data

## API Endpoints

### Health Check
- `GET /api/health` - Health check endpoint

### Customer Management
- `GET /api/customers` - List all customers (with pagination and filtering)
- `GET /api/customers/{id}` - Get customer details with credit cards
- `POST /api/customers` - Create a new customer
- `PUT /api/customers/{id}` - Update customer information
- `DELETE /api/customers/{id}` - Delete a customer
- `GET /api/customers/{id}/credit-cards` - Get customer's credit cards
- `POST /api/customers/{id}/credit-cards` - Add a new credit card
- `PUT /api/customers/{id}/credit-cards/{card_id}` - Update credit card
- `DELETE /api/customers/{id}/credit-cards/{card_id}` - Delete credit card

### Payment Processing
- `POST /api/payments` - Make a payment
- `GET /api/payments` - List payments with filtering options
- `GET /api/payments/{id}` - Get payment details
- `GET /api/payments/customer/{customer_id}` - Get customer's payment history
- `POST /api/payments/{id}/refund` - Process payment refund
- `GET /api/payments/analytics/spending` - Get spending analytics

### Offers Management
- `GET /api/offers` - List all offers with filtering
- `GET /api/offers/{id}` - Get offer details
- `POST /api/offers` - Create a new offer
- `PUT /api/offers/{id}` - Update an offer
- `DELETE /api/offers/{id}` - Delete an offer
- `POST /api/offers/{id}/activate` - Activate offer for a customer
- `POST /api/offers/{id}/deactivate` - Deactivate offer for a customer
- `GET /api/offers/customer/{customer_id}` - Get customer's offers
- `GET /api/offers/categories` - Get available offer categories

### Rewards System
- `GET /api/rewards/customer/{customer_id}` - Get customer's rewards
- `GET /api/rewards/{id}` - Get reward details
- `POST /api/rewards` - Create manual reward
- `POST /api/rewards/{id}/redeem` - Redeem specific reward
- `POST /api/rewards/customer/{customer_id}/redeem` - Redeem from customer balance
- `GET /api/rewards/customer/{customer_id}/balance` - Get reward points balance
- `GET /api/rewards/customer/{customer_id}/history` - Get redemption history
- `POST /api/rewards/expire-check` - Check and expire old rewards

### Merchant Management
- `GET /api/merchants` - List all merchants with filtering and pagination
- `POST /api/merchants` - Create a new merchant
- `GET /api/merchants/{merchant_id}` - Get merchant details
- `PUT /api/merchants/{merchant_id}` - Update merchant information
- `DELETE /api/merchants/{merchant_id}` - Delete a merchant
- `GET /api/merchants/{merchant_id}/offers` - Get offers by merchant
- `GET /api/merchants/analytics` - Merchant performance analytics
- `GET /api/merchants/{merchant_id}/analytics` - Individual merchant analytics

### Merchant Offer History
- `GET /api/merchants/{merchant_id}/offer-history` - Get merchant's offer usage history
- `GET /api/merchants/offer-history` - Get all merchant offer history with filtering

### Customer Profile History
- `GET /api/profile-history` - List all customer profile history with filtering
- `GET /api/profile-history/customer/{customer_id}` - Get customer's profile history
- `POST /api/profile-history` - Create profile history entry (usually done automatically during payments)

## Sample Data

The system includes comprehensive sample data:
- 4 customers with different profiles
- 10 merchants across diverse categories (E-commerce, Restaurant, Airlines, Gas Station, Hotel, etc.)
- 5 credit cards with various product types (PLATINUM, GOLD, SILVER, BASIC)
- 5+ offers with merchant relationships and expanded categories (20+ categories available)
- 25+ payment transactions with automatic merchant offer application
- Rewards and redemption history
- Merchant offer history tracking
- Customer profile history with merchant offer usage

## Data Models

### Customer
- Personal information (name, email, phone, address, DOB)
- Multiple credit cards
- Rewards and offer activations

### Credit Card
- Card details (masked number, expiry, holder name)
- Product types with different reward multipliers
- Credit limits and available credit

### Payment
- Transaction details (amount, merchant, category)
- Status tracking (PENDING, COMPLETED, FAILED, REFUNDED)
- Automatic reward point calculation

### Offer
- 20+ Categories: TRAVEL, MERCHANT, DINING, FUEL, SHOPPING, CASHBACK, GROCERY, ENTERTAINMENT, FITNESS, SUBSCRIPTION, etc.
- Merchant-specific offers with merchant relationships
- Discount percentages and caps
- Expiry dates and usage limits
- Activation tracking per customer

### Reward
- Point earning and redemption
- Dollar value conversion (1 point = $0.01)
- Status tracking (EARNED, REDEEMED, EXPIRED)
- Expiry management

### Merchant
- Comprehensive merchant database with name and category
- 21+ Categories: E_COMMERCE, RESTAURANT, AIRLINE, GAS_STATION, HOTEL, RETAIL_STORE, etc.
- Merchant-specific analytics and performance tracking
- Integration with offers and payment processing

### Merchant Offer History
- Track merchant offer usage and performance
- Amount saved tracking per merchant offer
- Analytics for merchant performance optimization

### Customer Profile History
- Complete history of customer's merchant offer usage
- Amount availed tracking with statement descriptors
- Date and merchant information for each transaction

## Business Logic

### Reward Point Calculation
- Base: 1 point per dollar spent
- Card type multipliers:
  - PLATINUM: 3x points
  - GOLD: 2x points
  - SILVER: 1.5x points
  - BASIC: 1x points
- Category bonuses for DINING and TRAVEL (1.5x additional)

### Offer Activation
- Customers must activate offers to use them
- Usage tracking and limits per customer
- Automatic deactivation on expiry

### Payment Processing
- Credit limit validation
- Automatic reward point calculation
- Refund processing with point adjustments

## Query Parameters

Most list endpoints support:
- `page` - Page number for pagination
- `per_page` - Items per page (default: 10)
- `start_date` / `end_date` - Date range filtering (ISO format)
- Various entity-specific filters

## Response Format

All responses follow a consistent JSON format:
```json
{
  "data": {...},
  "total": 100,
  "pages": 10,
  "current_page": 1,
  "per_page": 10
}
```

Error responses:
```json
{
  "error": "Error message description"
}
```

## Testing

Use the provided sample data to test all endpoints. The `seed_data.py` script creates a comprehensive dataset for testing various scenarios.

Example test scenarios:
1. Customer registration and credit card issuance
2. Payment processing with automatic reward calculation
3. Offer activation and usage tracking
4. Reward redemption and balance management
5. Payment history and analytics
6. Offer expiry and reward expiration handling