FROM python:3.10-slim-bookworm

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install Node.js + FFmpeg
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs ffmpeg git \
    && node -v \
    && npm -v \
    && ffmpeg -version \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
