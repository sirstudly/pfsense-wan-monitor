FROM python:3.9-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apk add --no-cache \
    curl \
    bash \
    && rm -rf /var/cache/apk/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY wanmonitor.py .
COPY tapo_smart_plug.py .
COPY renew_dhcp.sh .
COPY install-wanmonitor.sh .

# Make scripts executable
RUN chmod +x renew_dhcp.sh install-wanmonitor.sh

# Create log directory
RUN mkdir -p /app/logs

# Set default command to keep container running
CMD ["tail", "-f", "/dev/null"]
# CMD ["python", "wanmonitor.py"]
