from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric

# Create a db instance that will be initialized by the app
db = SQLAlchemy()

try:
    from sqlalchemy import Enum as SQLAlchemyEnum
except ImportError:
    # For IDEs that can't resolve the import
    SQLAlchemyEnum = Enum

# Enums for better data integrity
class OfferCategory(Enum):
    TRAVEL = "TRAVEL"
    MERCHANT = "MERCHANT"
    CASHBACK = "CASHBACK"
    DINING = "DINING"
    FUEL = "FUEL"
    SHOPPING = "SHOPPING"
    GROCERY = "GROCERY"
    ENTERTAINMENT = "ENTERTAINMENT"
    HEALTH_WELLNESS = "HEALTH_WELLNESS"
    TELECOMMUNICATIONS = "TELECOMMUNICATIONS"
    UTILITIES = "UTILITIES"
    INSURANCE = "INSURANCE"
    EDUCATION = "EDUCATION"
    AUTOMOTIVE = "AUTOMOTIVE"
    HOME_GARDEN = "HOME_GARDEN"
    FASHION = "FASHION"
    ELECTRONICS = "ELECTRONICS"
    SUBSCRIPTION = "SUBSCRIPTION"
    FINANCE = "FINANCE"
    SPORTS_FITNESS = "SPORTS_FITNESS"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class RewardStatus(Enum):
    EARNED = "EARNED"
    REDEEMED = "REDEEMED"
    EXPIRED = "EXPIRED"

class CreditCardProduct(Enum):
    PLATINUM = "PLATINUM"
    GOLD = "GOLD"
    SILVER = "SILVER"
    BASIC = "BASIC"

class CardType(Enum):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMERICAN_EXPRESS = "AMERICAN_EXPRESS"
    DISCOVER = "DISCOVER"

class MerchantCategory(Enum):
    RESTAURANT = "RESTAURANT"
    RETAIL_STORE = "RETAIL_STORE"
    GAS_STATION = "GAS_STATION"
    AIRLINE = "AIRLINE"
    HOTEL = "HOTEL"
    E_COMMERCE = "E_COMMERCE"
    GROCERY_STORE = "GROCERY_STORE"
    PHARMACY = "PHARMACY"
    ENTERTAINMENT_VENUE = "ENTERTAINMENT_VENUE"
    HEALTHCARE_PROVIDER = "HEALTHCARE_PROVIDER"
    TELECOM_PROVIDER = "TELECOM_PROVIDER"
    UTILITY_COMPANY = "UTILITY_COMPANY"
    INSURANCE_COMPANY = "INSURANCE_COMPANY"
    EDUCATIONAL_INSTITUTION = "EDUCATIONAL_INSTITUTION"
    AUTOMOTIVE_SERVICE = "AUTOMOTIVE_SERVICE"
    HOME_IMPROVEMENT = "HOME_IMPROVEMENT"
    FASHION_RETAILER = "FASHION_RETAILER"
    ELECTRONICS_STORE = "ELECTRONICS_STORE"
    SUBSCRIPTION_SERVICE = "SUBSCRIPTION_SERVICE"
    FINANCIAL_SERVICE = "FINANCIAL_SERVICE"
    FITNESS_CENTER = "FITNESS_CENTER"

# Merchant Model
class Merchant(db.Model):
    CAB_RENTAL = "CAB_RENTAL"
    __tablename__ = 'merchants'
    
    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.String(50), unique=True, nullable=False)  # External merchant identifier
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(SQLAlchemyEnum(MerchantCategory), nullable=False)
    website = db.Column(db.String(255))
    contact_email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    offers = db.relationship('Offer', backref='merchant_details', lazy=True)
    merchant_offer_history = db.relationship('MerchantOfferHistory', backref='merchant', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'merchant_id': self.merchant_id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'website': self.website,
            'contact_email': self.contact_email,
            'phone': self.phone,
            'address': self.address,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Customer Model
class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    credit_cards = db.relationship('CreditCard', backref='customer', lazy=True, cascade='all, delete-orphan')
    rewards = db.relationship('Reward', backref='customer', lazy=True)
    activated_offers = db.relationship('CustomerOffer', backref='customer', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'address': self.address,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Credit Card Model
class CreditCard(db.Model):
    __tablename__ = 'credit_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    card_number = db.Column(db.String(16), unique=True, nullable=False)
    card_holder_name = db.Column(db.String(200), nullable=False)
    expiry_month = db.Column(db.Integer, nullable=False)
    expiry_year = db.Column(db.Integer, nullable=False)
    product_type = db.Column(SQLAlchemyEnum(CreditCardProduct), nullable=False)
    card_type = db.Column(SQLAlchemyEnum(CardType), nullable=False)  # Added card type
    credit_limit = db.Column(Numeric(10, 2), nullable=False)
    available_credit = db.Column(Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='credit_card', lazy=True)
    tokens = db.relationship('CardToken', backref='credit_card', lazy=True, cascade='all, delete-orphan')

    def get_first_six(self):
        """Get first 6 digits of card number"""
        return self.card_number[:6]

    def get_last_four(self):
        """Get last 4 digits of card number"""
        return self.card_number[-4:]

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'card_number': f"****-****-****-{self.card_number[-4:]}",  # Masked for security
            'card_holder_name': self.card_holder_name,
            'expiry_month': self.expiry_month,
            'expiry_year': self.expiry_year,
            'product_type': self.product_type.value,
            'card_type': self.card_type.value,
            'credit_limit': float(self.credit_limit),
            'available_credit': float(self.available_credit),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

    def to_dict_with_token(self, token_id=None):
        """Return card details with token information for secure API responses"""
        return {
            'token_id': token_id,
            'first_six': self.get_first_six(),
            'last_four': self.get_last_four(),
            'card_type': self.card_type.value,
            'product_type': self.product_type.value,
            'card_holder_name': self.card_holder_name,
            'expiry_month': self.expiry_month,
            'expiry_year': self.expiry_year,
            'credit_limit': float(self.credit_limit),
            'available_credit': float(self.available_credit),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
# Payment Model
class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_cards.id'), nullable=False)
    amount = db.Column(Numeric(10, 2), nullable=False)
    merchant_name = db.Column(db.String(200), nullable=False)
    merchant_category = db.Column(db.String(100))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(SQLAlchemyEnum(PaymentStatus), default=PaymentStatus.PENDING)
    reference_number = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'credit_card_id': self.credit_card_id,
            'amount': float(self.amount),
            'merchant_name': self.merchant_name,
            'merchant_category': self.merchant_category,
            'transaction_date': self.transaction_date.isoformat(),
            'status': self.status.value,
            'reference_number': self.reference_number,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

# Card Token Mapping Table
class CardToken(db.Model):
    __tablename__ = 'card_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.String(16), unique=True, nullable=False)  # Format-preserving token
    card_id = db.Column(db.Integer, db.ForeignKey('credit_cards.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)  # Optional token expiration

    # Relationships
    customer = db.relationship('Customer', backref='card_tokens', lazy=True)

    # Unique constraint to prevent duplicate tokens for same card
    __table_args__ = (db.UniqueConstraint('card_id', 'token_id'),)

    def to_dict(self):
        return {
            'id': self.id,
            'token_id': self.token_id,
            'card_id': self.card_id,
            'customer_id': self.customer_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

# Offer Model
class Offer(db.Model):
    __tablename__ = 'offers'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    offer_id = db.Column(db.String(20), unique=True, nullable=False)  # Alphanumeric offer ID
    offer_id = db.Column(db.String(20), unique=True, nullable=False)  # Alphanumeric offer ID
    category = db.Column(SQLAlchemyEnum(OfferCategory), nullable=False)
    merchant_name = db.Column(db.String(200))  # Deprecated - use merchant relationship
    discount_percentage = db.Column(Numeric(5, 2))
    reward_points = db.Column(db.Integer, default=0)
    max_discount_amount = db.Column(Numeric(10, 2))
    start_date = db.Column(db.DateTime, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)
    terms_and_conditions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    max_usage_per_customer = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    customer_activations = db.relationship('CustomerOffer', backref='offer', lazy=True)
    merchant_history = db.relationship('MerchantOfferHistory', backref='offer', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'offer_id': self.offer_id,
            'offer_id': self.offer_id,
            'category': self.category.value,
            'merchant_name': self.merchant_details.name if self.merchant_details else self.merchant_name,
            'merchant_category': self.merchant_details.category.value if self.merchant_details else None,
            'min_transaction_amount': float(self.min_transaction_amount) if self.min_transaction_amount else None,
            'merchant_category': self.merchant_details.category.value if self.merchant_details else None,
            'discount_percentage': float(self.discount_percentage) if self.discount_percentage else None,
            'reward_points': self.reward_points,
            'start_date': self.start_date.isoformat(),
            'expiry_date': self.expiry_date.isoformat(),
            'terms_and_conditions': self.terms_and_conditions,
            'is_active': self.is_active,
            'max_usage_per_customer': self.max_usage_per_customer,
            'created_at': self.created_at.isoformat()
        }

# Customer Offer Activation Model
class CustomerOffer(db.Model):
    __tablename__ = 'customer_offers'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=False)
    activation_date = db.Column(db.DateTime, default=datetime.utcnow)
    usage_count = db.Column(db.Integer, default=0)
    total_savings = db.Column(Numeric(10, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    
    __table_args__ = (db.UniqueConstraint('customer_id', 'offer_id'),)
    is_active = db.Column(db.Boolean, default=True)


    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'offer_id': self.offer_id,
            'activation_date': self.activation_date.isoformat(),
            'usage_count': self.usage_count,
            'total_savings': float(self.total_savings),
            'is_active': self.is_active
        }

# Reward Model
class Reward(db.Model):
    __tablename__ = 'rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True)  # Nullable for manual rewards
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=True)
    points_earned = db.Column(db.Integer, nullable=False)
    points_redeemed = db.Column(db.Integer, default=0)
    dollar_value = db.Column(Numeric(10, 2), nullable=False)  # Points to dollar conversion
    status = db.Column(SQLAlchemyEnum(RewardStatus), default=RewardStatus.EARNED)
    earned_date = db.Column(db.DateTime, default=datetime.utcnow)
    redeemed_date = db.Column(db.DateTime, nullable=True)
    expiry_date = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'payment_id': self.payment_id,
            'offer_id': self.offer_id,
            'points_earned': self.points_earned,
            'points_redeemed': self.points_redeemed,
            'dollar_value': float(self.dollar_value),
            'status': self.status.value,
            'earned_date': self.earned_date.isoformat(),
            'redeemed_date': self.redeemed_date.isoformat() if self.redeemed_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'description': self.description
        }

# Merchant Offer History Model
class MerchantOfferHistory(db.Model):
    __tablename__ = 'merchant_offer_history'
    
    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True)
    transaction_amount = db.Column(Numeric(10, 2), nullable=False)
    discount_applied = db.Column(Numeric(10, 2), default=0.00)
    reward_points_earned = db.Column(db.Integer, default=0)
    statement_descriptor = db.Column(db.String(255))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='merchant_offer_usage', lazy=True)
    payment = db.relationship('Payment', backref='merchant_offer_history', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'merchant_id': self.merchant_id,
            'merchant_name': self.merchant.name,
            'offer_id': self.offer_id,
            'offer_title': self.offer.title,
            'customer_id': self.customer_id,
            'customer_name': f"{self.customer.first_name} {self.customer.last_name}",
            'payment_id': self.payment_id,
            'transaction_amount': float(self.transaction_amount),
            'discount_applied': float(self.discount_applied),
            'reward_points_earned': self.reward_points_earned,
            'statement_descriptor': self.statement_descriptor,
            'transaction_date': self.transaction_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }

# Customer Profile History Model (tracks customer's merchant offer usage)
class CustomerProfileHistory(db.Model):
    __tablename__ = 'customer_profile_history'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True)
    amount_availed = db.Column(Numeric(10, 2), nullable=False)  # Discount amount saved
    transaction_amount = db.Column(Numeric(10, 2), nullable=False)  # Total transaction amount
    statement_descriptor = db.Column(db.String(255), nullable=False)
    availed_date = db.Column(db.DateTime, default=datetime.utcnow)
    offer_category = db.Column(SQLAlchemyEnum(OfferCategory), nullable=False)
    merchant_category = db.Column(SQLAlchemyEnum(MerchantCategory), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='profile_history', lazy=True)
    merchant = db.relationship('Merchant', backref='customer_usage_history', lazy=True)
    offer = db.relationship('Offer', backref='customer_usage_history', lazy=True)
    payment = db.relationship('Payment', backref='profile_history', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': f"{self.customer.first_name} {self.customer.last_name}",
            'merchant_id': self.merchant_id,
            'merchant_name': self.merchant.name,
            'offer_id': self.offer_id,
            'offer_title': self.offer.title,
            'payment_id': self.payment_id,
            'amount_availed': float(self.amount_availed),
            'transaction_amount': float(self.transaction_amount),
            'savings_percentage': round((float(self.amount_availed) / float(self.transaction_amount)) * 100, 2),
            'statement_descriptor': self.statement_descriptor,
            'availed_date': self.availed_date.isoformat(),
            'offer_category': self.offer_category.value,
            'merchant_category': self.merchant_category.value,
            'created_at': self.created_at.isoformat()
        }

# New Enums for Enhanced Features
class CustomerCategory(Enum):
    PREMIUM = "PREMIUM"
    STANDARD = "STANDARD"
    BASIC = "BASIC"

class CreditRating(Enum):
    EXCELLENT = "EXCELLENT"    # 750-850
    GOOD = "GOOD"             # 700-749
    FAIR = "FAIR"             # 650-699
    POOR = "POOR"             # 600-649
    VERY_POOR = "VERY_POOR"   # <600

class BookingStatus(Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    PENDING_CANCELLATION = "PENDING_CANCELLATION"
    REFUNDED = "REFUNDED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"

class DisputeStatus(Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    ESCALATED = "ESCALATED"

class DisputeCategory(Enum):
    UNAUTHORIZED_TRANSACTION = "UNAUTHORIZED_TRANSACTION"
    BILLING_ERROR = "BILLING_ERROR"
    SERVICE_NOT_RECEIVED = "SERVICE_NOT_RECEIVED"
    PRODUCT_NOT_RECEIVED = "PRODUCT_NOT_RECEIVED"
    DUPLICATE_CHARGE = "DUPLICATE_CHARGE"
    INCORRECT_AMOUNT = "INCORRECT_AMOUNT"
    CANCELLED_RECURRING = "CANCELLED_RECURRING"
    OTHER = "OTHER"

class RefundStatus(Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    PROCESSED = "PROCESSED"
    COMPLETED = "COMPLETED"

# Enhanced Customer Profile
class CustomerCreditProfile(db.Model):
    __tablename__ = 'customer_credit_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, unique=True)
    credit_score = db.Column(db.Integer, nullable=False)
    credit_rating = db.Column(SQLAlchemyEnum(CreditRating), nullable=False)
    category = db.Column(SQLAlchemyEnum(CustomerCategory), nullable=False, default=CustomerCategory.STANDARD)
    annual_income = db.Column(Numeric(12, 2))
    debt_to_income_ratio = db.Column(Numeric(5, 2))  # Percentage
    years_of_credit_history = db.Column(db.Integer)
    number_of_credit_accounts = db.Column(db.Integer)
    recent_credit_inquiries = db.Column(db.Integer)
    payment_history_score = db.Column(db.Integer)  # Out of 100
    credit_utilization = db.Column(Numeric(5, 2))  # Percentage
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref=db.backref('credit_profile', uselist=False))

# Credit Card Products
class CreditCardProductDetails(db.Model):
    __tablename__ = 'credit_card_product_details'
    
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False, unique=True)
    product_code = db.Column(db.String(20), nullable=False, unique=True)
    issuer = db.Column(db.String(50), nullable=False)
    category = db.Column(SQLAlchemyEnum(CustomerCategory), nullable=False)
    annual_fee = db.Column(Numeric(8, 2), nullable=False, default=0)
    apr_range_min = db.Column(Numeric(5, 2), nullable=False)
    apr_range_max = db.Column(Numeric(5, 2), nullable=False)
    credit_limit_min = db.Column(Numeric(10, 2), nullable=False)
    credit_limit_max = db.Column(Numeric(10, 2), nullable=False)
    min_credit_score = db.Column(db.Integer, nullable=False)
    welcome_bonus = db.Column(db.Text)
    key_benefits = db.Column(db.JSON)
    reward_structure = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Bookings (External Service Bookings)
class Booking(db.Model):
    __tablename__ = 'booking'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(50), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'))
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'))
    service_type = db.Column(db.String(20), nullable=False)  # travel, hotel, shopping
    service_booking_id = db.Column(db.String(100))  # External service booking ID
    status = db.Column(SQLAlchemyEnum(BookingStatus), default=BookingStatus.CONFIRMED)
    booking_amount = db.Column(Numeric(10, 2), nullable=False)
    discount_amount = db.Column(Numeric(10, 2), default=0)
    final_amount = db.Column(Numeric(10, 2), nullable=False)
    booking_details = db.Column(db.JSON)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    service_date = db.Column(db.DateTime)
    cancellation_date = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)
    is_refundable = db.Column(db.Boolean, default=True)
    cancellation_fee = db.Column(Numeric(8, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='bookings')
    payment = db.relationship('Payment')
    offer = db.relationship('Offer')

# Refunds
class Refund(db.Model):
    __tablename__ = 'refund'
    
    id = db.Column(db.Integer, primary_key=True)
    refund_reference = db.Column(db.String(50), nullable=False, unique=True)
    original_payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    refund_type = db.Column(db.String(20), nullable=False)  # booking_cancellation, dispute_resolution, goodwill
    refund_amount = db.Column(Numeric(10, 2), nullable=False)
    processing_fee = db.Column(Numeric(8, 2), default=0)
    net_refund_amount = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(SQLAlchemyEnum(RefundStatus), default=RefundStatus.REQUESTED)
    reason = db.Column(db.Text)
    requested_date = db.Column(db.DateTime, default=datetime.utcnow)
    approved_date = db.Column(db.DateTime)
    processed_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    estimated_completion = db.Column(db.DateTime)
    
    # Relationships
    original_payment = db.relationship('Payment')
    booking = db.relationship('Booking')
    customer = db.relationship('Customer', backref='refunds')

# Transaction Disputes
class TransactionDispute(db.Model):
    __tablename__ = 'transaction_dispute'
    
    id = db.Column(db.Integer, primary_key=True)
    dispute_reference = db.Column(db.String(50), nullable=False, unique=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    category = db.Column(SQLAlchemyEnum(DisputeCategory), nullable=False)
    status = db.Column(SQLAlchemyEnum(DisputeStatus), default=DisputeStatus.OPEN)
    disputed_amount = db.Column(Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=False)
    customer_evidence = db.Column(db.JSON)
    merchant_response = db.Column(db.Text)
    resolution_notes = db.Column(db.Text)
    provisional_credit_amount = db.Column(Numeric(10, 2), default=0)
    final_resolution_amount = db.Column(Numeric(10, 2))
    filed_date = db.Column(db.DateTime, default=datetime.utcnow)
    response_due_date = db.Column(db.DateTime)
    resolved_date = db.Column(db.DateTime)
    assigned_agent = db.Column(db.String(100))
    
    # Relationships
    payment = db.relationship('Payment')
    customer = db.relationship('Customer', backref='disputes')
    merchant = db.relationship('Merchant', backref='disputes')

# Points Redemption Cancellations
class RedemptionCancellation(db.Model):
    __tablename__ = 'redemption_cancellation'
    
    id = db.Column(db.Integer, primary_key=True)
    cancellation_reference = db.Column(db.String(50), nullable=False, unique=True)
    original_reward_id = db.Column(db.Integer, db.ForeignKey('rewards.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    points_to_restore = db.Column(db.Integer, nullable=False)
    cancellation_fee_points = db.Column(db.Integer, default=0)
    net_points_restored = db.Column(db.Integer, nullable=False)
    cancellation_reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='PENDING')  # PENDING, APPROVED, DENIED, COMPLETED
    requested_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed_date = db.Column(db.DateTime)
    
    # Relationships
    original_reward = db.relationship('Reward')
    customer = db.relationship('Customer', backref='redemption_cancellations')

# Offer Terms and Conditions
class OfferTerms(db.Model):
    __tablename__ = 'offer_terms'
    
    id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    version = db.Column(db.String(10), nullable=False, default='1.0')
    terms_text = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.JSON)
    restrictions = db.Column(db.JSON)
    cancellation_policy = db.Column(db.Text)
    refund_policy = db.Column(db.Text)
    dispute_resolution = db.Column(db.Text)
    privacy_terms = db.Column(db.Text)
    effective_date = db.Column(db.DateTime, nullable=False)
    expiry_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    offer = db.relationship('Offer', backref='terms')
    merchant = db.relationship('Merchant', backref='offer_terms')

# Product-Specific Terms
class ProductTerms(db.Model):
    __tablename__ = 'product_terms'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('credit_card_product_details.id'), nullable=False)
    version = db.Column(db.String(10), nullable=False, default='1.0')
    cardholder_agreement = db.Column(db.Text, nullable=False)
    pricing_information = db.Column(db.JSON)
    rewards_terms = db.Column(db.Text)
    credit_terms = db.Column(db.JSON)
    fees_schedule = db.Column(db.JSON)
    dispute_procedures = db.Column(db.Text)
    privacy_policy = db.Column(db.Text)
    effective_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('CreditCardProductDetails', backref='terms')

# Aggregator Service Cache
class PriceComparison(db.Model):
    __tablename__ = 'price_comparison'
    
    id = db.Column(db.Integer, primary_key=True)
    search_hash = db.Column(db.String(64), nullable=False, unique=True)  # Hash of search criteria
    service_type = db.Column(db.String(20), nullable=False)  # travel, hotel, shopping
    search_criteria = db.Column(db.JSON, nullable=False)
    results = db.Column(db.JSON, nullable=False)
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_valid = db.Column(db.Boolean, default=True)
