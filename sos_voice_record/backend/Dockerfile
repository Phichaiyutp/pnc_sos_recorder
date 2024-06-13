FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create directories for app, utils, and media
RUN mkdir -p /main/app /main/utils /main/media

# Set the working directory
WORKDIR /main/app

# Copy the application code
COPY ./app /main/app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
