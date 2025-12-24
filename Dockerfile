# Python ka base version use karenge
FROM python:3.10-slim

# Working directory set karenge
WORKDIR /app

# 🔥 FFmpeg aur Git install karenge (Sabse Zaroori Step)
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    apt-get clean

# Saari files copy karenge
COPY . .

# Requirements install karenge
RUN pip install --no-cache-dir -r requirements.txt

# Bot start karenge
CMD ["python", "main.py"]
