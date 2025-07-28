# Use a specific Python version for consistency with platform specification
FROM --platform=linux/amd64 python:3.11-slim

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for ML libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with optimizations for PyTorch
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files into the container
COPY . .

# Remove unnecessary files to reduce image size
RUN find . -type f -name "*.pyc" -delete && \
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find . -type f -name "*.swp" -delete && \
    rm -f .git* .dockerignore Dockerfile* || true

# Create output directory for results
RUN mkdir -p /app/output

# This command will be executed when the container runs
# The user will provide the collection directory as an argument
ENTRYPOINT ["python", "run_analysis.py"]
