#!/bin/bash

# Check for proxy settings in the .env file and set them if available
set_proxy_from_env() {
    if [ -f ".env" ]; then
        source .env
        if [ ! -z "$HTTP_PROXY" ]; then
            export HTTP_PROXY=$HTTP_PROXY
            echo "HTTP Proxy set to: $HTTP_PROXY"
        else
            echo "No HTTP_PROXY found in .env file."
        fi

        if [ ! -z "$HTTPS_PROXY" ]; then
            export HTTPS_PROXY=$HTTPS_PROXY
            echo "HTTPS Proxy set to: $HTTPS_PROXY"
        else
            echo "No HTTPS_PROXY found in .env file."
        fi
    else
        echo ".env file not found. Proceeding without proxy settings."
    fi
}

# Check if .venv directory exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Set proxy from .env if available
set_proxy_from_env

# Install required packages
echo "Installing requirements..."
pip install -r requirements.txt

# Start the application
echo "Starting the application..."
uvicorn main:app --reload
