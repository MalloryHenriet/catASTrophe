FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

# Create /usr/bin/test-db to point to main.py using Python
RUN echo '#!/bin/sh\nexec python /app/main.py "$@"' > /usr/bin/test-db \
    && chmod +x /usr/bin/test-db

ENTRYPOINT ["/usr/bin/test-db"]


#build image with: docker build -t fuzzer-db .
#then run : docker run --rm -v $(pwd)/shared:/data --network host fuzzer-db -r 100
