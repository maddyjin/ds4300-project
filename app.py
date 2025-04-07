import streamlit as st
from helper import upload_to_s3, get_iam_token
import boto3
import pymysql
import os
from dotenv import load_dotenv
import pandas as pd

BUCKET_NAME = "ds4300-jamsters-project"

load_dotenv()
RDS_HOST = os.getenv("RDS_HOST")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")

# initialize s3 client
s3_client = boto3.client(
        "s3",
        region_name='us-east-2',
    )


# rds-induced chaos
connection = pymysql.connect(
            host=RDS_HOST,
            port=3306,
            user='admin',
            password=RDS_PASSWORD,
            database='file_data',
            autocommit=True
        )
with connection.cursor() as cursor:
    q = """SELECT 
            upload_time,
            type,
            SUM(size) OVER (PARTITION BY type ORDER BY upload_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_size
        FROM 
            uploaded_files
        ORDER BY 
            upload_time, type;
    """
    cursor.execute(q)
    running = pd.DataFrame(cursor.fetchall(), columns=['Timestamp', 'File Type', 'Size'])
    running['Size'] = running['Size'].astype(int)

    cursor.execute(f"SELECT * FROM uploaded_files")
    data = pd.DataFrame(cursor.fetchall(), 
                        columns=['idx', 'File Name', 'Size', 'File Type', 'Timestamp'])

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
    st.line_chart(running,
                  x='Timestamp',
                  y='Size',
                  color='File Type')

    
    st.dataframe(data)
    st.dataframe(running)

    


