import streamlit as st

def UploadNav():
    st.sidebar.page_link("upload.py", label="S3 File Upload", icon="⬆️")


def DataNav():
    st.sidebar.page_link("pages/data.py", label="RDS Data Table", icon="🗒️")

def VizNav():
    st.sidebar.page_link("pages/visualize.py", label="RDS Data Visualization", icon="📊")


def SideBarLinks():
    """
    This function handles adding links to the sidebar of the app based upon the logged-in user's role, which was put in the streamlit session_state object when logging in.
    """
    with st.sidebar:
        UploadNav()
        DataNav()
        VizNav()
