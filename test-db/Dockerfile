# Use a base image (e.g., Python image)
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your Python script that interacts with SQLite into the container
COPY . .

# Install any dependencies you need (e.g., SQLite3 for Python)
RUN pip install --no-cache-dir -r requirements.txt

# Command to run when the container starts (replace with your own entrypoint)
CMD ["python", "interact_with_sqlite.py"]



# # Use an official Ubuntu as a base image
# FROM ubuntu:22.04

# # Set environment variables for non-interactive installation
# ENV DEBIAN_FRONTEND=noninteractive

# # Install necessary dependencies and SQLite versions
# RUN apt-get update && apt-get install -y \
#     wget \
#     build-essential \
#     libreadline-dev \
#     libssl-dev \
#     zlib1g-dev \
#     && apt-get clean

# # Download and install SQLite 3.26.0
# RUN wget https://sqlite.org/2018/sqlite-autoconf-3260000.tar.gz && \
#     tar xzf sqlite-autoconf-3260000.tar.gz && \
#     cd sqlite-autoconf-3260000 && \
#     ./configure && \
#     make && \
#     make install

# # Download and install SQLite 3.39.4 (corrected URL)
# RUN wget https://sqlite.org/2023/sqlite-autoconf-3390400.tar.gz && \
#     tar xzf sqlite-autoconf-3390400.tar.gz && \
#     cd sqlite-autoconf-3390400 && \
#     ./configure && \
#     make && \
#     make install

# # Set working directory for the SQLite3 test
# WORKDIR /sqlite

# # Define entrypoint for SQLite3 commands
# ENTRYPOINT ["/usr/bin/sqlite3"]
