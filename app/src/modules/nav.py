import streamlit as st

def UploadNav():
    st.sidebar.page_link("upload.py", label="S3 File Upload", icon="⬆️")


def DataNav():
    st.sidebar.page_link("pages/data.py", label="RDS Data Table", icon="🗒️")

def VizNav():
    st.sidebar.page_link("pages/visualize.py", label="RDS Data Visualization", icon="📊")