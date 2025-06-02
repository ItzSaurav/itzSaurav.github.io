#!/bin/bash

# Activate virtual environment if you're using one
# source venv/bin/activate

# Install required packages
pip install requests feedparser beautifulsoup4 schedule

# Run the news updater
python news_updater.py > news_updater.log 2>&1 &

# Save the process ID
echo $! > news_updater.pid

echo "News updater started with PID: $(cat news_updater.pid)" 