# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (e.g., nmap)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy scripts & app
COPY app /app/app
COPY scripts /app/scripts

# Copy entrypoint script and make executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose both backend and Streamlit ports
EXPOSE 8000 8501

# Entrypoint runs both FastAPI & Streamlit
ENTRYPOINT ["/app/entrypoint.sh"]
