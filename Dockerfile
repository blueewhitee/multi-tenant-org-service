
# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.12-slim

# Set environment variables for better Python execution in Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if needed for potential future compiled libraries)
# For now, we keep it minimal.
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on (Cloud Run defaults to 8080, but we can configure it)
EXPOSE 8080

# Command to run the application using CMD
# We use host 0.0.0.0 to be accessible outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
