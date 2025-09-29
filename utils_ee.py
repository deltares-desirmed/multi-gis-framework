import ee
import streamlit as st
from google.oauth2 import service_account 

def initialize_earth_engine():
    try:
        key_dict = {
            "type": st.secrets["GEE_KEY_TYPE"],
            "project_id": st.secrets["GEE_PROJECT_ID"],
            "private_key_id": st.secrets["GEE_PRIVATE_KEY_ID"],
            "private_key": st.secrets["GEE_PRIVATE_KEY"],
            "client_email": st.secrets["GEE_CLIENT_EMAIL"],
            "client_id": st.secrets["GEE_CLIENT_ID"],
            "auth_uri": st.secrets["GEE_AUTH_URI"],
            "token_uri": st.secrets["GEE_TOKEN_URI"],
            "auth_provider_x509_cert_url": st.secrets["GEE_AUTH_PROVIDER_X509_CERT_URL"],
            "client_x509_cert_url": st.secrets["GEE_CLIENT_X509_CERT_URL"],
            "universe_domain": st.secrets["GEE_UNIVERSE_DOMAIN"],
        }

        credentials = service_account.Credentials.from_service_account_info(
            key_dict,
            scopes=[
                "https://www.googleapis.com/auth/earthengine",
                "https://www.googleapis.com/auth/devstorage.read_write"
            ]
        )
        ee.Initialize(credentials)
        st.success("Earth Engine initialized successfully!")
    except Exception as e:
        st.error(f"Earth Engine initialization failed: {e}")
