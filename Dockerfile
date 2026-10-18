# Base Image: Python 3.11 slim (Sesuai SDD: Python 3.10 ke atas)
FROM python:3.11-slim

# Menetapkan working directory di dalam container
WORKDIR /app

# Mengatur environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependensi sistem jika diperlukan
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Salin requirements dan install dependencies Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode proyek ke dalam container
COPY . .

# Expose port FastAPI
EXPOSE 8000

# Perintah untuk menjalankan server FastAPI dengan Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
