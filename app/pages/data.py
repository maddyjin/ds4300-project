import streamlit as st
from helper import upload_to_s3, get_iam_token
import boto3
import pymysql
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import altair as alt
import random

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
        q = """WITH ranked_files AS (
                SELECT 
                    upload_time,
                    type,
                    size,
                    ROW_NUMBER() OVER (PARTITION BY upload_time, type ORDER BY size DESC) AS rn
                FROM 
                    uploaded_files
            )
            SELECT 
                upload_time,
                type,
                SUM(size) OVER (PARTITION BY type ORDER BY upload_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_size
            FROM 
                ranked_files
            WHERE 
                rn = 1
            ORDER BY 
                upload_time, type;

        """
        cursor.execute(q)
        running_df = pd.DataFrame(cursor.fetchall(), columns=['Timestamp', 'File Type', 'Size'])
        running_df['Size'] = running_df['Size'].astype(int)

        # every filetype listed should have row for every time listed
        # if there's no new dat at that time, it should reflect the most recent update



                # Get the most recent (largest) size for each file type
        latest_sizes = running_df.groupby('File Type')['Size'].max().reset_index()

        # Add new rows with current timestamp for each file type
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp
        new_rows = []
        for _, row in latest_sizes.iterrows():
            new_row = {
                'Timestamp': now,
                'File Type': row['File Type'],
                'Size': row['Size']
            }
            new_rows.append(new_row)

        # Convert new rows to DataFrame and append to the original running_df
        new_rows_df = pd.DataFrame(new_rows)
        running_df = pd.concat([running_df, new_rows_df], ignore_index=True)

        cursor.execute("SELECT * FROM uploaded_files")
        data_df = pd.DataFrame(cursor.fetchall(),
                               columns=['idx', 'File Name', 'Size', 'File Type', 'Timestamp'])

    return running_df, data_df

# Session state to trigger refresh
if 'refresh_data' not in st.session_state:
    st.session_state.refresh_data = True  # load once on start

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = set()



st.header("RDS Data Table")
if st.button("🔄 Refresh Data", key="refresh_table_button"):
    st.session_state.refresh_data = True

if not data.empty:
    st.dataframe(data)
else:
    st.write("No data to display.")