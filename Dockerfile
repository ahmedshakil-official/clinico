FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install dependencies (only what you need)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn uvicorn[standard]

COPY install-weasyprint-deps.sh /app/
#RUN chmod +x /app/install-weasyprint-deps.sh && /app/install-weasyprint-deps.sh

COPY . /app/

EXPOSE 8000