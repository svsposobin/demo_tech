#!/bin/bash

set -e

echo "Applying database migrations..."
sleep 5
alembic upgrade head

echo "Starting application..."
exec python src/main.py
