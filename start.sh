
#!/bin/bash

# Check if .venv directory exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# # Install required packages
# echo "Installing requirements..."
# pip install --proxy   -r requirements.txt

# # # Start the application
# echo "Starting the application..."
# uvicorn main:app --reload
