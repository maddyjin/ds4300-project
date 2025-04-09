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

st.title('Jamsters ETL Pipeline Dashboard')
tab1, tab2, tab3 = st.tabs(["S3 File Upload", "RDS Data Visualization", "RDS Data Table"])

with tab1:
    st.header("Upload files to S3")

    uploads = st.file_uploader(
        "Choose files to upload:", accept_multiple_files=True
    )
    for file in uploads:
        st.write("Processing", str(file.name) + '...')
        if file.name not in st.session_state.uploaded_files:
            e = upload_to_s3(s3_client, file, BUCKET_NAME)
            if e == 0:
                st.success(f'{file.name} uploaded successfully!')
                print(file.name, type(file.name))
                file_type = file_name.split(".")[-1]
                file_name = file_name.split(".")[0].split("_")[:-1][0]
                st.session_state.uploaded_files.add(str(file_name+"."+file_type))
            else:
                st.error(f'an error occured while uploading {file.name}: {e}')
    print(st.session_state.uploaded_files)

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
        running['Timestamp'] = pd.to_datetime(running['Timestamp'], errors='ignore')
        st.write(alt.Chart(running).mark_line().encode(
            x=alt.X('Timestamp:T', title='Time'),
            y=alt.Y('Size:Q', title='Total Uploaded Bytes'),
            color=alt.Color('File Type:N')
        ).properties(
            title='Total Uploaded Bytes by File Type'
        ).interactive())

        filecounts = data.value_counts('File Type').to_frame().reset_index()
        st.write(alt.Chart(filecounts).mark_bar().encode(
            y=alt.Y('File Type:N', title='File Type'),
            x=alt.X('count:Q', title='Number of Files'),
            color=alt.Color('File Type:N', legend=None)
        ).properties(
            title='Number of Files by File Type'
        ))
        # st.write(alt.Chart(data).mark_bar().encode(
        #         x=alt.X('Size:Q', title='Total Uploaded Bytes'),
        #         y=alt.Y('File Type:N').sort('-x'),
        #         color=alt.Color('File Type:N', legend=None)
        #     ).properties(
        #         title='Total Uploaded Bytes by File Type'
        #     )

                #  )

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