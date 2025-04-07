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

# Function to query RDS data
def query_rds_data():
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
        running_df = pd.DataFrame(cursor.fetchall(), columns=['Timestamp', 'File Type', 'Size'])
        running_df['Size'] = running_df['Size'].astype(int)

        cursor.execute("SELECT * FROM uploaded_files")
        data_df = pd.DataFrame(cursor.fetchall(),
                               columns=['idx', 'File Name', 'Size', 'File Type', 'Timestamp'])

    return running_df, data_df


# Session state to trigger refresh
if 'refresh_data' not in st.session_state:
    st.session_state.refresh_data = True  # load once on start

# Tabs
tab1, tab2, tab3 = st.tabs(["S3 File Upload", "RDS Data Visualization", "RDS Data Table"])

# First tab: S3 uploads
with tab1:
    st.header("Upload files to S3")

    uploads = st.file_uploader(
        "Choose files to upload:", accept_multiple_files=True
    )

    for file in uploads:
        st.write("Processing", str(file.name) + '...')
        e = upload_to_s3(s3_client, file, BUCKET_NAME)
        st.write(e)

if st.session_state.refresh_data:
    running, data = query_rds_data()
    st.session_state.running = running
    st.session_state.data = data
    st.session_state.refresh_data = False  # Reset the flag after refreshing
else:
    running = st.session_state.get('running', pd.DataFrame())
    data = st.session_state.get('data', pd.DataFrame())


with tab2:
    st.header("Data Visualization from RDS")
    if st.button("🔄 Refresh Data", key="refresh_chart_button"):
        st.session_state.refresh_data = True

    if not running.empty:
        st.line_chart(running,
                      x='Timestamp',
                      y='Size',
                      color='File Type')
    else:
        st.write("No data to display.")

with tab3:
    st.header("RDS Data Table")
    if st.button("🔄 Refresh Data", key="refresh_table_button"):
        st.session_state.refresh_data = True

    if not data.empty:
        st.dataframe(data)
    else:
        st.write("No data to display.")