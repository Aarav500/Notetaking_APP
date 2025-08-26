# Use Oracle Linux as base image for better compatibility with OCI
FROM oraclelinux:8-slim

# Set working directory
WORKDIR /app

# Install Python and required system dependencies
RUN dnf -y install python39 python39-devel gcc oracle-instantclient-release-el8 && \
    dnf -y install oracle-instantclient-basic oracle-instantclient-devel && \
    dnf clean all

# Set environment variables for Oracle Instant Client
ENV LD_LIBRARY_PATH=/usr/lib/oracle/21/client64/lib:${LD_LIBRARY_PATH}
ENV ORACLE_HOME=/usr/lib/oracle/21/client64
ENV PATH=$PATH:$ORACLE_HOME/bin

# Install pip and upgrade it
RUN python3.9 -m ensurepip && \
    python3.9 -m pip install --no-cache-dir --upgrade pip

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN python3.9 -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user to run the application
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python3.9", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]