from flask import Blueprint, jsonify, request
from app.models import (
    db, Booking, Customer, Payment, Offer, BookingStatus, 
    Refund, RefundStatus
)
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import requests

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/api/bookings', methods=['POST'])
def create_booking():
    """Create a new booking"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer_id', 'service_type', 'booking_amount', 'final_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Generate booking reference
        booking_reference = f"BK{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Create booking
        booking = Booking(
            booking_reference=booking_reference,
            customer_id=data['customer_id'],
            payment_id=data.get('payment_id'),
            offer_id=data.get('offer_id'),
            service_type=data['service_type'],
            service_booking_id=data.get('service_booking_id'),
            status=BookingStatus.CONFIRMED,
            booking_amount=data['booking_amount'],
            discount_amount=data.get('discount_amount', 0),
            final_amount=data['final_amount'],
            booking_details=data.get('booking_details', {}),
            service_date=datetime.fromisoformat(data['service_date']) if data.get('service_date') else None,
            is_refundable=data.get('is_refundable', True),
            cancellation_fee=data.get('cancellation_fee', 0)
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking_id': booking.id,
            'booking_reference': booking_reference,
            'status': booking.status.value,
            'message': 'Booking created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@booking_bp.route('/api/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        data = request.get_json()
        
        # Find booking
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Check if booking can be cancelled
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.REFUNDED]:
            return jsonify({'error': f'Booking is already {booking.status.value.lower()}'}), 400
        
        # Calculate cancellation fee based on service date
        cancellation_fee = 0
        refund_amount = float(booking.final_amount)
        
        if booking.service_date:
            days_until_service = (booking.service_date - datetime.now()).days
            
            # Dynamic cancellation fee based on timing
            if days_until_service < 1:
                cancellation_fee = refund_amount * 0.5  # 50% fee for same day
            elif days_until_service < 7:
                cancellation_fee = refund_amount * 0.25  # 25% fee for < 7 days
            elif days_until_service < 30:
                cancellation_fee = refund_amount * 0.1   # 10% fee for < 30 days
            # No fee for > 30 days
            
            # Override with booking-specific fee if set
            if booking.cancellation_fee and booking.cancellation_fee > 0:
                cancellation_fee = min(cancellation_fee, float(booking.cancellation_fee))
        
        refund_amount = refund_amount - cancellation_fee
        
        # Cancel with external service if service_booking_id exists
        external_cancellation_success = True
        if booking.service_booking_id:
            external_cancellation_success = cancel_external_booking(
                booking.service_type, 
                booking.service_booking_id
            )
        
        # Update booking status
        if external_cancellation_success:
            booking.status = BookingStatus.CANCELLED
            booking.cancellation_date = datetime.now()
            booking.cancellation_reason = data.get('reason', 'Cancelled by customer')
            booking.cancellation_fee = Decimal(str(cancellation_fee))
        else:
            booking.status = BookingStatus.PENDING_CANCELLATION
        
        # Create refund if applicable
        refund = None
        if refund_amount > 0 and booking.is_refundable:
            refund_reference = f"RF{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
            
            refund = Refund(
                refund_reference=refund_reference,
                original_payment_id=booking.payment_id,
                booking_id=booking.id,
                customer_id=booking.customer_id,
                refund_type='booking_cancellation',
                refund_amount=Decimal(str(booking.final_amount)),
                processing_fee=Decimal(str(cancellation_fee)),
                net_refund_amount=Decimal(str(refund_amount)),
                status=RefundStatus.APPROVED if external_cancellation_success else RefundStatus.REQUESTED,
                reason=f"Booking cancellation: {booking.booking_reference}",
                approved_date=datetime.now() if external_cancellation_success else None,
                estimated_completion=datetime.now() + timedelta(days=5)
            )
            db.session.add(refund)
        
        db.session.commit()
        
        response = {
            'success': True,
            'booking_id': booking.id,
            'booking_reference': booking.booking_reference,
            'status': booking.status.value,
            'cancellation_date': booking.cancellation_date.isoformat() if booking.cancellation_date else None,
            'cancellation_fee': float(cancellation_fee),
            'refund_amount': float(refund_amount) if refund_amount > 0 else 0,
            'external_service_cancelled': external_cancellation_success,
            'message': 'Booking cancelled successfully' if external_cancellation_success else 'Booking cancellation pending external service confirmation'
        }
        
        if refund:
            response['refund_reference'] = refund.refund_reference
            response['refund_status'] = refund.status.value
        
        return jsonify(response), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@booking_bp.route('/api/bookings/<int:booking_id>/status', methods=['GET'])
def get_booking_status(booking_id):
    """Get booking status and details"""
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Get related refunds
        refunds = Refund.query.filter_by(booking_id=booking.id).all()
        
        response = {
            'booking_id': booking.id,
            'booking_reference': booking.booking_reference,
            'customer_id': booking.customer_id,
            'service_type': booking.service_type,
            'status': booking.status.value,
            'booking_amount': float(booking.booking_amount),
            'discount_amount': float(booking.discount_amount),
            'final_amount': float(booking.final_amount),
            'booking_date': booking.booking_date.isoformat(),
            'service_date': booking.service_date.isoformat() if booking.service_date else None,
            'is_refundable': booking.is_refundable,
            'booking_details': booking.booking_details,
            'refunds': []
        }
        
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.PENDING_CANCELLATION]:
            response.update({
                'cancellation_date': booking.cancellation_date.isoformat() if booking.cancellation_date else None,
                'cancellation_reason': booking.cancellation_reason,
                'cancellation_fee': float(booking.cancellation_fee) if booking.cancellation_fee else 0
            })
        
        # Add refund information
        for refund in refunds:
            response['refunds'].append({
                'refund_reference': refund.refund_reference,
                'refund_amount': float(refund.refund_amount),
                'processing_fee': float(refund.processing_fee),
                'net_refund_amount': float(refund.net_refund_amount),
                'status': refund.status.value,
                'requested_date': refund.requested_date.isoformat(),
                'estimated_completion': refund.estimated_completion.isoformat() if refund.estimated_completion else None
            })
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@booking_bp.route('/api/bookings/<int:booking_id>/modify', methods=['PUT'])
def modify_booking(booking_id):
    """Modify booking details (if allowed)"""
    try:
        data = request.get_json()
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Check if booking can be modified
        if booking.status != BookingStatus.CONFIRMED:
            return jsonify({'error': f'Cannot modify booking with status: {booking.status.value}'}), 400
        
        # Check if modification is allowed based on service date
        if booking.service_date:
            days_until_service = (booking.service_date - datetime.now()).days
            if days_until_service < 1:
                return jsonify({'error': 'Cannot modify booking on the same day of service'}), 400
        
        # Update allowed fields
        modifiable_fields = ['service_date', 'booking_details']
        modification_fee = 0
        
        for field in modifiable_fields:
            if field in data:
                if field == 'service_date':
                    booking.service_date = datetime.fromisoformat(data[field])
                    modification_fee += 25.00  # $25 modification fee
                elif field == 'booking_details':
                    booking.booking_details.update(data[field])
        
        # Add modification fee if changes were made
        if modification_fee > 0:
            booking.final_amount += modification_fee
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking_id': booking.id,
            'booking_reference': booking.booking_reference,
            'modification_fee': modification_fee,
            'new_final_amount': float(booking.final_amount),
            'message': 'Booking modified successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@booking_bp.route('/api/bookings', methods=['GET'])
def list_bookings():
    """List bookings with filtering options"""
    try:
        # Get query parameters
        customer_id = request.args.get('customer_id', type=int)
        status = request.args.get('status')
        service_type = request.args.get('service_type')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Build query
        query = Booking.query
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        if status:
            try:
                booking_status = BookingStatus(status.upper())
                query = query.filter_by(status=booking_status)
            except ValueError:
                return jsonify({'error': f'Invalid status: {status}'}), 400
        
        if service_type:
            query = query.filter_by(service_type=service_type)
        
        # Order by most recent first
        query = query.order_by(Booking.created_at.desc())
        
        # Paginate results
        bookings = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        results = []
        for booking in bookings.items:
            results.append({
                'booking_id': booking.id,
                'booking_reference': booking.booking_reference,
                'customer_id': booking.customer_id,
                'service_type': booking.service_type,
                'status': booking.status.value,
                'final_amount': float(booking.final_amount),
                'booking_date': booking.booking_date.isoformat(),
                'service_date': booking.service_date.isoformat() if booking.service_date else None
            })
        
        return jsonify({
            'bookings': results,
            'total': bookings.total,
            'pages': bookings.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

def cancel_external_booking(service_type, service_booking_id):
    """Cancel booking with external service"""
    try:
        service_ports = {
            'travel': 5002,
            'hotel': 5003,
            'shopping': 5004
        }
        
        if service_type not in service_ports:
            return False
        
        port = service_ports[service_type]
        cancel_url = f"http://localhost:{port}/cancel/{service_booking_id}"
        
        response = requests.post(cancel_url, timeout=5)
        return response.status_code == 200
        
    except requests.RequestException:
        return False
    except Exception:
        return False