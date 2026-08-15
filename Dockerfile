FROM python:3.10-slim

# Install system dependencies required for PDF and document processing:
# - libreoffice: For Word (.doc/.docx) -> PDF conversion
# - poppler-utils: For PDF -> Image conversion (pdftoppm)
# - fonts-liberation: Standard font package for rendered PDFs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    poppler-utils \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency definition and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code into container
COPY . .

# Start the bot directly via long polling (no Webhook / FastAPI server needed)
CMD ["python", "bot.py"]
