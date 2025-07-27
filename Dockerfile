# Multi-stage build for faster builds and smaller final image

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libsqlite3-dev \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/opt/venv -r requirements.txt

# Stage 2: Runtime image
FROM python:3.11-slim AS runtime

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libsqlite3-0 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /opt/venv /opt/venv

# Make sure scripts and packages in venv are usable
ENV PATH=/opt/venv/bin:$PATH
ENV PYTHONPATH=/opt/venv/lib/python3.11/site-packages:$PYTHONPATH

# Copy the application code
COPY . .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port (Cloud Run uses 8080)
EXPOSE 8080

# Start the FastAPI app using uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
