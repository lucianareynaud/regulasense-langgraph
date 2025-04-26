#!/bin/bash

# Load environment variables
if [ -f .env ]; then
  source .env
else
  echo "Warning: .env file not found. Using default configuration."
fi

# Start the application
docker-compose up --build 