FROM python:3.10-slim

# Install LibreOffice and Poppler for Word->PDF and PDF->Images conversions
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    poppler-utils \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "10000"]
