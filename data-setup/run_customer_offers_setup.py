#!/usr/bin/env python3
"""
Runner script for Customer-Specific Offers Setup
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from customer_offers_setup import CustomerOffersSetupManager

if __name__ == "__main__":
    print("🎯 Bus Payments & Rewards System - Customer Offers Setup")
    print("=" * 60)
    print("This script will create 200 customer-specific offer activations")
    print("by linking existing customers to existing offer templates.")
    print("=" * 60)

    try:
        # Create and run the setup manager
        setup_manager = CustomerOffersSetupManager()
        setup_manager.setup_customer_offers()

        print("\n🎉 Customer offers setup completed successfully!")
        print("You can now test the customer-specific offers API endpoints.")

    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
