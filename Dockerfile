# Multi-stage build for production

# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY vite.config.js tailwind.config.js postcss.config.js ./
COPY src ./src
COPY index.html ./

# Install dependencies and build
RUN npm ci && npm run build


# Stage 2: Build backend with frontend assets
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir torch==2.1.2+cpu --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt
# Copy backend code
COPY app ./app

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/app/static/dist ./app/static/dist

# Create necessary directories
RUN mkdir -p app/static app/Storage data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:rag_api", "--host", "0.0.0.0", "--port", "8000"]
