FROM python:3.12-slim

# ffmpeg = HD video merge + mp3 er jonno
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# Download gulo ekhane jabe (volume kora jay)
ENV DOWNLOAD_DIR=/app/downloads
RUN mkdir -p /app/downloads

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# Production e uvicorn, multiple worker
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
