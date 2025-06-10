FROM theosotr/sqlite3-test

# Switch to root to install system packages
USER root

# Install Python and required tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install sqlparse

# Set working directory
WORKDIR /reducer

# Copy reducer source code
COPY reducer.py reducer.py
COPY code/ code/

# Make reducer.py executable and link it
RUN chmod +x reducer.py && ln -s /reducer/reducer.py /usr/bin/reducer

RUN ln -s /reducer/reducer.py /reducer/reducer

# Optionally switch back to original user (uncomment if you know the user)
# USER sqlite

# Default command
CMD ["/bin/bash"]

