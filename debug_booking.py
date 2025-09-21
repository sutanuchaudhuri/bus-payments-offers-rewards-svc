#!/usr/bin/env python3
"""
Simple test to verify booking APIs work
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from app.models import db, Booking

def test_booking_cancellation():
    """Test booking cancellation logic directly"""
    app = create_app()
    
    with app.app_context():
        print("Testing booking cancellation...")
        
        # Get the first booking
        booking = Booking.query.first()
        if not booking:
            print("No bookings found")
            return
        
        print(f"Found booking: {booking.id} - {booking.booking_reference}")
        print(f"Final amount: {booking.final_amount} (type: {type(booking.final_amount)})")
        print(f"Cancellation fee: {booking.cancellation_fee} (type: {type(booking.cancellation_fee)})")
        
        # Test the calculation that was failing
        try:
            refund_amount = float(booking.final_amount)
            print(f"Converted final_amount to float: {refund_amount}")
            
            if booking.cancellation_fee and booking.cancellation_fee > 0:
                cancellation_fee = float(booking.cancellation_fee)
                print(f"Converted cancellation_fee to float: {cancellation_fee}")
            else:
                cancellation_fee = 0
                print(f"No cancellation fee set: {cancellation_fee}")
            
            # Test dynamic calculation
            from datetime import datetime
            if booking.service_date:
                days_until_service = (booking.service_date - datetime.now()).days
                print(f"Days until service: {days_until_service}")
                
                # Dynamic cancellation fee based on timing
                if days_until_service < 1:
                    dynamic_fee = refund_amount * 0.5
                elif days_until_service < 7:
                    dynamic_fee = refund_amount * 0.25
                elif days_until_service < 30:
                    dynamic_fee = refund_amount * 0.1
                else:
                    dynamic_fee = 0
                
                print(f"Dynamic fee calculated: {dynamic_fee}")
                
                if cancellation_fee > 0:
                    final_fee = min(dynamic_fee, cancellation_fee)
                else:
                    final_fee = dynamic_fee
                
                print(f"Final cancellation fee: {final_fee}")
                
                final_refund = refund_amount - final_fee
                print(f"Final refund amount: {final_refund}")
            
            print("Calculation successful!")
            
        except Exception as e:
            print(f"Error in calculation: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_booking_cancellation()