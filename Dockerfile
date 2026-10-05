# Production Dockerfile for DRDO EW Smart Scan (SENTINEL-EW) Tactical C2 Dashboard
FROM python:3.10-slim

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install lightweight CPU PyTorch wheel first to optimize container size and build speed
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install project dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and models
COPY ew_simulator/ ew_simulator/
COPY schedulers/ schedulers/
COPY metrics/ metrics/
COPY dataset/ dataset/
COPY models/ models/
COPY ui/ ui/
COPY cli.py .
COPY README.md .

# Expose unified dashboard port
EXPOSE 8080

# Health check to ensure simulation is active
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Launch unified Tactical EW Server
CMD ["python", "ui/server.py"]
