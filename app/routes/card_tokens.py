from flask import Blueprint, request, jsonify
from app.models import db, CardToken, CreditCard, Customer
from datetime import datetime, timedelta
import logging
import random

token_bp = Blueprint('tokens', __name__)
logger = logging.getLogger(__name__)

def detect_card_type_from_number(card_number):
    """Detect card type based on card number patterns"""
    card_number = card_number.replace(' ', '').replace('-', '')

    if card_number.startswith('4'):
        return 'VISA'
    elif card_number.startswith(('51', '52', '53', '54', '55')) or card_number.startswith(('2221', '2222', '2223', '2224', '2225', '2226', '2227', '2228', '2229', '223', '224', '225', '226', '227', '228', '229', '23', '24', '25', '26', '270', '271', '2720')):
        return 'MASTERCARD'
    elif card_number.startswith(('34', '37')):
        return 'AMERICAN_EXPRESS'
    elif card_number.startswith(('6011', '622', '64', '65')):
        return 'DISCOVER'
    else:
        return 'VISA'  # Default fallback

def generate_format_preserving_token(card_number):
    """Generate a format-preserving token that maintains the same format as the original card number"""
    # Keep first 6 digits (BIN) and last 4 digits, tokenize the middle 6 digits
    first_six = card_number[:6]
    last_four = card_number[-4:]

    # Generate random 6 digits for middle section
    middle_six = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    # Ensure the token doesn't match the original card number
    token = first_six + middle_six + last_four
    while token == card_number:
        middle_six = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        token = first_six + middle_six + last_four

    return token

@token_bp.route('/api/tokens/create', methods=['POST'])
def create_token():
    """Create a new token for a credit card"""
    try:
        logger.info("POST /api/tokens/create - Create token request received")
        data = request.get_json()
        logger.debug(f"Token creation data: {data}")

        # Validation
        required_fields = ['card_id', 'customer_id']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return jsonify({'error': f'{field} is required'}), 400

        card_id = data['card_id']
        customer_id = data['customer_id']

        # Verify card exists and belongs to customer
        credit_card = CreditCard.query.filter_by(id=card_id, customer_id=customer_id).first()
        if not credit_card:
            logger.warning(f"Credit card {card_id} not found for customer {customer_id}")
            return jsonify({'error': 'Credit card not found or does not belong to customer'}), 404

        # Check if customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            logger.warning(f"Customer {customer_id} not found")
            return jsonify({'error': 'Customer not found'}), 404

        # Generate format-preserving token
        token_id = generate_format_preserving_token(credit_card.card_number)

        # Ensure token is unique
        while CardToken.query.filter_by(token_id=token_id).first():
            token_id = generate_format_preserving_token(credit_card.card_number)

        # Set expiration date (optional, defaults to 2 years)
        expires_at = None
        if 'expires_in_days' in data:
            expires_at = datetime.utcnow() + timedelta(days=data['expires_in_days'])
        else:
            expires_at = datetime.utcnow() + timedelta(days=730)  # 2 years default

        # Create token record
        card_token = CardToken(
            token_id=token_id,
            card_id=card_id,
            customer_id=customer_id,
            expires_at=expires_at,
            is_active=True
        )

        db.session.add(card_token)
        db.session.commit()

        logger.info(f"Token {token_id} created successfully for card {card_id}")

        # Return token with card details
        response = {
            'success': True,
            'token': card_token.to_dict(),
            'card_details': credit_card.to_dict_with_token(token_id)
        }

        return jsonify(response), 201

    except Exception as e:
        logger.error(f"Error creating token: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@token_bp.route('/api/tokens/<token_id>', methods=['GET'])
def get_token_details(token_id):
    """Get token details and associated card information"""
    try:
        logger.info(f"GET /api/tokens/{token_id} - Get token details request")

        # Find token
        card_token = CardToken.query.filter_by(token_id=token_id, is_active=True).first()
        if not card_token:
            logger.warning(f"Token {token_id} not found or inactive")
            return jsonify({'error': 'Token not found or inactive'}), 404

        # Check if token is expired
        if card_token.expires_at and datetime.utcnow() > card_token.expires_at:
            logger.warning(f"Token {token_id} has expired")
            card_token.is_active = False
            db.session.commit()
            return jsonify({'error': 'Token has expired'}), 410

        # Update last used timestamp
        card_token.last_used = datetime.utcnow()
        db.session.commit()

        # Get associated card details
        credit_card = card_token.credit_card

        response = {
            'token': card_token.to_dict(),
            'card_details': credit_card.to_dict_with_token(token_id)
        }

        logger.info(f"Token {token_id} details retrieved successfully")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error retrieving token details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@token_bp.route('/api/tokens/customer/<int:customer_id>', methods=['GET'])
def get_customer_tokens(customer_id):
    """Get all active tokens for a customer"""
    try:
        logger.info(f"GET /api/tokens/customer/{customer_id} - Get customer tokens request")

        # Verify customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            logger.warning(f"Customer {customer_id} not found")
            return jsonify({'error': 'Customer not found'}), 404

        # Get all active tokens for customer
        active_tokens = CardToken.query.filter_by(customer_id=customer_id, is_active=True).all()

        # Filter out expired tokens
        valid_tokens = []
        current_time = datetime.utcnow()

        for token in active_tokens:
            if token.expires_at and current_time > token.expires_at:
                # Mark expired tokens as inactive
                token.is_active = False
                continue
            valid_tokens.append(token)

        db.session.commit()

        # Prepare response with card details for each token
        tokens_with_cards = []
        for token in valid_tokens:
            credit_card = token.credit_card
            tokens_with_cards.append({
                'token': token.to_dict(),
                'card_details': credit_card.to_dict_with_token(token.token_id)
            })

        response = {
            'customer_id': customer_id,
            'customer_name': f"{customer.first_name} {customer.last_name}",
            'tokens': tokens_with_cards,
            'total_tokens': len(valid_tokens)
        }

        logger.info(f"Retrieved {len(valid_tokens)} active tokens for customer {customer_id}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error retrieving customer tokens: {str(e)}")
        return jsonify({'error': str(e)}), 500

@token_bp.route('/api/tokens/<token_id>/deactivate', methods=['PUT'])
def deactivate_token(token_id):
    """Deactivate a token"""
    try:
        logger.info(f"PUT /api/tokens/{token_id}/deactivate - Deactivate token request")

        # Find token
        card_token = CardToken.query.filter_by(token_id=token_id).first()
        if not card_token:
            logger.warning(f"Token {token_id} not found")
            return jsonify({'error': 'Token not found'}), 404

        # Deactivate token
        card_token.is_active = False
        db.session.commit()

        logger.info(f"Token {token_id} deactivated successfully")
        return jsonify({
            'success': True,
            'message': 'Token deactivated successfully',
            'token': card_token.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error deactivating token: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@token_bp.route('/api/tokens/card/<int:card_id>/tokens', methods=['GET'])
def get_card_tokens(card_id):
    """Get all tokens for a specific card"""
    try:
        logger.info(f"GET /api/tokens/card/{card_id}/tokens - Get card tokens request")

        # Verify card exists
        credit_card = CreditCard.query.get(card_id)
        if not credit_card:
            logger.warning(f"Credit card {card_id} not found")
            return jsonify({'error': 'Credit card not found'}), 404

        # Get all tokens for the card
        card_tokens = CardToken.query.filter_by(card_id=card_id).order_by(CardToken.created_at.desc()).all()

        # Prepare response
        tokens_data = []
        for token in card_tokens:
            token_data = token.to_dict()
            # Add status based on expiration and active flag
            if not token.is_active:
                token_data['status'] = 'DEACTIVATED'
            elif token.expires_at and datetime.utcnow() > token.expires_at:
                token_data['status'] = 'EXPIRED'
            else:
                token_data['status'] = 'ACTIVE'
            tokens_data.append(token_data)

        response = {
            'card_id': card_id,
            'card_details': credit_card.to_dict_with_token(),
            'tokens': tokens_data,
            'total_tokens': len(tokens_data)
        }

        logger.info(f"Retrieved {len(tokens_data)} tokens for card {card_id}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error retrieving card tokens: {str(e)}")
        return jsonify({'error': str(e)}), 500

@token_bp.route('/api/tokens/<token_id>/validate', methods=['POST'])
def validate_token(token_id):
    """Validate a token and return card details if valid"""
    try:
        logger.info(f"POST /api/tokens/{token_id}/validate - Validate token request")

        # Find token
        card_token = CardToken.query.filter_by(token_id=token_id, is_active=True).first()
        if not card_token:
            logger.warning(f"Token {token_id} not found or inactive")
            return jsonify({
                'valid': False,
                'error': 'Token not found or inactive'
            }), 404

        # Check if token is expired
        if card_token.expires_at and datetime.utcnow() > card_token.expires_at:
            logger.warning(f"Token {token_id} has expired")
            card_token.is_active = False
            db.session.commit()
            return jsonify({
                'valid': False,
                'error': 'Token has expired'
            }), 410

        # Update last used timestamp
        card_token.last_used = datetime.utcnow()
        db.session.commit()

        # Get associated card details
        credit_card = card_token.credit_card

        response = {
            'valid': True,
            'token': card_token.to_dict(),
            'card_details': credit_card.to_dict_with_token(token_id)
        }

        logger.info(f"Token {token_id} validated successfully")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        return jsonify({'error': str(e)}), 500
