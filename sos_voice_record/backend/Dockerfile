FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /main

# Copy the application code
COPY ./app /main

# Create directories for utils and media
RUN mkdir -p /utils /media

# Copy requirements file and install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
