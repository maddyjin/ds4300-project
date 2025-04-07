import streamlit as st
from helper import upload_to_s3, get_iam_token
import boto3
import pymysql


BUCKET_NAME = "ds4300-jamsters-project"

# initialize s3 client
s3_client = boto3.client(
        "s3",
        region_name='us-east-2',
    )


# rds-induced chaos
RDS_HOST = 'ds4300-jamsters-project-2.chm4484qs1an.us-east-2.rds.amazonaws.com'
password = get_iam_token(RDS_HOST)
connection = pymysql.connect(
            host=RDS_HOST,
            port=3306,
            user='admin',
            password=password,
            autocommit=True
        )
with connection.cursor() as cursor:
    cursor.execute(f"SELECT * FROM file_uploads")
    data = cursor.fetchall()

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
    st.dataframe(data)

    


