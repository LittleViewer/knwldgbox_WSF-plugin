# ==========================================
# Stage 1: Build the Vue Frontend
# ==========================================
FROM node:20-slim AS frontend-builder
WORKDIR /app-src

# Install dependencies and build
COPY app/package*.json ./
RUN npm ci

COPY app/ ./
RUN VITE_API_PORT="" npm run build


# ==========================================
# Stage 2: Build the Python Backend
# ==========================================
FROM python:3.12-slim

# Prevent python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/lib/playwright

# Install system dependencies (Chromium for OSINT archiving/TikTok)
RUN apt-get update && apt-get install -y \
    chromium \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/knwldgbox

# Install Python dependencies
COPY backend/requirements.txt .
# Playwright needs to install its chromium binary if the system one isn't enough, 
# but using the system one saves space. We'll install python deps normally.
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# Copy backend code
COPY backend/ ./backend/

# Copy the built frontend from Stage 1
COPY --from=frontend-builder /app-src/dist ./app/dist/

# Set up data directory (this will be a mounted volume)
ENV XDG_DATA_HOME=/data
ENV KNWLDGBOX_HOME=/opt/knwldgbox
RUN mkdir -p /data/knwldgbox

# Expose the API port
EXPOSE 8000

# Create a non-root user for security
RUN useradd -r -u 10001 -m knwldg && chown -R knwldg:knwldg /opt/knwldgbox /data
USER knwldg

# Start FastAPI server binding to 0.0.0.0 (Docker networking handles isolation)
WORKDIR /opt/knwldgbox/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
