#!/bin/bash
set -e

# Get PORT from environment or default to 5000
PORT=${PORT:-5000}

# Start Gunicorn
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120

