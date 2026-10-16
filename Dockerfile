FROM python:3.12-slim

WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source
COPY src/ ./src/

# Port
EXPOSE 8000

# Start
CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]