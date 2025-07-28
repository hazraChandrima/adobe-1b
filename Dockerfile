FROM python:3.10-slim-bullseye

WORKDIR /app

# Install only what's needed for pdfplumber
RUN apt-get update && apt-get install -y --no-install-recommends poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Upgrade pip and install dependencies with prebuilt wheels
RUN pip install --upgrade pip \
    && pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu \
    && pip install -r requirements.txt

CMD ["python", "run_analysis.py", "./Collection_1/"]
