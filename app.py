import streamlit as st
from helper import load_env_variables, upload_to_s3
import boto3

BUCKET_NAME = "ds4300-jamsters-project"

# # load aws credentials
# aws_credentials = load_env_variables()

# # verify credentials
# if not aws_credentials["aws_access_key_id"]:
#     raise ValueError("No AWS Access key id set")
# if not aws_credentials["aws_secret_access_key"]:
#     raise ValueError("No AWS Secret Access key set")
# if not aws_credentials["aws_region"]:
#     raise ValueError("No AWS Region Set")
# if not aws_credentials["s3_bucket_name"]:
#     raise ValueError("S3_BUCKET_NAME environment variable is not set")

# initialize client
s3_client = boto3.client(
        "s3",
        # aws_access_key_id=aws_credentials["aws_access_key_id"],
        # aws_secret_access_key=aws_credentials["aws_secret_access_key"],
        region_name='us-east-2',
    )

# upload files via streamlit
uploads = st.file_uploader(
    "Choose files to upload:", accept_multiple_files=True
)

# upload
for file in uploads:
    st.write("Processing", file.name)
    e = upload_to_s3(s3_client, file, BUCKET_NAME)
    st.write(e)

