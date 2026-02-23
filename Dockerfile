# Recipe Assistant Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY database.py .
COPY services.py .
COPY api.py .
COPY static/ ./static/

# Create directory for database
RUN mkdir -p /data

# Expose port
EXPOSE 8000

# Environment variables (can be overridden)
ENV ANTHROPIC_API_KEY=""
ENV DATABASE_PATH="/data/recipe_assistant.db"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
