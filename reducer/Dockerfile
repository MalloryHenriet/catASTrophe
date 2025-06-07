FROM python:3.9-slim

# Install required packages
RUN apt-get update && apt-get install -y sqlite3 bash && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /reducer

# Copy your source code
COPY reducer.py reducer.py
COPY code/ code/   
# Include the code/ directory used by reducer.py

# Install Python dependencies
RUN pip install sqlparse

# Make reducer.py executable and symlink it to /usr/bin/reducer
RUN chmod +x reducer.py && ln -s /reducer/reducer.py /usr/bin/reducer
