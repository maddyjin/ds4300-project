import streamlit as st
from helper import upload_to_s3
import boto3

BUCKET_NAME = "ds4300-jamsters-project"

# initialize client
s3_client = boto3.client(
        "s3",
        region_name='us-east-2',
    )

tab1, tab2 = st.tabs(["S3 File Upload", "RDS Data Visualization"])

with tab1: 
    st.header("Upload files to S3")

    # upload files via streamlit
    uploads = st.file_uploader(
        "Choose files to upload:", accept_multiple_files=True
    )

    # upload
    for file in uploads:
        st.write("Processing", str(file.name) + '...')
        e = upload_to_s3(s3_client, file, BUCKET_NAME)
        st.write(e)

with tab2: 
    st.header("Data Visualization from RDS")

