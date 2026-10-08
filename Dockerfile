# Dockerfile
# Use an official Python runtime as a parent image (Slim version for smaller footprint)
FROM python:3.12-slim

# Set environment variables to optimize Python execution in containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user for security compliance
RUN adduser --disabled-password --gecos "" appuser

# Set the working directory within the container
WORKDIR /app

# Copy only the requirements first to leverage Docker layer caching
COPY requirements.txt /app/

# Install Python dependencies without storing the cache to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual application code
COPY ./app /app/app

# Transfer ownership of the application files to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]