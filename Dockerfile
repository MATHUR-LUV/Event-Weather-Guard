# 1. Use an official Python runtime as a parent image
# Slim version is smaller and more secure for production
FROM python:3.12-slim

# 2. Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
# Ensures the app folder is in the Python Path
ENV PYTHONPATH=/app

# 3. Set the working directory in the container
WORKDIR /app

# 4. Install system dependencies
# This ensures that even on bare-bones Linux servers, 
# common network tools are available for the app.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python dependencies
# We copy requirements first to leverage Docker's layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Expose the port the app runs on
EXPOSE 8000

# 8. Define the command to run the app
# 0.0.0.0 is crucial; it allows the container to accept external traffic
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]