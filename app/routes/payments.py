from flask import Blueprint, request, jsonify
from app.models import (db, Payment, CreditCard, Customer, PaymentStatus, Reward, RewardStatus,
                   Offer, CustomerOffer, MerchantOfferHistory, CustomerProfileHistory,
                   Merchant, OfferCategory)
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import logging
from sqlalchemy import func, and_, or_

payment_bp = Blueprint('payments', __name__)
logger = logging.getLogger(__name__)

def generate_reference_number():
    """Generate a unique reference number"""
    return f"PAY-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

def calculate_reward_points(amount, product_type):
    """Calculate reward points based on amount and card product type"""
    # Different multipliers for different card types
    multipliers = {
        'PLATINUM': 3.0,
        'GOLD': 2.0,
        'SILVER': 1.5,
        'BASIC': 1.0
    }
    
    # 1 point per dollar spent, multiplied by card type
    base_points = int(float(amount))
    multiplier = multipliers.get(product_type.value if hasattr(product_type, 'value') else product_type, 1.0)
    return int(base_points * multiplier)

@payment_bp.route('', methods=['POST'])
def make_payment():
    """Process a new payment"""
    try:
        logger.info("POST /api/payments - Payment request received")
        data = request.get_json()
        logger.debug(f"Payment data received: {data}")

        # Validation
        required_fields = ['credit_card_id', 'amount', 'merchant_name']
        for field in required_fields:
            if field not in data or data[field] is None:
                logger.warning(f"Missing required field: {field}")
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate credit card
        credit_card = CreditCard.query.get_or_404(data['credit_card_id'])
        if not credit_card.is_active:
            logger.warning(f"Credit card {data['credit_card_id']} is not active")
            return jsonify({'error': 'Credit card is not active'}), 400
        
        # Validate amount
        amount = Decimal(str(data['amount']))
        if amount <= 0:
            logger.warning(f"Invalid payment amount: {amount}")
            return jsonify({'error': 'Amount must be positive'}), 400
        
        # Check credit limit
        if amount > credit_card.available_credit:
            logger.warning(f"Payment amount {amount} exceeds available credit {credit_card.available_credit}")
            return jsonify({'error': 'Insufficient credit available'}), 400

        # Create payment record
        payment = Payment(
            credit_card_id=data['credit_card_id'],
            amount=amount,
            merchant_name=data['merchant_name'],
            reference_number=generate_reference_number(),
            status=PaymentStatus.COMPLETED,
            transaction_date=datetime.utcnow(),
            description=data.get('description', ''),
            category=data.get('category', 'general')
        )
        
        # Update credit card available credit
        credit_card.available_credit -= amount
        
        db.session.add(payment)
        db.session.commit()

        logger.info(f"Payment {payment.reference_number} processed successfully for amount {amount}")

        # Calculate and create reward points
        points_earned = calculate_reward_points(amount, credit_card.product_type)
        if points_earned > 0:
            reward = Reward(
                customer_id=credit_card.customer_id,
                payment_id=payment.id,
                points_earned=points_earned,
                status=RewardStatus.EARNED,
                expiry_date=datetime.utcnow() + timedelta(days=365)
            )
            db.session.add(reward)
            db.session.commit()
            logger.info(f"Reward points {points_earned} earned for payment {payment.reference_number}")

        response_data = payment.to_dict()
        response_data['points_earned'] = points_earned

        return jsonify(response_data), 201

    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('', methods=['GET'])
def get_payments():
    """Get payments with optional filtering"""
    try:
        logger.info("GET /api/payments - Request received")
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        customer_id = request.args.get('customer_id', type=int)
        status = request.args.get('status')
        merchant_name = request.args.get('merchant_name')

        logger.debug(f"Request parameters - page: {page}, per_page: {per_page}, customer_id: {customer_id}, status: {status}, merchant_name: {merchant_name}")

        query = Payment.query.join(CreditCard)

        if customer_id:
            query = query.filter(CreditCard.customer_id == customer_id)
            logger.debug(f"Filtering payments by customer_id: {customer_id}")

        if status:
            try:
                status_enum = PaymentStatus(status)
                query = query.filter(Payment.status == status_enum)
                logger.debug(f"Filtering payments by status: {status}")
            except ValueError:
                valid_statuses = [s.value for s in PaymentStatus]
                logger.warning(f"Invalid status: {status}")
                return jsonify({'error': f'Invalid status. Valid statuses: {valid_statuses}'}), 400
        
        if merchant_name:
            query = query.filter(Payment.merchant_name.ilike(f'%{merchant_name}%'))
            logger.debug(f"Filtering payments by merchant_name: {merchant_name}")

        payments = query.paginate(page=page, per_page=per_page, error_out=False)

        logger.info(f"Retrieved {payments.total} payments, showing page {page}")

        return jsonify({
            'payments': [payment.to_dict() for payment in payments.items],
            'total': payments.total,
            'pages': payments.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving payments: {str(e)}")
        return jsonify({'error': 'Failed to retrieve payments'}), 500

@payment_bp.route('/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    """Get a specific payment by ID"""
    try:
        payment = Payment.query.get_or_404(payment_id)
        
        # Include credit card and customer info
        payment_data = payment.to_dict()
        payment_data['credit_card'] = payment.credit_card.to_dict()
        payment_data['customer'] = payment.credit_card.customer.to_dict()
        
        # Include associated rewards
        rewards = Reward.query.filter_by(payment_id=payment_id).all()
        payment_data['rewards'] = [reward.to_dict() for reward in rewards]
        
        return jsonify(payment_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer_payments(customer_id):
    """Get all payments for a specific customer"""
    try:
        # Verify customer exists
        customer = Customer.query.get_or_404(customer_id)
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Payment.query.join(CreditCard).filter(CreditCard.customer_id == customer_id)
        
        # Date range filtering
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(Payment.transaction_date >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(Payment.transaction_date <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format'}), 400
        
        # Order by transaction date (newest first)
        query = query.order_by(Payment.transaction_date.desc())
        
        # Paginate
        payments = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Calculate summary statistics
        total_spent = db.session.query(db.func.sum(Payment.amount)).join(CreditCard).filter(
            CreditCard.customer_id == customer_id
        ).scalar() or 0
        
        return jsonify({
            'customer_id': customer_id,
            'customer_name': f"{customer.first_name} {customer.last_name}",
            'payments': [payment.to_dict() for payment in payments.items],
            'total_payments': payments.total,
            'total_amount_spent': float(total_spent),
            'pages': payments.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/<int:payment_id>/refund', methods=['POST'])
def refund_payment(payment_id):
    """Process a refund for a payment"""
    try:
        payment = Payment.query.get_or_404(payment_id)
        
        if payment.status == PaymentStatus.REFUNDED:
            return jsonify({'error': 'Payment already refunded'}), 400
        
        if payment.status != PaymentStatus.COMPLETED:
            return jsonify({'error': 'Can only refund completed payments'}), 400
        
        data = request.get_json() or {}
        refund_amount = Decimal(str(data.get('amount', payment.amount)))
        
        if refund_amount <= 0 or refund_amount > payment.amount:
            return jsonify({'error': 'Invalid refund amount'}), 400
        
        # Update payment status
        if refund_amount == payment.amount:
            payment.status = PaymentStatus.REFUNDED
        # For partial refunds, you might want to create a separate refund record
        
        # Restore credit limit
        credit_card = payment.credit_card
        credit_card.available_credit += refund_amount
        
        # Handle reward points (deduct if refunded)
        rewards = Reward.query.filter_by(payment_id=payment_id).all()
        for reward in rewards:
            if reward.status == RewardStatus.EARNED:
                # Calculate proportional point deduction
                points_to_deduct = int((refund_amount / payment.amount) * reward.points_earned)
                reward.points_redeemed = min(reward.points_earned, points_to_deduct)
                if reward.points_redeemed == reward.points_earned:
                    reward.status = RewardStatus.REDEEMED
        
        db.session.commit()
        
        return jsonify({
            'message': 'Refund processed successfully',
            'refund_amount': float(refund_amount),
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/analytics/spending', methods=['GET'])
def get_spending_analytics():
    """Get spending analytics"""
    try:
        customer_id = request.args.get('customer_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        group_by = request.args.get('group_by', 'month')  # month, week, day
        
        # Build base query
        query = Payment.query.filter(Payment.status == PaymentStatus.COMPLETED)
        
        if customer_id:
            query = query.join(CreditCard).filter(CreditCard.customer_id == customer_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Payment.transaction_date >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Payment.transaction_date <= end_dt)
        
        payments = query.all()
        
        # Calculate analytics
        total_amount = sum(float(p.amount) for p in payments)
        total_transactions = len(payments)
        avg_transaction = total_amount / total_transactions if total_transactions > 0 else 0
        
        # Group by merchant category
        category_spending = {}
        for payment in payments:
            category = payment.merchant_category or 'Other'
            category_spending[category] = category_spending.get(category, 0) + float(payment.amount)
        
        # Group by time period
        time_series = {}
        for payment in payments:
            if group_by == 'day':
                key = payment.transaction_date.strftime('%Y-%m-%d')
            elif group_by == 'week':
                # Get Monday of the week
                monday = payment.transaction_date - timedelta(days=payment.transaction_date.weekday())
                key = monday.strftime('%Y-%m-%d')
            else:  # month
                key = payment.transaction_date.strftime('%Y-%m')
            
            time_series[key] = time_series.get(key, 0) + float(payment.amount)
        
        return jsonify({
            'total_amount': total_amount,
            'total_transactions': total_transactions,
            'average_transaction': round(avg_transaction, 2),
            'spending_by_category': category_spending,
            'spending_by_time': time_series
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500