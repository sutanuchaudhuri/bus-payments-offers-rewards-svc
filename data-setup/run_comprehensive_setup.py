#!/usr/bin/env python3
"""
Simple runner for the comprehensive database setup
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_setup import main

if __name__ == "__main__":
    print("🎯 Bus Payments & Rewards System - Database Setup Runner")
    print("=" * 60)

    # If no arguments provided, show help
    if len(sys.argv) == 1:
        print("Available options:")
        print("  python run_comprehensive_setup.py            # Create new database")
        print("  python run_comprehensive_setup.py --purge    # Recreate with backup")
        print("  python run_comprehensive_setup.py --help     # Show detailed help")
        print("\nStarting with default setup (create new database)...")
        print("=" * 60)

    main()
