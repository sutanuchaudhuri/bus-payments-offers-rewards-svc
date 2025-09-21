from flask import Blueprint, request, jsonify
from app.models import db, Reward, Customer, RewardStatus, Payment, Offer
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from sqlalchemy import func, or_

reward_bp = Blueprint('rewards', __name__)
logger = logging.getLogger(__name__)

@reward_bp.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer_rewards(customer_id):
    """Get all rewards for a specific customer"""
    try:
        logger.info(f"GET /api/rewards/customer/{customer_id} - Request received")
        customer = Customer.query.get_or_404(customer_id)
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        logger.debug(f"Request parameters - page: {page}, per_page: {per_page}, status: {status}, start_date: {start_date}, end_date: {end_date}")

        # Build query
        query = Reward.query.filter(Reward.customer_id == customer_id)
        
        if status:
            try:
                reward_status = RewardStatus(status.upper())
                query = query.filter(Reward.status == reward_status)
                logger.debug(f"Filtering rewards by status: {status}")
            except ValueError:
                valid_statuses = [s.value for s in RewardStatus]
                logger.warning(f"Invalid status: {status}")
                return jsonify({'error': f'Invalid status. Valid statuses: {valid_statuses}'}), 400
        
        # Date range filtering
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(Reward.earned_date >= start_dt)
                logger.debug(f"Filtering rewards from start_date: {start_date}")
            except ValueError:
                logger.warning(f"Invalid start_date format: {start_date}")
                return jsonify({'error': 'Invalid start_date format. Use ISO format'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(Reward.earned_date <= end_dt)
                logger.debug(f"Filtering rewards to end_date: {end_date}")
            except ValueError:
                logger.warning(f"Invalid end_date format: {end_date}")
                return jsonify({'error': 'Invalid end_date format. Use ISO format'}), 400
        
        # Order by earned date (newest first)
        query = query.order_by(Reward.earned_date.desc())
        
        # Paginate
        rewards = query.paginate(page=page, per_page=per_page, error_out=False)

        logger.info(f"Retrieved {rewards.total} rewards for customer {customer_id}, showing page {page}")

        # Include payment and offer details
        rewards_data = []
        for reward in rewards.items:
            reward_dict = reward.to_dict()

            # Add payment details if available
            if reward.payment_id:
                payment = Payment.query.get(reward.payment_id)
                if payment:
                    reward_dict['payment'] = {
                        'id': payment.id,
                        'amount': float(payment.amount),
                        'merchant_name': payment.merchant_name,
                        'transaction_date': payment.transaction_date.isoformat(),
                        'reference_number': payment.reference_number
                    }

            # Add offer details if available
            if reward.offer_id:
                offer = Offer.query.get(reward.offer_id)
                if offer:
                    reward_dict['offer'] = {
                        'id': offer.id,
                        'title': offer.title,
                        'description': offer.description,
                        'merchant_name': offer.merchant_name
                    }

            rewards_data.append(reward_dict)

        return jsonify({
            'customer_id': customer_id,
            'customer_name': f"{customer.first_name} {customer.last_name}",
            'rewards': rewards_data,
            'total': rewards.total,
            'pages': rewards.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving rewards for customer {customer_id}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve rewards'}), 500

@reward_bp.route('/<int:reward_id>', methods=['GET'])
def get_reward(reward_id):
    """Get a specific reward by ID"""
    try:
        reward = Reward.query.get_or_404(reward_id)
        
        reward_data = reward.to_dict()
        
        # Include related information
        if reward.payment_id:
            payment = Payment.query.get(reward.payment_id)
            reward_data['payment'] = payment.to_dict() if payment else None
        
        if reward.offer_id:
            offer = Offer.query.get(reward.offer_id)
            reward_data['offer'] = offer.to_dict() if offer else None
        
        reward_data['customer'] = reward.customer.to_dict()
        
        return jsonify(reward_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reward_bp.route('', methods=['POST'])
def create_manual_reward():
    """Create a manual reward (not tied to a payment)"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['customer_id', 'points_earned', 'description']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate customer
        customer = Customer.query.get_or_404(data['customer_id'])
        
        # Validate points
        points_earned = int(data['points_earned'])
        if points_earned <= 0:
            return jsonify({'error': 'Points earned must be positive'}), 400
        
        # Calculate dollar value
        dollar_value = Decimal(str(points_earned * 0.01))  # 1 point = $0.01
        if 'dollar_value' in data and data['dollar_value']:
            dollar_value = Decimal(str(data['dollar_value']))
        
        # Parse expiry date if provided
        expiry_date = None
        if 'expiry_date' in data and data['expiry_date']:
            try:
                expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid expiry_date format. Use ISO format'}), 400
        else:
            # Default expiry: 2 years from now
            expiry_date = datetime.utcnow() + timedelta(days=730)
        
        # Create reward
        reward = Reward(
            customer_id=data['customer_id'],
            offer_id=data.get('offer_id'),
            points_earned=points_earned,
            dollar_value=dollar_value,
            status=RewardStatus.EARNED,
            expiry_date=expiry_date,
            description=data['description']
        )
        
        db.session.add(reward)
        db.session.commit()
        
        return jsonify(reward.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reward_bp.route('/<int:reward_id>/redeem', methods=['POST'])
def redeem_reward(reward_id):
    """Redeem reward points"""
    try:
        reward = Reward.query.get_or_404(reward_id)
        data = request.get_json() or {}
        
        if reward.status != RewardStatus.EARNED:
            return jsonify({'error': 'Reward is not available for redemption'}), 400
        
        # Check if reward has expired
        if reward.expiry_date and datetime.utcnow() > reward.expiry_date:
            reward.status = RewardStatus.EXPIRED
            db.session.commit()
            return jsonify({'error': 'Reward has expired'}), 400
        
        # Validate redemption amount
        points_to_redeem = data.get('points', reward.points_earned - reward.points_redeemed)
        if points_to_redeem <= 0:
            return jsonify({'error': 'Points to redeem must be positive'}), 400
        
        available_points = reward.points_earned - reward.points_redeemed
        if points_to_redeem > available_points:
            return jsonify({'error': f'Insufficient points. Available: {available_points}'}), 400
        
        # Process redemption
        reward.points_redeemed += points_to_redeem
        reward.redeemed_date = datetime.utcnow()
        
        # If all points redeemed, mark as redeemed
        if reward.points_redeemed >= reward.points_earned:
            reward.status = RewardStatus.REDEEMED
        
        # Calculate redeemed dollar value
        redeemed_dollar_value = Decimal(str(points_to_redeem * 0.01))
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reward points redeemed successfully',
            'points_redeemed': points_to_redeem,
            'dollar_value_redeemed': float(redeemed_dollar_value),
            'remaining_points': reward.points_earned - reward.points_redeemed,
            'reward': reward.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reward_bp.route('/customer/<int:customer_id>/redeem', methods=['POST'])
def redeem_customer_points(customer_id):
    """Redeem points from customer's total available balance"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        if 'points' not in data:
            return jsonify({'error': 'points is required'}), 400
        
        points_to_redeem = int(data['points'])
        if points_to_redeem <= 0:
            return jsonify({'error': 'Points to redeem must be positive'}), 400
        
        # Get available rewards (EARNED status, not expired)
        now = datetime.utcnow()
        available_rewards = Reward.query.filter(
            Reward.customer_id == customer_id,
            Reward.status == RewardStatus.EARNED,
            or_(Reward.expiry_date.is_(None), Reward.expiry_date > now)
        ).order_by(Reward.earned_date.asc()).all()  # FIFO redemption
        
        # Calculate total available points
        total_available = sum(r.points_earned - r.points_redeemed for r in available_rewards)
        
        if points_to_redeem > total_available:
            return jsonify({'error': f'Insufficient points. Available: {total_available}'}), 400
        
        # Redeem points from rewards (FIFO)
        remaining_to_redeem = points_to_redeem
        redeemed_rewards = []
        
        for reward in available_rewards:
            if remaining_to_redeem <= 0:
                break
            
            available_in_reward = reward.points_earned - reward.points_redeemed
            if available_in_reward <= 0:
                continue
            
            redeem_from_this = min(remaining_to_redeem, available_in_reward)
            
            reward.points_redeemed += redeem_from_this
            if not reward.redeemed_date:
                reward.redeemed_date = now
            
            if reward.points_redeemed >= reward.points_earned:
                reward.status = RewardStatus.REDEEMED
            
            redeemed_rewards.append({
                'reward_id': reward.id,
                'points_redeemed': redeem_from_this,
                'dollar_value': float(Decimal(str(redeem_from_this * 0.01)))
            })
            
            remaining_to_redeem -= redeem_from_this
        
        total_dollar_value = sum(r['dollar_value'] for r in redeemed_rewards)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Points redeemed successfully',
            'total_points_redeemed': points_to_redeem,
            'total_dollar_value': total_dollar_value,
            'redeemed_from_rewards': redeemed_rewards,
            'description': data.get('description', 'Point redemption')
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reward_bp.route('/customer/<int:customer_id>/balance', methods=['GET'])
def get_customer_balance(customer_id):
    """Get customer's current reward points balance"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # Calculate totals
        total_earned = db.session.query(
            func.sum(Reward.points_earned)
        ).filter(
            Reward.customer_id == customer_id,
            Reward.status != RewardStatus.EXPIRED
        ).scalar() or 0
        
        total_redeemed = db.session.query(
            func.sum(Reward.points_redeemed)
        ).filter(
            Reward.customer_id == customer_id
        ).scalar() or 0
        
        available_points = total_earned - total_redeemed
        
        # Calculate expiring points (next 30 days)
        expiring_date = datetime.utcnow() + timedelta(days=30)
        expiring_points = db.session.query(
            func.sum(Reward.points_earned - Reward.points_redeemed)
        ).filter(
            Reward.customer_id == customer_id,
            Reward.status == RewardStatus.EARNED,
            Reward.expiry_date <= expiring_date,
            Reward.expiry_date > datetime.utcnow()
        ).scalar() or 0
        
        # Recent earning activity (last 30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_earned = db.session.query(
            func.sum(Reward.points_earned)
        ).filter(
            Reward.customer_id == customer_id,
            Reward.earned_date >= recent_date
        ).scalar() or 0
        
        return jsonify({
            'customer_id': customer_id,
            'customer_name': f"{customer.first_name} {customer.last_name}",
            'balance': {
                'total_earned': int(total_earned),
                'total_redeemed': int(total_redeemed),
                'available_points': int(available_points),
                'available_dollar_value': float(Decimal(str(available_points * 0.01))),
                'expiring_soon': int(expiring_points),
                'recent_earned': int(recent_earned)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reward_bp.route('/customer/<int:customer_id>/history', methods=['GET'])
def get_redemption_history(customer_id):
    """Get customer's reward redemption history"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query for redeemed rewards
        query = Reward.query.filter(
            Reward.customer_id == customer_id,
            Reward.points_redeemed > 0
        )
        
        # Date range filtering
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(Reward.redeemed_date >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(Reward.redeemed_date <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format'}), 400
        
        # Order by redemption date (newest first)
        query = query.order_by(Reward.redeemed_date.desc())
        
        # Paginate
        rewards = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        history = []
        for reward in rewards.items:
            reward_data = reward.to_dict()
            reward_data['redeemed_dollar_value'] = float(Decimal(str(reward.points_redeemed * 0.01)))
            history.append(reward_data)
        
        # Calculate total redeemed
        total_redeemed = db.session.query(
            func.sum(Reward.points_redeemed)
        ).filter(
            Reward.customer_id == customer_id
        ).scalar() or 0
        
        total_dollar_redeemed = float(Decimal(str(total_redeemed * 0.01)))
        
        return jsonify({
            'customer_id': customer_id,
            'customer_name': f"{customer.first_name} {customer.last_name}",
            'redemption_history': history,
            'summary': {
                'total_points_redeemed': int(total_redeemed),
                'total_dollar_value_redeemed': total_dollar_redeemed
            },
            'total': rewards.total,
            'pages': rewards.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reward_bp.route('/expire-check', methods=['POST'])
def expire_rewards():
    """Check and expire rewards that have passed their expiry date"""
    try:
        now = datetime.utcnow()
        
        # Find expired rewards
        expired_rewards = Reward.query.filter(
            Reward.status == RewardStatus.EARNED,
            Reward.expiry_date < now
        ).all()
        
        expired_count = 0
        for reward in expired_rewards:
            reward.status = RewardStatus.EXPIRED
            expired_count += 1
        
        if expired_count > 0:
            db.session.commit()
        
        return jsonify({
            'message': f'{expired_count} rewards expired',
            'expired_count': expired_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500