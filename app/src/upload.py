import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import streamlit as st
from helper.helper import upload_to_s3, get_iam_token
import boto3
import pymysql
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import altair as alt
import random
from modules.nav import SideBarLinks

SideBarLinks()

BUCKET_NAME = "ds4300-jamsters-project"

load_dotenv()
RDS_HOST = os.getenv("RDS_HOST")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")

# initialize s3 client
s3_client = boto3.client(
    "s3",
    region_name='us-east-2',
)

st.header("Upload files to S3")
with st.form("my-form", clear_on_submit=True):
    uploads = st.file_uploader(
        "Choose files to upload:", accept_multiple_files=True
    )
    for file in uploads:
        st.write("Processing", str(file.name) + '...')
        if file.name not in st.session_state.uploaded_files:
            e = upload_to_s3(s3_client, file, BUCKET_NAME)
            if e == 0:
                st.success(f'{file.name} uploaded successfully!')
                # print(file.name, type(file.name))
                # file_type = file.name.split(".")[-1]
                # file_name = file.name.split(".")[0].split("_")[:-1][0]
                # st.session_state.uploaded_files.add(str(file_name+"."+file_type))
            else:
                st.error(f'an error occured while uploading {file.name}: {e}')
    submitted = st.form_submit_button("submit")