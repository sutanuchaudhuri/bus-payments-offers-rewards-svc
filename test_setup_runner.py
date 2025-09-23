#!/usr/bin/env python3
"""
Simple test runner to verify the database setup works
"""
import sys
import os
import traceback

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_test():
    try:
        print("🔧 Starting database setup test...")

        # Import the setup class
        from data_setup.comprehensive_setup import ComprehensiveDatabaseSetup

        # Create setup instance with purge flag
        setup = ComprehensiveDatabaseSetup(purge_existing=True)

        # Run the setup
        success = setup.run_setup()

        if success:
            print("✅ Database setup completed successfully!")
        else:
            print("❌ Database setup failed!")

        return success

    except Exception as e:
        print(f"❌ Error running setup: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
