#!/bin/bash

# Script to rebuild the dev container from scratch
# This is useful when encountering build issues

echo "🧹 Cleaning up Docker system..."
docker system prune -f

echo "🗑️ Removing any existing containers for this project..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down --remove-orphans

echo "🔨 Building dev container with no cache..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache

echo "✅ Dev container rebuild complete!"
echo "You can now try to reopen the project in the dev container."
