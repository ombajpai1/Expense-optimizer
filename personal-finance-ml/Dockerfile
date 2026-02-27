# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy the project code
COPY . /app/

# Expose port 8000 for the app
EXPOSE 8000

# Start command (using gunicorn for production, but manage.py runserver is also perfectly fine for local dev)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
