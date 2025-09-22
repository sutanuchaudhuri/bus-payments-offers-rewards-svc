#!/usr/bin/env python3
"""
Execute the comprehensive data setup script with better error handling
"""

import sys
import os
import traceback

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 Starting Bus Payments & Rewards System Data Setup")
    print("=" * 60)
    sys.stdout.flush()

    try:
        from comprehensive_data_setup import DataSetupManager

        print("📦 Initializing data manager...")
        sys.stdout.flush()

        data_manager = DataSetupManager()

        print("🔄 Setting up all data...")
        sys.stdout.flush()

        data_manager.setup_all_data()

        print("\n🎉 SUCCESS! All data has been created successfully!")
        print("\nYou can now:")
        print("• View customer C0001 (Sutanu Chaudhuri) in the system")
        print("• Test the three credit cards (Chase Sapphire, IHG Rewards, Amazon Visa)")
        print("• Use the tokenized cards for secure transactions")
        print("• Explore 500+ merchants across different categories")
        print("• Check out the 50 active offers")
        print("• Review 3000 historical transactions from the last 2 years")
        sys.stdout.flush()

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        print("Please check the error message above and try again.")
        sys.stdout.flush()
        sys.exit(1)

if __name__ == "__main__":
    main()
