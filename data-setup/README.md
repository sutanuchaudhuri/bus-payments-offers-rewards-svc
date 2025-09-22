# Database Setup Guide

This guide explains how to set up and manage the database schema and data for the Bus Payments & Rewards System.

## Overview

The database setup is now separated into distinct phases:
1. **Schema Setup**: Creates/updates database tables and structure
2. **Basic Data Population**: Creates sample data with 1 customer (Sutanu Chaudhuri)
3. **Bulk Customer Setup**: Creates 500 diverse customers with varied profiles, bonuses, and transaction patterns

## Setup Scripts

### 1. Schema Setup (`schema_setup.py`)

**Purpose**: Manages database schema creation and updates without populating data.

**Usage**:
```bash
# Create/update schema (default action)
python schema_setup.py create

# Show detailed table information
python schema_setup.py info

# Create schema backup
python schema_setup.py backup

# Drop all tables (use with caution!)
python schema_setup.py drop
```

**Features**:
- ✅ Creates or updates database schema
- ✅ Verifies all expected tables are present
- ✅ Shows detailed table structure with columns, indexes, and foreign keys
- ✅ Creates schema backups with timestamps
- ✅ Safe table dropping with confirmation
- ✅ Detects existing vs. additional tables

### 2. Basic Data Population (`comprehensive_data_setup.py`)

**Purpose**: Populates the database with basic sample data including one customer and merchants.

**Usage**:
```bash
# Run basic data setup (includes schema verification)
python comprehensive_data_setup.py
```

**What it creates**:
- 1 Customer (Sutanu Chaudhuri)
- 3 Credit Cards (Platinum, Gold, Silver)
- 3 Card Tokens (for secure transactions)
- 544+ Merchants:
  - 6 Airlines
  - 20 Hotel companies
  - 500 Restaurants (across 3 continents)
  - 10 Insurance companies
  - 10 Car rental companies
- 50 Offers (across all merchant categories)
- 3000 Transactions (over the last 2 years)
- Associated reward points

### 3. Bulk Customer Setup (`bulk_customer_setup.py`) 🆕

**Purpose**: Creates 500 diverse customers with varied profiles, bonus structures, transaction patterns, and personalized offers.

**Usage**:
```bash
# Run bulk customer setup (may take 5-10 minutes)
python bulk_customer_setup.py
```

**What it creates**:
- **500 Customers** across 8 different profiles:
  - Budget Conscious (low spending, basic cards)
  - Regular Shopper (medium spending, retail focus)
  - Business Traveler (high spending, travel-focused)
  - Luxury Spender (very high spending, premium cards)
  - Family Oriented (medium spending, family purchases)
  - Tech Professional (medium-high spending, tech focus)
  - Young Professional (moderate spending, entertainment)
  - Insurance Buyer (insurance/automotive focus)

- **1000+ Credit Cards** with realistic limits and utilization
- **500 Credit Profiles** with varied credit scores (580-850)
- **60,000+ Transactions** spanning 12 months per customer
- **5 Welcome Bonus Types**:
  - 50K Points ($500 value)
  - 75K Points ($750 value)
  - 100K Points ($1000 value)
  - $200 Cashback Bonus
  - 60K Travel Miles ($720 value)
- **1500+ Personalized Offers** based on spending patterns
- **80,000+ Reward Points** with category multipliers

### 4. Quick Setup Runners

**Schema Only**:
```bash
python run_schema_setup.py
```

**Basic Setup**:
```bash
python run_setup.py
```

**Bulk Customer Setup**:
```bash
python run_bulk_customer_setup.py
```

## Recommended Workflows

### Development Testing (Basic)
1. **Create Schema**: `python schema_setup.py create`
2. **Basic Data**: `python comprehensive_data_setup.py`
3. **Start Application**: `python ../run.py`

### Comprehensive Testing (500 Customers)
1. **Create Schema**: `python schema_setup.py create`
2. **Load Merchants**: `python comprehensive_data_setup.py` (for merchant data)
3. **Bulk Customers**: `python bulk_customer_setup.py` (⚠️ takes 5-10 minutes)
4. **Start Application**: `python ../run.py`

### Production-like Environment
1. **Schema + Basic Data**: Follow basic workflow first
2. **Add Bulk Customers**: Run bulk setup for realistic scale testing
3. **Verify Data**: Use schema info and API endpoints to validate

## Customer Profile Distribution

The bulk setup creates customers across 8 distinct profiles with realistic characteristics:

| Profile | Spending Range | Frequency | Preferred Categories | Card Types |
|---------|---------------|-----------|---------------------|------------|
| Budget Conscious | $50-300 | 2-5/month | Grocery, Gas | Silver |
| Regular Shopper | $100-800 | 8-15/month | Restaurant, Grocery, Retail | Silver, Gold |
| Business Traveler | $200-2500 | 15-25/month | Airline, Hotel, Restaurant | Gold, Platinum |
| Luxury Spender | $500-5000 | 20-35/month | Airline, Hotel, Retail | Platinum |
| Family Oriented | $150-1200 | 10-20/month | Grocery, Gas, Restaurant | Silver, Gold |
| Tech Professional | $200-1500 | 12-18/month | Retail, Restaurant, Online | Gold, Platinum |
| Young Professional | $80-600 | 8-12/month | Restaurant, Entertainment | Silver, Gold |
| Insurance Buyer | $100-800 | 3-8/month | Insurance, Automotive | Silver, Gold |

## Bonus and Reward Systems

### Welcome Bonuses (60% of customers receive)
- **50K Points**: Spend $3,000 in first 3 months → $500 value
- **75K Points**: Spend $5,000 in first 3 months → $750 value  
- **100K Points**: Spend $6,000 in first 3 months → $1,000 value
- **$200 Cashback**: Spend $1,000 in first 3 months
- **60K Miles**: Spend $4,000 in first 3 months → $720 value

### Transaction Rewards
- **Card Multipliers**: Platinum (3x), Gold (2x), Silver (1.5x)
- **Category Bonuses**: Travel (2x), Dining (1.5x)
- **Personalized Offers**: Based on individual spending patterns

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check DATABASE_URL environment variable
echo $DATABASE_URL

# Verify app configuration
python -c "from app.app import create_app; app = create_app(); print(app.config['SQLALCHEMY_DATABASE_URI'])"
```

**2. Schema Verification Failures**
```bash
# Check current database status
python schema_setup.py info

# Recreate schema if needed
python schema_setup.py drop  # Type 'DROP ALL TABLES' to confirm
python schema_setup.py create
```

**3. Data Population Errors**
```bash
# Ensure schema exists first
python schema_setup.py create

# Clean and repopulate data
python comprehensive_data_setup.py
```

**4. UNIQUE Constraint Violations**
The scripts now handle existing data gracefully. If you encounter constraint violations:
```bash
# Clean existing data and start fresh
python comprehensive_data_setup.py
```

### Validation Commands

**Check Schema Status**:
```bash
python schema_setup.py info
```

**Verify Data Population**:
```bash
python -c "
from app.app import create_app
from app.models import *

app = create_app()
with app.app_context():
    print(f'Customers: {Customer.query.count()}')
    print(f'Credit Cards: {CreditCard.query.count()}')
    print(f'Merchants: {Merchant.query.count()}')
    print(f'Payments: {Payment.query.count()}')
"
```

## File Structure

```
data-setup/
├── schema_setup.py              # Main schema management script
├── run_schema_setup.py          # Quick schema setup runner
├── comprehensive_data_setup.py  # Data population script
├── run_setup.py                 # Complete setup runner
└── README.md                    # This documentation
```

## Environment Requirements

- Python 3.8+
- Flask-SQLAlchemy
- Faker library for sample data
- SQLite/PostgreSQL/MySQL (depending on configuration)

## Security Notes

- Sample data includes test credit card numbers (not real)
- Tokens are format-preserving but randomly generated
- Use proper encryption and security measures in production
- Never commit real credit card or personal information

---

For additional help or issues, refer to the main project documentation or create an issue in the project repository.
