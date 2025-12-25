# Python 3.10 use karenge (Stable hai)
FROM python:3.10-slim-buster

# Logs dekhne ke liye setting
ENV PYTHONUNBUFFERED=1

# Folder set karo
WORKDIR /app

# --- SYSTEM DEPENDENCIES (FFmpeg Yahan Install Hoga) ---
# Ye step server par FFmpeg, Git aur Curl download karega
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- REQUIREMENTS INSTALL ---
# Pehle requirements copy karo taaki cache use ho sake
COPY requirements.txt .

# Python libraries install karo
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# --- COPY CODE ---
# Baaki saara code copy karo
COPY . .

# --- START COMMAND ---
# Bot start karne ka command
CMD ["python", "main.py"]
