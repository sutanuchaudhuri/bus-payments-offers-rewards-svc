from flask import Blueprint, request, jsonify
from app.models import db, CustomerProfileHistory, Customer, Merchant, Offer, OfferCategory, MerchantCategory
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, and_

profile_history_bp = Blueprint('profile_history', __name__)

@profile_history_bp.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer_profile_history(customer_id):
    """Get customer's merchant offer usage history"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        merchant_id = request.args.get('merchant_id', type=int)
        offer_category = request.args.get('offer_category')
        merchant_category = request.args.get('merchant_category')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        min_amount = request.args.get('min_amount', type=float)
        max_amount = request.args.get('max_amount', type=float)
        
        # Build query
        query = CustomerProfileHistory.query.filter(CustomerProfileHistory.customer_id == customer_id)
        
        if merchant_id:
            query = query.filter(CustomerProfileHistory.merchant_id == merchant_id)
        
        if offer_category:
            try:
                category = OfferCategory(offer_category.upper())
                query = query.filter(CustomerProfileHistory.offer_category == category)
            except ValueError:
                valid_categories = [c.value for c in OfferCategory]
                return jsonify({'error': f'Invalid offer category. Valid categories: {valid_categories}'}), 400
        
        if merchant_category:
            try:
                category = MerchantCategory(merchant_category.upper())
                query = query.filter(CustomerProfileHistory.merchant_category == category)
            except ValueError:
                valid_categories = [c.value for c in MerchantCategory]
                return jsonify({'error': f'Invalid merchant category. Valid categories: {valid_categories}'}), 400
        
        # Date range filtering
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(CustomerProfileHistory.availed_date >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(CustomerProfileHistory.availed_date <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format'}), 400
        
        # Amount range filtering
        if min_amount is not None:
            query = query.filter(CustomerProfileHistory.amount_availed >= min_amount)
        
        if max_amount is not None:
            query = query.filter(CustomerProfileHistory.amount_availed <= max_amount)
        
        # Order by availed date (newest first)
        query = query.order_by(CustomerProfileHistory.availed_date.desc())
        
        # Paginate
        history = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Calculate summary statistics
        total_saved = db.session.query(
            func.sum(CustomerProfileHistory.amount_availed)
        ).filter(CustomerProfileHistory.customer_id == customer_id).scalar() or 0
        
        total_spent = db.session.query(
            func.sum(CustomerProfileHistory.transaction_amount)
        ).filter(CustomerProfileHistory.customer_id == customer_id).scalar() or 0
        
        total_transactions = db.session.query(
            func.count(CustomerProfileHistory.id)
        ).filter(CustomerProfileHistory.customer_id == customer_id).scalar() or 0
        
        # Savings by category
        category_savings = {}
        category_results = db.session.query(
            CustomerProfileHistory.offer_category,
            func.sum(CustomerProfileHistory.amount_availed)
        ).filter(
            CustomerProfileHistory.customer_id == customer_id
        ).group_by(CustomerProfileHistory.offer_category).all()
        
        for category, savings in category_results:
            category_savings[category.value] = float(savings)
        
        # Top merchants
        merchant_results = db.session.query(
            CustomerProfileHistory.merchant_id,
            Merchant.name,
            func.sum(CustomerProfileHistory.amount_availed),
            func.count(CustomerProfileHistory.id)
        ).join(
            Merchant, CustomerProfileHistory.merchant_id == Merchant.id
        ).filter(
            CustomerProfileHistory.customer_id == customer_id
        ).group_by(
            CustomerProfileHistory.merchant_id, Merchant.name
        ).order_by(
            func.sum(CustomerProfileHistory.amount_availed).desc()
        ).limit(5).all()
        
        top_merchants = []
        for merchant_id, merchant_name, savings, transactions in merchant_results:
            top_merchants.append({
                'merchant_id': merchant_id,
                'merchant_name': merchant_name,
                'total_savings': float(savings),
                'transaction_count': transactions
            })
        
        return jsonify({
            'customer_id': customer_id,
            'customer_name': f"{customer.first_name} {customer.last_name}",
            'history': [record.to_dict() for record in history.items],
            'summary': {
                'total_amount_saved': float(total_saved),
                'total_amount_spent': float(total_spent),
                'total_transactions': total_transactions,
                'average_savings_per_transaction': float(total_saved / total_transactions) if total_transactions > 0 else 0,
                'savings_percentage': round((float(total_saved) / float(total_spent)) * 100, 2) if total_spent > 0 else 0,
                'savings_by_category': category_savings,
                'top_merchants': top_merchants
            },
            'total': history.total,
            'pages': history.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_history_bp.route('/merchant/<int:merchant_id>/customers', methods=['GET'])
def get_merchant_customer_history(merchant_id):
    """Get customer usage history for a specific merchant"""
    try:
        merchant = Merchant.query.get_or_404(merchant_id)
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = CustomerProfileHistory.query.filter(CustomerProfileHistory.merchant_id == merchant_id)
        
        # Date range filtering
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(CustomerProfileHistory.availed_date >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(CustomerProfileHistory.availed_date <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format'}), 400
        
        # Order by availed date (newest first)
        query = query.order_by(CustomerProfileHistory.availed_date.desc())
        
        # Paginate
        history = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get unique customers and their stats
        customer_stats = db.session.query(
            CustomerProfileHistory.customer_id,
            Customer.first_name,
            Customer.last_name,
            func.sum(CustomerProfileHistory.amount_availed),
            func.sum(CustomerProfileHistory.transaction_amount),
            func.count(CustomerProfileHistory.id)
        ).join(
            Customer, CustomerProfileHistory.customer_id == Customer.id
        ).filter(
            CustomerProfileHistory.merchant_id == merchant_id
        ).group_by(
            CustomerProfileHistory.customer_id,
            Customer.first_name,
            Customer.last_name
        ).order_by(
            func.sum(CustomerProfileHistory.amount_availed).desc()
        ).all()
        
        customer_summary = []
        for customer_id, first_name, last_name, savings, spent, transactions in customer_stats:
            customer_summary.append({
                'customer_id': customer_id,
                'customer_name': f"{first_name} {last_name}",
                'total_savings': float(savings),
                'total_spent': float(spent),
                'transaction_count': transactions,
                'average_savings': float(savings / transactions) if transactions > 0 else 0
            })
        
        return jsonify({
            'merchant_id': merchant_id,
            'merchant_name': merchant.name,
            'customer_history': [record.to_dict() for record in history.items],
            'customer_summary': customer_summary,
            'total': history.total,
            'pages': history.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_history_bp.route('', methods=['POST'])
def create_profile_history():
    """Create a new customer profile history record"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['customer_id', 'merchant_id', 'offer_id', 'amount_availed', 
                          'transaction_amount', 'statement_descriptor']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate references
        customer = Customer.query.get_or_404(data['customer_id'])
        merchant = Merchant.query.get_or_404(data['merchant_id'])
        offer = Offer.query.get_or_404(data['offer_id'])
        
        # Validate amounts
        amount_availed = Decimal(str(data['amount_availed']))
        transaction_amount = Decimal(str(data['transaction_amount']))
        
        if amount_availed <= 0:
            return jsonify({'error': 'Amount availed must be positive'}), 400
        
        if transaction_amount <= 0:
            return jsonify({'error': 'Transaction amount must be positive'}), 400
        
        if amount_availed > transaction_amount:
            return jsonify({'error': 'Amount availed cannot exceed transaction amount'}), 400
        
        # Parse availed date if provided
        availed_date = datetime.utcnow()
        if 'availed_date' in data and data['availed_date']:
            try:
                availed_date = datetime.fromisoformat(data['availed_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid availed_date format. Use ISO format'}), 400
        
        # Create profile history record
        profile_history = CustomerProfileHistory(
            customer_id=data['customer_id'],
            merchant_id=data['merchant_id'],
            offer_id=data['offer_id'],
            payment_id=data.get('payment_id'),
            amount_availed=amount_availed,
            transaction_amount=transaction_amount,
            statement_descriptor=data['statement_descriptor'],
            availed_date=availed_date,
            offer_category=offer.category,
            merchant_category=merchant.category
        )
        
        db.session.add(profile_history)
        db.session.commit()
        
        return jsonify(profile_history.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@profile_history_bp.route('/analytics', methods=['GET'])
def get_profile_history_analytics():
    """Get analytics across all customer profile history"""
    try:
        # Query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        customer_id = request.args.get('customer_id', type=int)
        merchant_id = request.args.get('merchant_id', type=int)
        
        # Build base query
        query = CustomerProfileHistory.query
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(CustomerProfileHistory.availed_date >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(CustomerProfileHistory.availed_date <= end_dt)
        
        if customer_id:
            query = query.filter(CustomerProfileHistory.customer_id == customer_id)
        
        if merchant_id:
            query = query.filter(CustomerProfileHistory.merchant_id == merchant_id)
        
        records = query.all()
        
        if not records:
            return jsonify({
                'message': 'No data found for the specified criteria',
                'analytics': {}
            }), 200
        
        # Calculate overall analytics
        total_savings = sum(float(r.amount_availed) for r in records)
        total_spent = sum(float(r.transaction_amount) for r in records)
        total_transactions = len(records)
        
        # Savings by offer category
        category_analytics = {}
        for record in records:
            category = record.offer_category.value
            if category not in category_analytics:
                category_analytics[category] = {
                    'category': category,
                    'transactions': 0,
                    'total_savings': 0,
                    'total_spent': 0
                }
            
            category_analytics[category]['transactions'] += 1
            category_analytics[category]['total_savings'] += float(record.amount_availed)
            category_analytics[category]['total_spent'] += float(record.transaction_amount)
        
        # Monthly trends
        monthly_trends = {}
        for record in records:
            month_key = record.availed_date.strftime('%Y-%m')
            if month_key not in monthly_trends:
                monthly_trends[month_key] = {
                    'month': month_key,
                    'transactions': 0,
                    'savings': 0,
                    'spent': 0
                }
            
            monthly_trends[month_key]['transactions'] += 1
            monthly_trends[month_key]['savings'] += float(record.amount_availed)
            monthly_trends[month_key]['spent'] += float(record.transaction_amount)
        
        return jsonify({
            'analytics': {
                'summary': {
                    'total_transactions': total_transactions,
                    'total_savings': round(total_savings, 2),
                    'total_spent': round(total_spent, 2),
                    'average_savings_per_transaction': round(total_savings / total_transactions, 2),
                    'overall_savings_percentage': round((total_savings / total_spent) * 100, 2)
                },
                'category_breakdown': list(category_analytics.values()),
                'monthly_trends': list(monthly_trends.values())
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500