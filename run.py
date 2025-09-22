#!/usr/bin/env python3
"""
Main application runner
"""
import sys
import os

# Add the current directory to Python path for app imports
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Note: Database tables are created and populated by the separate data setup script
    # located in data-setup/comprehensive_data_setup.py

    # Run the application on port 5001 (matching app.py configuration)
    app.run(debug=True, host='0.0.0.0', port=5001)
