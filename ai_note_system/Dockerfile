FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Oracle Instant Client
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ffmpeg \
    tesseract-ocr \
    graphviz \
    libaio1 \
    wget \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Oracle Instant Client
RUN mkdir -p /opt/oracle
WORKDIR /opt/oracle
RUN wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip && \
    unzip instantclient-basiclite-linuxx64.zip && \
    rm instantclient-basiclite-linuxx64.zip && \
    cd /opt/oracle/instantclient* && \
    echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig

# Set environment variables for Oracle
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient*:$LD_LIBRARY_PATH
ENV PATH=/opt/oracle/instantclient*:$PATH

# Return to app directory
WORKDIR /app

# Copy requirements and installation script
COPY requirements.txt install.py ./

# Copy the entire application
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Initialize the database
RUN python data/init_db.py

# Create a volume for data persistence
VOLUME /app/data

# Create a volume for configuration
VOLUME /app/config

# Expose the port for the web interface (if implemented)
EXPOSE 8000

# Set environment variable for Docker
ENV PANSOPHY_ENV=production

# Run the application
CMD ["python", "main.py"]

# Usage instructions:
# Build the image:
#   docker build -t pansophy .
#
# Run the container:
#   docker run -it --name pansophy-app \
#     -v /path/to/local/data:/app/data \
#     -v /path/to/local/config:/app/config \
#     -p 8000:8000 \
#     pansophy
#
# Run a specific command:
#   docker run -it --rm \
#     -v /path/to/local/data:/app/data \
#     -v /path/to/local/config:/app/config \
#     pansophy python main.py process --input "Your text here" --type text