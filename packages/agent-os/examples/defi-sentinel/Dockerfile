FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir \
    pydantic>=2.0.0 \
    && pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Default command
CMD ["python", "demo.py", "--attack", "all"]
