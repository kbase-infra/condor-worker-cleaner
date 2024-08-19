#!/bin/sh

# Infinite loop to run the Python script every 5 minutes
while true; do
    python /app/main.py
    echo "Script execution completed. Sleeping for 5 minutes..."
    sleep 300  # Sleep for 5 minutes (300 seconds)
done