#!/bin/sh

# Infinite loop to run the Python script every 60 minutes
while true; do
    python /app/main.py
    echo "Script execution completed. Sleeping for 60 minutes..."
    sleep 3600  # Sleep for 60 minutes
done-