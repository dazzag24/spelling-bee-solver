# Dockerfile
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code from local app/ → container /app/
COPY app/. .

RUN mkdir -p /app/uploads

CMD ["python", "app.py"]
