# Use the official Python slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the application port
EXPOSE 8000

# Run the Django application
CMD ["gunicorn", "-b", "0.0.0.0:8000", "myproject.wsgi:application"]
