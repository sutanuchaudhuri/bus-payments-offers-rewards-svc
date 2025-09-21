from flask import Blueprint, jsonify, request
from app.models import (
    db, Refund, RefundStatus, Payment, Booking, Customer,
    RedemptionCancellation, Reward
)
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import uuid
import logging

refund_bp = Blueprint('refund', __name__)
logger = logging.getLogger(__name__)

@refund_bp.route('/api/refunds/request', methods=['POST'])
def request_refund():
    """Request a refund"""
    try:
        logger.info("POST /api/refunds/request - Refund request received")
        data = request.get_json()
        logger.debug(f"Refund request data: {data}")

        # Validate required fields
        required_fields = ['refund_type', 'refund_amount', 'reason']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate refund type and related IDs
        refund_type = data['refund_type']
        if refund_type not in ['booking_cancellation', 'dispute_resolution', 'goodwill']:
            logger.warning(f"Invalid refund type: {refund_type}")
            return jsonify({'error': 'Invalid refund type'}), 400
        
        # Check for original payment
        if 'original_payment_id' not in data:
            logger.warning("Missing original_payment_id in refund request")
            return jsonify({'error': 'original_payment_id is required'}), 400

        original_payment = Payment.query.get(data['original_payment_id'])
        if not original_payment:
            logger.warning(f"Original payment not found: {data['original_payment_id']}")
            return jsonify({'error': 'Original payment not found'}), 404
        
        # Validate refund amount
        refund_amount = float(data['refund_amount'])
        if refund_amount <= 0 or refund_amount > float(original_payment.amount):
            logger.warning(f"Invalid refund amount: {refund_amount}")
            return jsonify({'error': 'Invalid refund amount'}), 400

        # Calculate processing fee (typically 1-3% or flat fee)
        processing_fee = min(data['refund_amount'] * 0.02, 25.00)  # 2% or $25 max
        if data.get('processing_fee') is not None:
            processing_fee = data['processing_fee']
            
        net_refund_amount = data['refund_amount'] - processing_fee
        
        # Generate refund reference
        refund_reference = f"RF{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Create refund
        refund = Refund(
            refund_reference=refund_reference,
            original_payment_id=data['original_payment_id'],
            booking_id=data.get('booking_id'),
            customer_id=original_payment.customer_id,
            refund_type=refund_type,
            refund_amount=data['refund_amount'],
            processing_fee=processing_fee,
            net_refund_amount=net_refund_amount,
            status=RefundStatus.REQUESTED,
            reason=data['reason'],
            estimated_completion=datetime.now() + timedelta(days=5)
        )
        
        db.session.add(refund)
        db.session.commit()
        
        logger.info(f"Refund request created successfully with ID: {refund.refund_id}")
        return jsonify({
            'success': True,
            'refund_id': refund.id,
            'refund_reference': refund_reference,
            'status': refund.status.value,
            'refund_amount': float(refund.refund_amount),
            'processing_fee': float(processing_fee),
            'net_refund_amount': float(net_refund_amount),
            'estimated_completion': refund.estimated_completion.isoformat(),
            'message': 'Refund request submitted successfully'
        }), 201
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in refund request: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Error in refund request: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@refund_bp.route('/api/refunds/<int:refund_id>', methods=['GET'])
def get_refund(refund_id):
    """Get refund details"""
    try:
        refund = Refund.query.get(refund_id)
        if not refund:
            return jsonify({'error': 'Refund not found'}), 404
        
        response = {
            'refund_id': refund.id,
            'refund_reference': refund.refund_reference,
            'original_payment_id': refund.original_payment_id,
            'booking_id': refund.booking_id,
            'customer_id': refund.customer_id,
            'refund_type': refund.refund_type,
            'status': refund.status.value,
            'refund_amount': float(refund.refund_amount),
            'processing_fee': float(refund.processing_fee),
            'net_refund_amount': float(refund.net_refund_amount),
            'reason': refund.reason,
            'requested_date': refund.requested_date.isoformat(),
            'approved_date': refund.approved_date.isoformat() if refund.approved_date else None,
            'processed_date': refund.processed_date.isoformat() if refund.processed_date else None,
            'completed_date': refund.completed_date.isoformat() if refund.completed_date else None,
            'estimated_completion': refund.estimated_completion.isoformat() if refund.estimated_completion else None
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@refund_bp.route('/api/refunds/<int:refund_id>/approve', methods=['PUT'])
def approve_refund(refund_id):
    """Approve a refund request"""
    try:
        data = request.get_json()
        
        refund = Refund.query.get(refund_id)
        if not refund:
            return jsonify({'error': 'Refund not found'}), 404
        
        # Check if refund can be approved
        if refund.status != RefundStatus.REQUESTED:
            return jsonify({'error': f'Cannot approve refund with status: {refund.status.value}'}), 400
        
        # Update refund status
        refund.status = RefundStatus.APPROVED
        refund.approved_date = datetime.now()
        
        # Auto-process if it's a simple case
        auto_process_types = ['goodwill', 'booking_cancellation']
        if refund.refund_type in auto_process_types and refund.net_refund_amount < 500:
            refund.status = RefundStatus.PROCESSED
            refund.processed_date = datetime.now()
            refund.estimated_completion = datetime.now() + timedelta(days=3)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'refund_id': refund.id,
            'refund_reference': refund.refund_reference,
            'status': refund.status.value,
            'approved_date': refund.approved_date.isoformat(),
            'processed_date': refund.processed_date.isoformat() if refund.processed_date else None,
            'estimated_completion': refund.estimated_completion.isoformat(),
            'message': f'Refund approved and {"processed" if refund.status == RefundStatus.PROCESSED else "queued for processing"}'
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@refund_bp.route('/api/refunds/<int:refund_id>/deny', methods=['PUT'])
def deny_refund(refund_id):
    """Deny a refund request"""
    try:
        data = request.get_json()
        
        refund = Refund.query.get(refund_id)
        if not refund:
            return jsonify({'error': 'Refund not found'}), 404
        
        if refund.status != RefundStatus.REQUESTED:
            return jsonify({'error': f'Cannot deny refund with status: {refund.status.value}'}), 400
        
        # Update refund status
        refund.status = RefundStatus.DENIED
        
        # Add denial reason if provided
        if data.get('denial_reason'):
            refund.reason += f" | DENIED: {data['denial_reason']}"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'refund_id': refund.id,
            'refund_reference': refund.refund_reference,
            'status': refund.status.value,
            'message': 'Refund request denied'
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@refund_bp.route('/api/refunds/points/cancel', methods=['POST'])
def cancel_points_redemption():
    """Cancel a points redemption and restore points"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['reward_id', 'cancellation_reason']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Find the original reward
        original_reward = Reward.query.get(data['reward_id'])
        if not original_reward:
            return jsonify({'error': 'Reward not found'}), 404
        
        # Check if reward can be cancelled
        if original_reward.status.value not in ['EARNED', 'REDEEMED']:
            return jsonify({'error': f'Cannot cancel reward with status: {original_reward.status.value}'}), 400
        
        # Calculate points to restore
        points_to_restore = original_reward.points_earned
        cancellation_fee_points = 0
        
        # Apply cancellation fee for certain redemptions
        if original_reward.status.value == 'REDEEMED':
            # 5% cancellation fee for redeemed points
            cancellation_fee_points = int(points_to_restore * 0.05)
        
        net_points_restored = points_to_restore - cancellation_fee_points
        
        # Generate cancellation reference
        cancellation_reference = f"PC{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Create redemption cancellation record
        cancellation = RedemptionCancellation(
            cancellation_reference=cancellation_reference,
            original_reward_id=data['reward_id'],
            customer_id=original_reward.customer_id,
            points_to_restore=points_to_restore,
            cancellation_fee_points=cancellation_fee_points,
            net_points_restored=net_points_restored,
            cancellation_reason=data['cancellation_reason'],
            status='APPROVED',  # Auto-approve for now
            processed_date=datetime.now()
        )
        
        db.session.add(cancellation)
        
        # Update original reward status
        original_reward.status_notes = f"CANCELLED: {data['cancellation_reason']}"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'cancellation_id': cancellation.id,
            'cancellation_reference': cancellation_reference,
            'original_reward_id': data['reward_id'],
            'points_to_restore': points_to_restore,
            'cancellation_fee_points': cancellation_fee_points,
            'net_points_restored': net_points_restored,
            'status': cancellation.status,
            'message': 'Points redemption cancelled successfully'
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@refund_bp.route('/api/refunds', methods=['GET'])
def list_refunds():
    """List refunds with filtering options"""
    try:
        # Get query parameters
        customer_id = request.args.get('customer_id', type=int)
        status = request.args.get('status')
        refund_type = request.args.get('refund_type')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Build query
        query = Refund.query
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        if status:
            try:
                refund_status = RefundStatus(status.upper())
                query = query.filter_by(status=refund_status)
            except ValueError:
                return jsonify({'error': f'Invalid status: {status}'}), 400
        
        if refund_type:
            query = query.filter_by(refund_type=refund_type)
        
        # Order by most recent first
        query = query.order_by(Refund.requested_date.desc())
        
        # Paginate results
        refunds = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        results = []
        for refund in refunds.items:
            results.append({
                'refund_id': refund.id,
                'refund_reference': refund.refund_reference,
                'customer_id': refund.customer_id,
                'refund_type': refund.refund_type,
                'status': refund.status.value,
                'refund_amount': float(refund.refund_amount),
                'net_refund_amount': float(refund.net_refund_amount),
                'requested_date': refund.requested_date.isoformat(),
                'estimated_completion': refund.estimated_completion.isoformat() if refund.estimated_completion else None
            })
        
        return jsonify({
            'refunds': results,
            'total': refunds.total,
            'pages': refunds.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500