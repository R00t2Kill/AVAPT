# 1️⃣ Use a Python base image
FROM python:3.11-slim

# 2️⃣ Set working directory inside container
WORKDIR /app

# 3️⃣ Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4️⃣ Copy requirements and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 5️⃣ Copy entrypoint script and make executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 6️⃣ Copy app and scripts
COPY app /app/app
COPY scripts /app/scripts

# 7️⃣ Expose ports for FastAPI and Streamlit
EXPOSE 8000 8501

# 8️⃣ Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
