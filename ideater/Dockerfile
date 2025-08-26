# Backend Dockerfile for Ideater (FastAPI)
# Uses Python 3.11 slim with required native libs for some dependencies
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System packages for building and for libraries like WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    libffi-dev \
    libssl-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set workdir to the backend source folder
WORKDIR /app/ideater

# Install Python dependencies
COPY ideater/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application source
COPY ideater /app/ideater

# Environment defaults
ENV HOST=0.0.0.0 \
    PORT=8000 \
    APP_NAME=Ideater \
    CORS_ORIGINS="http://localhost:5173,http://localhost:8000,http://localhost:3000" \
    DATABASE_URL=sqlite:///ideater.db \
    ORACLE_WALLET_DIR=/opt/oracle/wallet

# Expose API port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
