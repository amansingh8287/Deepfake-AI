FROM python:3.11-slim

WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend /app/backend
COPY models /app/models
COPY uploads /app/uploads
COPY reports /app/reports
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

