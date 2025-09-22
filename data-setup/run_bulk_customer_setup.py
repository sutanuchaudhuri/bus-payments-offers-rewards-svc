#!/usr/bin/env python3
"""
Bulk Customer Setup Runner
Simple script to run the bulk customer setup for 500 customers
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from bulk_customer_setup import BulkCustomerSetupManager

def main():
    """Run bulk customer setup"""
    print("🚀 Running bulk customer setup for 500 customers...")
    print("⚠️  Note: This process may take 5-10 minutes to complete.")
    print("=" * 60)

    bulk_manager = BulkCustomerSetupManager()
    bulk_manager.setup_bulk_customers()

if __name__ == "__main__":
    main()
