FROM python:3.11-slim

ARG BASE_URL=http://localhost:8000
ENV BASE_URL=$BASE_URL


WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Add cryptography explicitly
RUN pip install --no-cache-dir cryptography \
    && pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY static/ static/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
