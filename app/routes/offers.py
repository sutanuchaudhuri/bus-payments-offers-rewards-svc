from flask import Blueprint, request, jsonify
from app.models import db, Offer, Customer, CustomerOffer, OfferCategory
from datetime import datetime, timedelta
from decimal import Decimal
import logging

offer_bp = Blueprint('offers', __name__)
logger = logging.getLogger(__name__)

@offer_bp.route('', methods=['GET'])
def get_offers():
    """Get all offers with filtering options - customer_id is required"""
    try:
        logger.info("GET /api/offers - Request received")

        # customer_id is now required
        customer_id = request.args.get('customer_id', type=int)
        if not customer_id:
            logger.warning("Missing required customer_id parameter")
            return jsonify({'error': 'customer_id is required'}), 400

        # Verify customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            logger.warning(f"Customer {customer_id} not found")
            return jsonify({'error': f'Customer with ID {customer_id} not found'}), 404

        # Query parameters - all optional except customer_id
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        merchant_id = request.args.get('merchant_id', type=int)
        is_active = request.args.get('is_active', type=bool)

        logger.debug(f"Request parameters - page: {page}, per_page: {per_page}, category: {category}, merchant_id: {merchant_id}, is_active: {is_active}, customer_id: {customer_id}")

        # Build query
        query = Offer.query

        if category:
            try:
                offer_category = OfferCategory(category.upper())
                query = query.filter(Offer.category == offer_category)
                logger.debug(f"Filtering offers by category: {category}")
            except ValueError:
                valid_categories = [c.value for c in OfferCategory]
                logger.warning(f"Invalid category: {category}")
                return jsonify({'error': f'Invalid category. Valid categories: {valid_categories}'}), 400

        if merchant_id:
            query = query.filter(Offer.merchant_id == merchant_id)
            logger.debug(f"Filtering offers by merchant_id: {merchant_id}")

        if is_active is not None:
            current_date = datetime.utcnow()
            if is_active:
                query = query.filter(
                    Offer.start_date <= current_date,
                    Offer.expiry_date >= current_date
                )
                logger.debug("Filtering for active offers only")
            else:
                query = query.filter(
                    (Offer.start_date > current_date) | (Offer.expiry_date < current_date)
                )
                logger.debug("Filtering for inactive offers only")

        offers = query.paginate(page=page, per_page=per_page, error_out=False)

        logger.info(f"Retrieved {offers.total} offers, showing page {page}")

        offers_data = []
        for offer in offers.items:
            offer_dict = offer.to_dict()

            # Add customer-specific data since customer_id is required
            customer_offer = CustomerOffer.query.filter_by(
                customer_id=customer_id,
                offer_id=offer.id
            ).first()

            offer_dict['customer_activated'] = customer_offer is not None
            offer_dict['customer_id'] = customer_id
            if customer_offer:
                offer_dict['activation_date'] = customer_offer.activation_date.isoformat()
                offer_dict['used_count'] = customer_offer.used_count
                offer_dict['total_savings'] = float(customer_offer.total_savings)
            else:
                offer_dict['activation_date'] = None
                offer_dict['used_count'] = 0
                offer_dict['total_savings'] = 0.0

            offers_data.append(offer_dict)

        return jsonify({
            'offers': offers_data,
            'total': offers.total,
            'pages': offers.pages,
            'current_page': page,
            'per_page': per_page,
            'customer_id': customer_id
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving offers: {str(e)}")
        return jsonify({'error': 'Failed to retrieve offers'}), 500

@offer_bp.route('/<int:offer_id>', methods=['GET'])
def get_offer(offer_id):
    """Get a specific offer by ID - customer_id is required"""
    try:
        logger.info(f"GET /api/offers/{offer_id} - Request received")

        # Check if offer_id is valid
        if offer_id <= 0:
            logger.warning(f"Invalid offer ID: {offer_id}")
            return jsonify({'error': 'Invalid offer ID. Must be greater than 0'}), 400

        offer = Offer.query.get(offer_id)
        if not offer:
            logger.warning(f"Offer {offer_id} not found")
            return jsonify({'error': f'Offer with ID {offer_id} not found'}), 404

        # customer_id is now required
        customer_id = request.args.get('customer_id', type=int)
        if not customer_id:
            logger.warning("Missing required customer_id parameter")
            return jsonify({'error': 'customer_id is required'}), 400

        # Verify customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            logger.warning(f"Customer {customer_id} not found")
            return jsonify({'error': f'Customer with ID {customer_id} not found'}), 404

        offer_data = offer.to_dict()

        # Add activation statistics
        total_activations = CustomerOffer.query.filter_by(offer_id=offer_id).count()
        active_activations = CustomerOffer.query.filter_by(
            offer_id=offer_id,
            is_active=True
        ).count()

        offer_data['statistics'] = {
            'total_activations': total_activations,
            'active_activations': active_activations
        }

        # Add customer-specific data since customer_id is required
        customer_offer = CustomerOffer.query.filter_by(
            customer_id=customer_id,
            offer_id=offer.id
        ).first()

        offer_data['customer_activated'] = customer_offer is not None
        offer_data['customer_id'] = customer_id
        if customer_offer:
            offer_data['activation_date'] = customer_offer.activation_date.isoformat()
            offer_data['used_count'] = customer_offer.used_count
            offer_data['total_savings'] = float(customer_offer.total_savings)
        else:
            offer_data['activation_date'] = None
            offer_data['used_count'] = 0
            offer_data['total_savings'] = 0.0

        logger.info(f"Retrieved offer {offer_id} successfully for customer {customer_id}")
        return jsonify(offer_data), 200

    except Exception as e:
        logger.error(f"Error retrieving offer {offer_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@offer_bp.route('', methods=['POST'])
def create_offer():
    """Create a new offer"""
    try:
        logger.info("POST /api/offers - Create offer request received")
        data = request.get_json()
        logger.debug(f"Offer data received: {data}")

        # Validation
        required_fields = ['title', 'category', 'start_date', 'expiry_date']
        for field in required_fields:
            if field not in data or not data[field]:
                logger.warning(f"Missing required field: {field}")
                return jsonify({'error': f'{field} is required'}), 400

        # Validate category
        try:
            category = OfferCategory(data['category'].upper())
        except ValueError:
            valid_categories = [c.value for c in OfferCategory]
            logger.warning(f"Invalid category: {data['category']}")
            return jsonify({'error': f'Invalid category. Valid categories: {valid_categories}'}), 400

        # Parse dates
        try:
            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
        except ValueError:
            logger.warning(f"Invalid date format in request")
            return jsonify({'error': 'Invalid date format. Use ISO format'}), 400

        if expiry_date <= start_date:
            logger.warning(f"Invalid date range: expiry_date <= start_date")
            return jsonify({'error': 'Expiry date must be after start date'}), 400

        # Validate numeric fields
        discount_percentage = None
        if 'discount_percentage' in data and data['discount_percentage']:
            discount_percentage = Decimal(str(data['discount_percentage']))
            if discount_percentage <= 0 or discount_percentage > 100:
                logger.warning(f"Invalid discount percentage: {discount_percentage}")
                return jsonify({'error': 'Discount percentage must be between 0 and 100'}), 400

        max_discount_amount = None
        if 'max_discount_amount' in data and data['max_discount_amount']:
            max_discount_amount = Decimal(str(data['max_discount_amount']))
            if max_discount_amount <= 0:
                logger.warning(f"Invalid max discount amount: {max_discount_amount}")
                return jsonify({'error': 'Max discount amount must be positive'}), 400

        min_transaction_amount = None
        if 'min_transaction_amount' in data and data['min_transaction_amount']:
            min_transaction_amount = Decimal(str(data['min_transaction_amount']))
            if min_transaction_amount <= 0:
                logger.warning(f"Invalid min transaction amount: {min_transaction_amount}")
                return jsonify({'error': 'Min transaction amount must be positive'}), 400

        # Create offer
        offer = Offer(
            title=data['title'],
            description=data.get('description'),
            category=category,
            merchant_name=data.get('merchant_name'),
            discount_percentage=discount_percentage,
            max_discount_amount=max_discount_amount,
            min_transaction_amount=min_transaction_amount,
            reward_points=data.get('reward_points', 0),
            start_date=start_date,
            expiry_date=expiry_date,
            terms_and_conditions=data.get('terms_and_conditions'),
            is_active=data.get('is_active', True),
            max_usage_per_customer=data.get('max_usage_per_customer', 1)
        )

        db.session.add(offer)
        db.session.commit()

        logger.info(f"Offer created successfully with ID: {offer.id}")
        return jsonify(offer.to_dict()), 201

    except Exception as e:
        logger.error(f"Error creating offer: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@offer_bp.route('/<int:offer_id>', methods=['PUT'])
def update_offer(offer_id):
    """Update an existing offer"""
    try:
        logger.info(f"PUT /api/offers/{offer_id} - Update offer request received")
        offer = Offer.query.get_or_404(offer_id)
        data = request.get_json()
        logger.debug(f"Update data received: {data}")

        # Validate category if provided
        if 'category' in data:
            try:
                category = OfferCategory(data['category'].upper())
                offer.category = category
            except ValueError:
                valid_categories = [c.value for c in OfferCategory]
                logger.warning(f"Invalid category: {data['category']}")
                return jsonify({'error': f'Invalid category. Valid categories: {valid_categories}'}), 400

        # Parse dates if provided
        if 'start_date' in data:
            try:
                offer.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Invalid start_date format")
                return jsonify({'error': 'Invalid start_date format. Use ISO format'}), 400

        if 'expiry_date' in data:
            try:
                offer.expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Invalid expiry_date format")
                return jsonify({'error': 'Invalid expiry_date format. Use ISO format'}), 400

        # Validate date range if both dates are being updated
        if offer.expiry_date <= offer.start_date:
            logger.warning(f"Invalid date range: expiry_date <= start_date")
            return jsonify({'error': 'Expiry date must be after start date'}), 400

        # Update other fields
        if 'title' in data:
            offer.title = data['title']
        if 'description' in data:
            offer.description = data['description']
        if 'merchant_id' in data:
            offer.merchant_id = data['merchant_id']
        if 'merchant_name' in data:
            offer.merchant_name = data['merchant_name']

        # Validate and update numeric fields
        if 'discount_percentage' in data and data['discount_percentage'] is not None:
            discount_percentage = Decimal(str(data['discount_percentage']))
            if discount_percentage <= 0 or discount_percentage > 100:
                return jsonify({'error': 'Discount percentage must be between 0 and 100'}), 400
            offer.discount_percentage = discount_percentage

        if 'max_discount_amount' in data and data['max_discount_amount'] is not None:
            max_discount_amount = Decimal(str(data['max_discount_amount']))
            if max_discount_amount <= 0:
                return jsonify({'error': 'Max discount amount must be positive'}), 400
            offer.max_discount_amount = max_discount_amount

        if 'min_transaction_amount' in data and data['min_transaction_amount'] is not None:
            min_transaction_amount = Decimal(str(data['min_transaction_amount']))
            if min_transaction_amount <= 0:
                return jsonify({'error': 'Min transaction amount must be positive'}), 400
            offer.min_transaction_amount = min_transaction_amount

        if 'reward_points' in data:
            offer.reward_points = data['reward_points']
        if 'terms_and_conditions' in data:
            offer.terms_and_conditions = data['terms_and_conditions']
        if 'is_active' in data:
            offer.is_active = data['is_active']
        if 'max_usage_per_customer' in data:
            offer.max_usage_per_customer = data['max_usage_per_customer']

        db.session.commit()
        logger.info(f"Offer {offer_id} updated successfully")
        return jsonify(offer.to_dict()), 200

    except Exception as e:
        logger.error(f"Error updating offer {offer_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@offer_bp.route('/<int:offer_id>', methods=['DELETE'])
def delete_offer(offer_id):
    """Delete an offer"""
    try:
        logger.info(f"DELETE /api/offers/{offer_id} - Delete offer request received")
        offer = Offer.query.get_or_404(offer_id)

        # Check if offer has active customer activations
        active_activations = CustomerOffer.query.filter_by(
            offer_id=offer_id,
            is_active=True
        ).count()

        if active_activations > 0:
            logger.warning(f"Cannot delete offer {offer_id} - has {active_activations} active customer activations")
            return jsonify({'error': 'Cannot delete offer with active customer activations. Deactivate the offer instead.'}), 400

        # Delete all customer offer records first (cascade)
        CustomerOffer.query.filter_by(offer_id=offer_id).delete()

        # Delete the offer
        db.session.delete(offer)
        db.session.commit()

        logger.info(f"Offer {offer_id} deleted successfully")
        return jsonify({'message': 'Offer deleted successfully'}), 200

    except Exception as e:
        logger.error(f"Error deleting offer {offer_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@offer_bp.route('/<int:offer_id>/activate', methods=['POST'])
def activate_offer_for_customer(offer_id):
    """Activate an offer for a customer"""
    try:
        logger.info(f"POST /api/offers/{offer_id}/activate - Activate offer request received")
        offer = Offer.query.get_or_404(offer_id)
        data = request.get_json()
        logger.debug(f"Activation data received: {data}")

        if 'customer_id' not in data:
            logger.warning("Missing customer_id in activation request")
            return jsonify({'error': 'customer_id is required'}), 400

        customer_id = data['customer_id']
        customer = Customer.query.get_or_404(customer_id)

        # Check if offer is active and valid
        now = datetime.utcnow()
        if not offer.is_active:
            logger.warning(f"Offer {offer_id} is not active")
            return jsonify({'error': 'Offer is not active'}), 400

        if now < offer.start_date:
            logger.warning(f"Offer {offer_id} has not started yet")
            return jsonify({'error': 'Offer has not started yet'}), 400

        if now > offer.expiry_date:
            logger.warning(f"Offer {offer_id} has expired")
            return jsonify({'error': 'Offer has expired'}), 400

        # Check if customer has already activated this offer
        existing_activation = CustomerOffer.query.filter_by(
            customer_id=customer_id,
            offer_id=offer.id
        ).first()

        if existing_activation:
            if existing_activation.is_active:
                logger.warning(f"Offer {offer_id} already activated for customer {customer_id}")
                return jsonify({'error': 'Offer already activated for this customer'}), 409
            else:
                # Reactivate the existing record
                existing_activation.is_active = True
                existing_activation.activation_date = now
                db.session.commit()
                logger.info(f"Offer {offer_id} reactivated for customer {customer_id}")
                return jsonify(existing_activation.to_dict()), 200

        # Create new activation
        customer_offer = CustomerOffer(
            customer_id=customer_id,
            offer_id=offer.id,
            activation_date=now,
            usage_count=0,
            total_savings=Decimal('0.00'),
            is_active=True
        )

        db.session.add(customer_offer)
        db.session.commit()

        logger.info(f"Offer {offer_id} activated successfully for customer {customer_id}")
        return jsonify(customer_offer.to_dict()), 201

    except Exception as e:
        logger.error(f"Error activating offer: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@offer_bp.route('/categories', methods=['GET'])
def get_offer_categories():
    """Get all available offer categories - customer_id is required"""
    try:
        logger.info("GET /api/offers/categories - Request received")

        # customer_id is now required for consistency
        customer_id = request.args.get('customer_id', type=int)
        if not customer_id:
            logger.warning("Missing required customer_id parameter")
            return jsonify({'error': 'customer_id is required'}), 400

        # Verify customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            logger.warning(f"Customer {customer_id} not found")
            return jsonify({'error': f'Customer with ID {customer_id} not found'}), 404

        categories = [
            {
                'name': category.name,
                'value': category.value,
                'description': {
                    'TRAVEL': 'Travel and transportation related offers',
                    'MERCHANT': 'Merchant-specific offers',
                    'CASHBACK': 'Cashback offers',
                    'DINING': 'Restaurant and dining offers',
                    'FUEL': 'Fuel and gas station offers',
                    'SHOPPING': 'Shopping and retail offers'
                }.get(category.name, 'General offer category')
            }
            for category in OfferCategory
        ]

        logger.info(f"Retrieved {len(categories)} offer categories for customer {customer_id}")
        return jsonify({
            'categories': categories,
            'customer_id': customer_id
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving offer categories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@offer_bp.route('/<int:offer_id>/deactivate', methods=['POST'])
def deactivate_offer(offer_id):
    """Deactivate an offer"""
    try:
        logger.info(f"POST /api/offers/{offer_id}/deactivate - Deactivate offer request received")
        offer = Offer.query.get_or_404(offer_id)

        if not offer.is_active:
            logger.warning(f"Offer {offer_id} is already inactive")
            return jsonify({'error': 'Offer is already inactive'}), 400

        offer.is_active = False
        db.session.commit()

        logger.info(f"Offer {offer_id} deactivated successfully")
        return jsonify({
            'message': 'Offer deactivated successfully',
            'offer': offer.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error deactivating offer {offer_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@offer_bp.route('/<int:offer_id>/reactivate', methods=['POST'])
def reactivate_offer(offer_id):
    """Reactivate an offer"""
    try:
        logger.info(f"POST /api/offers/{offer_id}/reactivate - Reactivate offer request received")
        offer = Offer.query.get_or_404(offer_id)

        if offer.is_active:
            logger.warning(f"Offer {offer_id} is already active")
            return jsonify({'error': 'Offer is already active'}), 400

        # Check if offer hasn't expired
        current_date = datetime.utcnow()
        if current_date > offer.expiry_date:
            logger.warning(f"Cannot reactivate expired offer {offer_id}")
            return jsonify({'error': 'Cannot reactivate expired offer'}), 400

        offer.is_active = True
        db.session.commit()

        logger.info(f"Offer {offer_id} reactivated successfully")
        return jsonify({
            'message': 'Offer reactivated successfully',
            'offer': offer.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error reactivating offer {offer_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@offer_bp.route('/<int:offer_id>/expire', methods=['POST'])
def expire_offer(offer_id):
    """Manually expire an offer by setting its expiry date to now"""
    try:
        logger.info(f"POST /api/offers/{offer_id}/expire - Expire offer request received")
        offer = Offer.query.get_or_404(offer_id)

        current_date = datetime.utcnow()
        if offer.expiry_date <= current_date:
            logger.warning(f"Offer {offer_id} is already expired")
            return jsonify({'error': 'Offer is already expired'}), 400

        # Set expiry date to current time to expire the offer
        offer.expiry_date = current_date
        offer.is_active = False  # Also deactivate it
        db.session.commit()

        logger.info(f"Offer {offer_id} expired successfully")
        return jsonify({
            'message': 'Offer expired successfully',
            'offer': offer.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error expiring offer {offer_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
