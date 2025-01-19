#!/bin/bash

# Update package lists and install dependencies
echo "Setting up the environment..."

# Install dependencies using pip (if not using setup.py)
pip install -r requirements.txt

# Optionally, run any additional setup commands here, e.g., creating a virtual environment
python3 -m venv venv
source venv/bin/activate

echo "Setup complete!"
