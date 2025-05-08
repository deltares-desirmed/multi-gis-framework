import json
import ee
import streamlit as st
from google.oauth2 import service_account

def initialize_earth_engine():
    try:
        # Retrieve the JSON credentials from Streamlit secrets
        key_dict = json.loads(st.secrets["GEE_KEY"])
        
        # Add custom scopes
        scopes = ['https://www.googleapis.com/auth/earthengine', 
                  'https://www.googleapis.com/auth/devstorage.read_write']
        
        # Create credentials object with specified scopes
        credentials = service_account.Credentials.from_service_account_info(
            key_dict, scopes=scopes
        )
        
        # Initialize Earth Engine with the credentials
        ee.Initialize(credentials)
        
        st.success("Earth Engine initialized successfully!")
    except Exception as e:
        st.error(f"Failed to initialize Earth Engine: {e}")
