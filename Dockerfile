# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for network monitoring
RUN apt-get update && apt-get install -y \
    build-essential \
    libpcap-dev \
    tcpdump \
    net-tools \
    iputils-ping \
    nmap \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')" || exit 1

# Run the application
# Use PORT env variable from Railway, default to 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
