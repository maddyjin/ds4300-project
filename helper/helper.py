import os
from dotenv import load_dotenv
import boto3
from botocore.config import Config
import random

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
    fn = file.name.split('.')
    fn[0] = fn[0] + '_' + str(random.getrandbits(128))
    file.name = '.'.join(fn)

    try:
        s3_client.upload_fileobj(file, bucket_name, f"uploads/{file.name}")
        return f'{file.name} uploaded successfully!'
    except Exception as e:
        return f'an error occured while uploading {file.name}: {e}'
    
def get_iam_token(RDS_HOST, RDS_PORT=3306, DB_USER='admin'):
    """Generate IAM authentication token"""
    client = boto3.client('rds', config=Config(region_name='us-east-2'))
    token = client.generate_db_auth_token(
        DBHostname=RDS_HOST,
        Port=RDS_PORT,
        DBUsername=DB_USER
    )
    return token