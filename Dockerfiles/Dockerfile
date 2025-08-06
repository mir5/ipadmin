# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app
# Copy project
COPY ./core /app

# Install system dependencies
# RUN apt-get update && apt-get install -y \
    # build-essential \
    # libpq-dev \
    # && rm -rf /var/lib/apt/lists/*

# Install pipenv or pip requirements
COPY /requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt



# Expose port (default Django port)
EXPOSE 8000

# Start Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]