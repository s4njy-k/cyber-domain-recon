FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Ensure browsers are installed
RUN playwright install chromium

COPY . .

EXPOSE 8000

# Set Python to run unbuffered
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "8000"]
