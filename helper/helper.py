import os
from dotenv import load_dotenv

# Load the values from .env into dictionary
def load_env_variables():
    load_dotenv()
    return {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "s3_bucket_name": os.getenv("S3_BUCKET_NAME"),
    }


def upload_to_s3(s3_client, file, bucket_name):
    try:
        s3_client.upload_fileobj(file, bucket_name, f"uploads/{file.name}")
        return f'{file.name} uploaded successfully'
    except Exception as e:
        return f'an error occured while uploading {file.name}: {e}'