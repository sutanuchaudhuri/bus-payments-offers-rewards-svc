from flask import Blueprint, request, jsonify
from app.models import db, Customer, CreditCard, CardType, CreditCardProduct
from datetime import datetime, timezone
import logging
from sqlalchemy import func

customer_bp = Blueprint('customers', __name__)
logger = logging.getLogger(__name__)

@customer_bp.route('', methods=['GET'])
def list_customers():
    """Get all customers with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        customers = Customer.query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'customers': [customer.to_dict() for customer in customers.items],
            'total': customers.total,
            'pages': customers.pages,
            'current_page': page
        })

    except Exception as e:
        logger.error(f"Error listing customers: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@customer_bp.route('', methods=['POST'])
def create_customer():
    """Create a new customer"""
    try:
        data = request.get_json()

        # Validation
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400

        # Check if email already exists
        existing_customer = Customer.query.filter_by(email=data['email']).first()
        if existing_customer:
            return jsonify({'error': 'Email already exists'}), 409

        # Create new customer
        customer = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            address=data.get('address')
        )

        db.session.add(customer)
        db.session.commit()

        logger.info(f"Customer created successfully: {customer.id}")
        return jsonify({
            'message': 'Customer created successfully',
            'customer': customer.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        logger.error(f"Error creating customer: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@customer_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get customer details by ID"""
    try:
        customer = Customer.query.get_or_404(customer_id)

        # Include credit cards in response
        customer_data = customer.to_dict()
        customer_data['credit_cards'] = [
            {
                'id': card.id,
                'masked_number': f"****-****-****-{card.card_number[-4:]}",
                'card_holder_name': card.card_holder_name,
                'expiry_month': card.expiry_month,
                'expiry_year': card.expiry_year,
                'product_type': card.product_type.value,
                'card_type': card.card_type.value,
                'is_active': card.is_active
            }
            for card in customer.credit_cards
        ]

        return jsonify(customer_data)

    except Exception as e:
        logger.error(f"Error getting customer {customer_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@customer_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update customer details"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()

        # Update allowed fields
        updateable_fields = ['first_name', 'last_name', 'phone', 'address', 'date_of_birth']
        for field in updateable_fields:
            if field in data:
                if field == 'date_of_birth' and data[field]:
                    setattr(customer, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                else:
                    setattr(customer, field, data[field])

        # Update email if provided and not duplicate
        if 'email' in data and data['email'] != customer.email:
            existing_customer = Customer.query.filter_by(email=data['email']).first()
            if existing_customer:
                return jsonify({'error': 'Email already exists'}), 409
            customer.email = data['email']

        customer.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        logger.info(f"Customer {customer_id} updated successfully")
        return jsonify({
            'message': 'Customer updated successfully',
            'customer': customer.to_dict()
        })

    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        logger.error(f"Error updating customer {customer_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@customer_bp.route('/<int:customer_id>/credit-cards', methods=['GET'])
def get_customer_credit_cards(customer_id):
    """Get all credit cards for a customer"""
    try:
        customer = Customer.query.get_or_404(customer_id)

        credit_cards = [
            {
                'id': card.id,
                'masked_number': f"****-****-****-{card.card_number[-4:]}",
                'card_holder_name': card.card_holder_name,
                'expiry_month': card.expiry_month,
                'expiry_year': card.expiry_year,
                'product_type': card.product_type.value if card.product_type else None,
                'card_type': card.card_type.value if card.card_type else None,
                'credit_limit': float(card.credit_limit) if card.credit_limit else 0,
                'available_credit': float(card.available_credit) if card.available_credit else 0,
                'is_active': card.is_active,
                'created_at': card.created_at.isoformat() if card.created_at else None,
                'updated_at': card.updated_at.isoformat() if card.updated_at else None
            }
            for card in customer.credit_cards
        ]

        logger.info(f"Retrieved {len(credit_cards)} credit cards for customer {customer_id}")
        return jsonify({
            'customer_id': customer_id,
            'credit_cards': credit_cards,
            'total_cards': len(credit_cards)
        })

    except Exception as e:
        logger.error(f"Error getting credit cards for customer {customer_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@customer_bp.route('/<int:customer_id>/credit-cards', methods=['POST'])
def add_credit_card(customer_id):
    """Add a credit card to customer"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()

        # Validation
        required_fields = ['card_number', 'card_holder_name', 'expiry_month', 'expiry_year', 'product_type', 'card_type', 'credit_limit']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400

        # Validate card number uniqueness
        existing_card = CreditCard.query.filter_by(card_number=data['card_number']).first()
        if existing_card:
            return jsonify({'error': 'Card number already exists'}), 409

        # Validate enum values
        try:
            product_type = CreditCardProduct(data['product_type'])
            card_type = CardType(data['card_type'])
        except ValueError as e:
            return jsonify({'error': f'Invalid enum value: {str(e)}'}), 400

        # Create credit card
        credit_card = CreditCard(
            customer_id=customer_id,
            card_number=data['card_number'],
            card_holder_name=data['card_holder_name'],
            expiry_month=data['expiry_month'],
            expiry_year=data['expiry_year'],
            product_type=product_type,
            card_type=card_type,
            credit_limit=data['credit_limit'],
            available_credit=data.get('available_credit', data['credit_limit'])
        )

        db.session.add(credit_card)
        db.session.commit()

        logger.info(f"Credit card added to customer {customer_id}")
        return jsonify({
            'message': 'Credit card added successfully',
            'credit_card': credit_card.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Error adding credit card to customer {customer_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@customer_bp.route('/<int:customer_id>/stats', methods=['GET'])
def get_customer_stats(customer_id):
    """Get customer statistics"""
    try:
        customer = Customer.query.get_or_404(customer_id)

        # Get payment statistics
        from app.models import Payment, Reward

        total_payments = db.session.query(func.count(Payment.id)).join(CreditCard).filter(
            CreditCard.customer_id == customer_id
        ).scalar() or 0

        total_spent = db.session.query(func.sum(Payment.amount)).join(CreditCard).filter(
            CreditCard.customer_id == customer_id
        ).scalar() or 0

        total_rewards = db.session.query(func.sum(Reward.points_earned)).filter(
            Reward.customer_id == customer_id
        ).scalar() or 0

        available_rewards = db.session.query(func.sum(Reward.points_earned - Reward.points_redeemed)).filter(
            Reward.customer_id == customer_id
        ).scalar() or 0

        return jsonify({
            'customer_id': customer_id,
            'total_payments': total_payments,
            'total_spent': float(total_spent) if total_spent else 0,
            'total_rewards_earned': total_rewards,
            'available_rewards': available_rewards,
            'credit_cards_count': len(customer.credit_cards)
        })

    except Exception as e:
        logger.error(f"Error getting customer stats {customer_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
