from flask import Blueprint, request, jsonify
from app.models import db, Merchant, MerchantCategory, MerchantOfferHistory, CustomerProfileHistory, Offer
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from sqlalchemy import func, or_

merchant_bp = Blueprint('merchants', __name__)
logger = logging.getLogger(__name__)

@merchant_bp.route('', methods=['GET'])
def get_merchants():
    """Get all merchants with filtering options"""
    try:
        logger.info("GET /api/merchants - Request received")
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        name = request.args.get('name')
        is_active = request.args.get('is_active', type=bool)
        
        logger.debug(f"Request parameters - page: {page}, per_page: {per_page}, category: {category}, name: {name}, is_active: {is_active}")

        # Build query
        query = Merchant.query
        
        if category:
            try:
                merchant_category = MerchantCategory(category.upper())
                query = query.filter(Merchant.category == merchant_category)
                logger.debug(f"Filtering merchants by category: {category}")
            except ValueError:
                valid_categories = [c.value for c in MerchantCategory]
                logger.warning(f"Invalid category: {category}")
                return jsonify({'error': f'Invalid category. Valid categories: {valid_categories}'}), 400
        
        if name:
            query = query.filter(Merchant.name.ilike(f'%{name}%'))
            logger.debug(f"Filtering merchants by name: {name}")

        if is_active is not None:
            query = query.filter(Merchant.is_active == is_active)
            logger.debug(f"Filtering merchants by is_active: {is_active}")

        merchants = query.paginate(page=page, per_page=per_page, error_out=False)

        logger.info(f"Retrieved {merchants.total} merchants, showing page {page}")

        return jsonify({
            'merchants': [merchant.to_dict() for merchant in merchants.items],
            'total': merchants.total,
            'pages': merchants.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving merchants: {str(e)}")
        return jsonify({'error': 'Failed to retrieve merchants'}), 500

@merchant_bp.route('/<int:merchant_id>', methods=['GET'])
def get_merchant(merchant_id):
    """Get a specific merchant by ID"""
    try:
        merchant = Merchant.query.get_or_404(merchant_id)
        
        merchant_data = merchant.to_dict()
        
        # Add related offers
        offers = Offer.query.filter_by(merchant_id=merchant_id).all()
        merchant_data['offers'] = [offer.to_dict() for offer in offers]
        
        # Add usage statistics
        total_transactions = MerchantOfferHistory.query.filter_by(merchant_id=merchant_id).count()
        total_discount_given = db.session.query(
            func.sum(MerchantOfferHistory.discount_applied)
        ).filter(MerchantOfferHistory.merchant_id == merchant_id).scalar() or 0
        
        merchant_data['statistics'] = {
            'total_transactions': total_transactions,
            'total_discount_given': float(total_discount_given),
            'active_offers': len([o for o in offers if o.is_active]),
            'total_offers': len(offers)
        }
        
        return jsonify(merchant_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@merchant_bp.route('', methods=['POST'])
def create_merchant():
    """Create a new merchant"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['merchant_id', 'name', 'category']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if merchant_id already exists
        if Merchant.query.filter_by(merchant_id=data['merchant_id']).first():
            return jsonify({'error': 'Merchant ID already exists'}), 409
        
        # Validate category
        try:
            category = MerchantCategory(data['category'].upper())
        except ValueError:
            valid_categories = [c.value for c in MerchantCategory]
            return jsonify({'error': f'Invalid category. Valid categories: {valid_categories}'}), 400
        
        # Create merchant
        merchant = Merchant(
            merchant_id=data['merchant_id'],
            name=data['name'],
            description=data.get('description'),
            category=category,
            website=data.get('website'),
            contact_email=data.get('contact_email'),
            phone=data.get('phone'),
            address=data.get('address'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(merchant)
        db.session.commit()
        
        return jsonify(merchant.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@merchant_bp.route('/<int:merchant_id>', methods=['PUT'])
def update_merchant(merchant_id):
    """Update an existing merchant"""
    try:
        merchant = Merchant.query.get_or_404(merchant_id)
        data = request.get_json()
        
        # Validate category if provided
        if 'category' in data and data['category']:
            try:
                category = MerchantCategory(data['category'].upper())
                merchant.category = category
            except ValueError:
                valid_categories = [c.value for c in MerchantCategory]
                return jsonify({'error': f'Invalid category. Valid categories: {valid_categories}'}), 400
        
        # Check merchant_id uniqueness if updating
        if 'merchant_id' in data and data['merchant_id'] != merchant.merchant_id:
            if Merchant.query.filter(
                Merchant.merchant_id == data['merchant_id'],
                Merchant.id != merchant_id
            ).first():
                return jsonify({'error': 'Merchant ID already exists'}), 409
        
        # Update fields
        updatable_fields = [
            'merchant_id', 'name', 'description', 'website', 
            'contact_email', 'phone', 'address', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(merchant, field, data[field])
        
        merchant.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(merchant.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@merchant_bp.route('/<int:merchant_id>', methods=['DELETE'])
def delete_merchant(merchant_id):
    """Delete a merchant"""
    try:
        merchant = Merchant.query.get_or_404(merchant_id)
        
        # Check if merchant has active offers
        active_offers = Offer.query.filter_by(merchant_id=merchant_id, is_active=True).count()
        if active_offers > 0:
            return jsonify({
                'error': f'Cannot delete merchant with {active_offers} active offers. Deactivate offers first.'
            }), 400
        
        # Check if merchant has transaction history
        transaction_count = MerchantOfferHistory.query.filter_by(merchant_id=merchant_id).count()
        if transaction_count > 0:
            return jsonify({
                'error': f'Cannot delete merchant with {transaction_count} transaction records. Deactivate instead.'
            }), 400
        
        db.session.delete(merchant)
        db.session.commit()
        
        return jsonify({'message': 'Merchant deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@merchant_bp.route('/<int:merchant_id>/offers', methods=['GET'])
def get_merchant_offers(merchant_id):
    """Get all offers for a specific merchant"""
    try:
        merchant = Merchant.query.get_or_404(merchant_id)
        
        # Query parameters
        is_active = request.args.get('is_active', type=bool)
        category = request.args.get('category')
        
        query = Offer.query.filter(Offer.merchant_id == merchant_id)
        
        if is_active is not None:
            query = query.filter(Offer.is_active == is_active)
            if is_active:
                # Also check date validity
                now = datetime.utcnow()
                query = query.filter(
                    Offer.start_date <= now,
                    Offer.expiry_date >= now
                )
        
        if category:
            try:
                from app.models import OfferCategory
                offer_category = OfferCategory(category.upper())
                query = query.filter(Offer.category == offer_category)
            except ValueError:
                from app.models import OfferCategory
                valid_categories = [c.value for c in OfferCategory]
                return jsonify({'error': f'Invalid category. Valid categories: {valid_categories}'}), 400
        
        offers = query.order_by(Offer.start_date.desc()).all()
        
        return jsonify({
            'merchant_id': merchant_id,
            'merchant_name': merchant.name,
            'offers': [offer.to_dict() for offer in offers],
            'total': len(offers)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@merchant_bp.route('/<int:merchant_id>/history', methods=['GET'])
def get_merchant_offer_history(merchant_id):
    """Get merchant offer usage history"""
    try:
        merchant = Merchant.query.get_or_404(merchant_id)
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        offer_id = request.args.get('offer_id', type=int)
        
        # Build query
        query = MerchantOfferHistory.query.filter(MerchantOfferHistory.merchant_id == merchant_id)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(MerchantOfferHistory.transaction_date >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(MerchantOfferHistory.transaction_date <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format'}), 400
        
        if offer_id:
            query = query.filter(MerchantOfferHistory.offer_id == offer_id)
        
        # Order by transaction date (newest first)
        query = query.order_by(MerchantOfferHistory.transaction_date.desc())
        
        # Paginate
        history = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Calculate summary statistics
        total_transactions = query.count()
        total_discount = db.session.query(
            func.sum(MerchantOfferHistory.discount_applied)
        ).filter(MerchantOfferHistory.merchant_id == merchant_id).scalar() or 0
        
        total_revenue = db.session.query(
            func.sum(MerchantOfferHistory.transaction_amount)
        ).filter(MerchantOfferHistory.merchant_id == merchant_id).scalar() or 0
        
        return jsonify({
            'merchant_id': merchant_id,
            'merchant_name': merchant.name,
            'history': [record.to_dict() for record in history.items],
            'summary': {
                'total_transactions': total_transactions,
                'total_discount_given': float(total_discount),
                'total_revenue_generated': float(total_revenue),
                'average_transaction': float(total_revenue / total_transactions) if total_transactions > 0 else 0
            },
            'total': history.total,
            'pages': history.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@merchant_bp.route('/<int:merchant_id>/analytics', methods=['GET'])
def get_merchant_analytics(merchant_id):
    """Get merchant analytics and insights"""
    try:
        merchant = Merchant.query.get_or_404(merchant_id)
        
        # Query parameters for date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build base query
        base_query = MerchantOfferHistory.query.filter(MerchantOfferHistory.merchant_id == merchant_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            base_query = base_query.filter(MerchantOfferHistory.transaction_date >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            base_query = base_query.filter(MerchantOfferHistory.transaction_date <= end_dt)
        
        # Get all records for analysis
        records = base_query.all()
        
        if not records:
            return jsonify({
                'merchant_id': merchant_id,
                'merchant_name': merchant.name,
                'message': 'No transaction data found for the specified period',
                'analytics': {}
            }), 200
        
        # Calculate analytics
        total_transactions = len(records)
        total_revenue = sum(float(r.transaction_amount) for r in records)
        total_discount = sum(float(r.discount_applied) for r in records)
        total_rewards = sum(r.reward_points_earned for r in records)
        
        # Group by offer
        offer_analytics = {}
        for record in records:
            offer_id = record.offer_id
            if offer_id not in offer_analytics:
                offer_analytics[offer_id] = {
                    'offer_id': offer_id,
                    'offer_title': record.offer.title,
                    'transactions': 0,
                    'revenue': 0,
                    'discount': 0,
                    'rewards': 0
                }
            
            offer_analytics[offer_id]['transactions'] += 1
            offer_analytics[offer_id]['revenue'] += float(record.transaction_amount)
            offer_analytics[offer_id]['discount'] += float(record.discount_applied)
            offer_analytics[offer_id]['rewards'] += record.reward_points_earned
        
        # Group by customer
        customer_analytics = {}
        for record in records:
            customer_id = record.customer_id
            if customer_id not in customer_analytics:
                customer_analytics[customer_id] = {
                    'customer_id': customer_id,
                    'customer_name': f"{record.customer.first_name} {record.customer.last_name}",
                    'transactions': 0,
                    'revenue': 0,
                    'discount': 0,
                    'rewards': 0
                }
            
            customer_analytics[customer_id]['transactions'] += 1
            customer_analytics[customer_id]['revenue'] += float(record.transaction_amount)
            customer_analytics[customer_id]['discount'] += float(record.discount_applied)
            customer_analytics[customer_id]['rewards'] += record.reward_points_earned
        
        # Monthly trends (if data spans multiple months)
        monthly_trends = {}
        for record in records:
            month_key = record.transaction_date.strftime('%Y-%m')
            if month_key not in monthly_trends:
                monthly_trends[month_key] = {
                    'month': month_key,
                    'transactions': 0,
                    'revenue': 0,
                    'discount': 0
                }
            
            monthly_trends[month_key]['transactions'] += 1
            monthly_trends[month_key]['revenue'] += float(record.transaction_amount)
            monthly_trends[month_key]['discount'] += float(record.discount_applied)
        
        return jsonify({
            'merchant_id': merchant_id,
            'merchant_name': merchant.name,
            'analytics': {
                'summary': {
                    'total_transactions': total_transactions,
                    'total_revenue': round(total_revenue, 2),
                    'total_discount_given': round(total_discount, 2),
                    'total_rewards_issued': total_rewards,
                    'average_transaction_value': round(total_revenue / total_transactions, 2),
                    'discount_percentage': round((total_discount / total_revenue) * 100, 2) if total_revenue > 0 else 0
                },
                'offer_performance': list(offer_analytics.values()),
                'customer_breakdown': list(customer_analytics.values()),
                'monthly_trends': list(monthly_trends.values())
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@merchant_bp.route('/categories', methods=['GET'])
def get_merchant_categories():
    """Get all available merchant categories"""
    try:
        categories = [
            {
                'name': category.name,
                'value': category.value,
                'description': {
                    'RESTAURANT': 'Restaurants and food service establishments',
                    'RETAIL_STORE': 'Physical retail stores and shops',
                    'GAS_STATION': 'Gas stations and fuel providers',
                    'AIRLINE': 'Airlines and air travel services',
                    'HOTEL': 'Hotels and accommodation services',
                    'E_COMMERCE': 'Online retail and e-commerce platforms',
                    'GROCERY_STORE': 'Grocery stores and supermarkets',
                    'PHARMACY': 'Pharmacies and health stores',
                    'ENTERTAINMENT_VENUE': 'Entertainment venues and services',
                    'HEALTHCARE_PROVIDER': 'Healthcare providers and medical services',
                    'TELECOM_PROVIDER': 'Telecommunications and internet providers',
                    'UTILITY_COMPANY': 'Utility companies (electricity, water, gas)',
                    'INSURANCE_COMPANY': 'Insurance companies and services',
                    'EDUCATIONAL_INSTITUTION': 'Schools, colleges, and educational services',
                    'AUTOMOTIVE_SERVICE': 'Automotive services and repair shops',
                    'HOME_IMPROVEMENT': 'Home improvement and hardware stores',
                    'FASHION_RETAILER': 'Fashion and clothing retailers',
                    'ELECTRONICS_STORE': 'Electronics and technology stores',
                    'SUBSCRIPTION_SERVICE': 'Subscription-based services',
                    'FINANCIAL_SERVICE': 'Financial services and institutions',
                    'FITNESS_CENTER': 'Gyms, fitness centers, and wellness services'
                }.get(category.name, 'Merchant category')
            }
            for category in MerchantCategory
        ]
        
        return jsonify({'categories': categories}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500