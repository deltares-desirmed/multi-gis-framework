import json
import ee
import streamlit as st

def initialize_earth_engine():
    try:
        key_dict = json.loads(st.secrets["GEE_KEY"])
        credentials = ee.ServiceAccountCredentials(
            key_dict["client_email"], key_data=key_dict
        )
        ee.Initialize(credentials)
        st.success("Earth Engine initialized successfully!")
    except Exception as e:
        st.error(f"Failed to initialize Earth Engine: {e}")
