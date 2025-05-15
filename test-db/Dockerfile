
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

RUN chmod +x /app/main.py && ln -s /app/main.py /usr/bin/test-db

ENTRYPOINT ["test-db"]

#build image with: docker build -t fuzzer-db .
#then run : docker run --rm -v $(pwd)/shared:/data --network host fuzzer-db -r 100
