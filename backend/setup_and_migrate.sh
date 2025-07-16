#!/bin/bash

# Asset Management Backend Setup and Migration Script

echo "Setting up backend environment..."

# Check if we're in the backend directory
if [ ! -f "alembic.ini" ]; then
    echo "Error: Please run this script from the backend directory"
    exit 1
fi

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found. Please create it first:"
    echo "python -m venv .venv"
    echo "source .venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Check if alembic is available
if ! command -v alembic &> /dev/null; then
    echo "Error: Alembic not found. Installing requirements..."
    pip install -r requirements.txt
fi

# Show current alembic version
echo "Alembic version: $(alembic --version)"

# Run migration
echo "Running database migration..."
alembic upgrade head

echo "Setup complete!" 