"""
LinkedIn Enhancer - AI-Powered Profile Optimization and Career Guidance
Main application entry point
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the Streamlit app
from src.ui.streamlit_app import main

if __name__ == "__main__":
    main() 