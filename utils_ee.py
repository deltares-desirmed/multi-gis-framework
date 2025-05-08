import ee
import streamlit as st
from google.oauth2 import service_account

def initialize_earth_engine():
    try:
        # Secrets are already a dictionary now, no need to json.loads
        key_dict = dict(st.secrets)

        # Define required scopes
        scopes = [
            "https://www.googleapis.com/auth/earthengine",
            "https://www.googleapis.com/auth/devstorage.read_write"
        ]

        # Authenticate using service account credentials
        credentials = service_account.Credentials.from_service_account_info(
            key_dict, scopes=scopes
        )
        ee.Initialize(credentials)
        st.success("Earth Engine initialized successfully!")

    except Exception as e:
        st.error(f"Failed to initialize Earth Engine: {e}")
