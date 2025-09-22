#!/usr/bin/env python3
"""
Schema Setup Runner
Simple script to run schema setup operations
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from schema_setup import SchemaSetupManager

def main():
    """Run schema setup with default create action"""
    print("🚀 Running database schema setup...")

    schema_manager = SchemaSetupManager()
    schema_manager.setup_schema()

if __name__ == "__main__":
    main()
