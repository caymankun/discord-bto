#!/bin/bash

# Update package list and install ffmpeg
apt-get update
apt-get install -y ffmpeg

# Install Python packages from requirements.txt
pip install -r requirements.txt

# Run the Python script
python main.py
