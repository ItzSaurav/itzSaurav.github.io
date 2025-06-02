#!/bin/bash

# Activate virtual environment (uncomment if using venv)
# source venv/bin/activate

# Install required packages
python3 -m pip install requests feedparser beautifulsoup4 schedule

# Run the news updater in the background
python3 news_updater.py > news_updater.log 2>&1 &

# Save the process ID
echo $! > news_updater.pid

echo "News updater started with PID: $(cat news_updater.pid)" 