# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the script to the container
COPY upload_monitor.py .

# Install required libraries
RUN pip install watchdog boto3

# Set environment variables (make these configurable at runtime)
ENV S3_ENDPOINT_URL=
ENV S3_ACCESS_KEY=
ENV S3_SECRET_KEY=
ENV S3_BUCKET_NAME=
ENV WATCH_DIR=./

# Command to run the script
CMD ["python", "upload_monitor.py"]
