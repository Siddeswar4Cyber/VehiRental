# Start from official Python image with Debian base
FROM python:3.12-slim

# Install system dependencies needed for mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your code into the container
COPY . .

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set command to run the Flask app
CMD ["python", "app.py"]
