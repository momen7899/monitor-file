import time
import os
import boto3
from botocore.exceptions import NoCredentialsError
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration for S3-compatible storage
# These should be set as environment variables in your Docker container for security
endpoint_url = os.environ.get('S3_ENDPOINT_URL')
access_key = os.environ.get('S3_ACCESS_KEY')
secret_key = os.environ.get('S3_SECRET_KEY')
bucket_name = os.environ.get('S3_BUCKET_NAME')
directory_to_watch = os.environ.get('WATCH_DIR', './data/watch')  # Default to current directory if not set

# Create an S3 client
session = boto3.session.Session()
s3_client = session.client(
    service_name='s3',
    region_name='',  # Example region
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)

class FileUploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Check if the created event is for a file
        if event.is_directory:
            return  # Ignore directories
        
        # File created, so we upload it
        file_path = event.src_path
        if self.is_ignored_file(file_path):
            print(f"Ignored file: {file_path}")
            return

        # File created, so upload it
        self.upload_file(file_path)

    def on_modified(self, event):
        # Check if the modified event is for a file
        if event.is_directory:
            return  # Ignore directories

        file_path = event.src_path
        if self.is_ignored_file(file_path):
            print(f"Ignored modified file: {file_path}")
            return

        # File modified, save it
        self.upload_file(file_path, update=True)

    def upload_file(self, file_path, update=False):
        file_name = os.path.basename(file_path)
        try:
            s3_client.upload_file(file_path, bucket_name, file_name)
            action = "Updated" if update else "Uploaded"
            print(f"{action}: {file_name} to {bucket_name}.")
        except NoCredentialsError:
            print("Credentials not available for S3 upload.")

    @staticmethod
    def is_ignored_file(file_path):
        # Ignore files based on extension or patterns
        ignored_extensions = {".swp", ".tmp", ".bak", ".swx"}  # Add more extensions as needed
        file_name = os.path.basename(file_path)
        return any(file_name.endswith(ext) for ext in ignored_extensions)


if __name__ == "__main__":
    event_handler = FileUploadHandler()
    observer = Observer()
    observer.schedule(event_handler, path=directory_to_watch, recursive=False)

    try:
        observer.start()
        print(f"Monitoring {directory_to_watch} for file changes...")
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
