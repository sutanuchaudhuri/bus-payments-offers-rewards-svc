"""
Payment Plan Configuration Seed Data
This script creates default payment plan configurations for the system.
"""

from app.models import db, PaymentPlanConfig, PaymentPlanType
from decimal import Decimal

def create_payment_plan_configs():
    """Create default payment plan configurations"""

    # Full Payment Plan
    full_payment = PaymentPlanConfig(
        plan_type=PaymentPlanType.FULL_PAYMENT,
        name="Full Payment",
        description="Pay the full amount immediately with no interest charges",
        duration_months=1,
        base_interest_rate=Decimal('0.00'),
        penalty_rate=Decimal('0.00'),
        minimum_amount=Decimal('1.00'),
        maximum_amount=None,
        processing_fee_percentage=Decimal('0.00'),
        reward_points_multiplier=Decimal('1.00'),
        is_active=True
    )

    # 6-Month Installment Plan
    six_month = PaymentPlanConfig(
        plan_type=PaymentPlanType.INSTALLMENT_6_MONTHS,
        name="6-Month Installment Plan",
        description="Spread payments over 6 months with competitive interest rates",
        duration_months=6,
        base_interest_rate=Decimal('8.99'),  # 8.99% annual
        penalty_rate=Decimal('5.00'),  # 5% late fee
        minimum_amount=Decimal('100.00'),
        maximum_amount=Decimal('10000.00'),
        processing_fee_percentage=Decimal('2.50'),  # 2.5% processing fee
        reward_points_multiplier=Decimal('1.25'),  # 25% bonus points
        is_active=True
    )

    # 12-Month Installment Plan
    twelve_month = PaymentPlanConfig(
        plan_type=PaymentPlanType.INSTALLMENT_12_MONTHS,
        name="12-Month Installment Plan",
        description="Lower monthly payments spread over 12 months",
        duration_months=12,
        base_interest_rate=Decimal('12.99'),  # 12.99% annual
        penalty_rate=Decimal('5.00'),  # 5% late fee
        minimum_amount=Decimal('500.00'),
        maximum_amount=Decimal('25000.00'),
        processing_fee_percentage=Decimal('3.00'),  # 3% processing fee
        reward_points_multiplier=Decimal('1.50'),  # 50% bonus points
        is_active=True
    )

    # 24-Month Installment Plan
    twenty_four_month = PaymentPlanConfig(
        plan_type=PaymentPlanType.INSTALLMENT_24_MONTHS,
        name="24-Month Extended Plan",
        description="Extended payment plan for larger amounts with maximum flexibility",
        duration_months=24,
        base_interest_rate=Decimal('15.99'),  # 15.99% annual
        penalty_rate=Decimal('6.00'),  # 6% late fee
        minimum_amount=Decimal('1000.00'),
        maximum_amount=Decimal('50000.00'),
        processing_fee_percentage=Decimal('3.50'),  # 3.5% processing fee
        reward_points_multiplier=Decimal('2.00'),  # 100% bonus points
        is_active=True
    )

    # Minimum Payment Plan
    minimum_payment = PaymentPlanConfig(
        plan_type=PaymentPlanType.MINIMUM_PAYMENT,
        name="Minimum Payment Plan",
        description="Pay minimum amount each month (2.5% of balance or $25, whichever is higher)",
        duration_months=60,  # Maximum 5 years
        base_interest_rate=Decimal('19.99'),  # 19.99% annual
        penalty_rate=Decimal('7.50'),  # 7.5% late fee
        minimum_amount=Decimal('100.00'),
        maximum_amount=Decimal('15000.00'),
        processing_fee_percentage=Decimal('1.00'),  # 1% processing fee
        reward_points_multiplier=Decimal('1.00'),  # Standard points
        is_active=True
    )

    # Add all configurations to the session
    configs = [full_payment, six_month, twelve_month, twenty_four_month, minimum_payment]

    for config in configs:
        # Check if configuration already exists
        existing = PaymentPlanConfig.query.filter_by(plan_type=config.plan_type).first()
        if not existing:
            db.session.add(config)
            print(f"Added payment plan configuration: {config.name}")
        else:
            print(f"Payment plan configuration already exists: {config.name}")

    db.session.commit()
    print("Payment plan configurations created successfully!")

if __name__ == "__main__":
    # This would be run from the Flask app context
    create_payment_plan_configs()
