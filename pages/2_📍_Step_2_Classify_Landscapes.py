import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
import folium
import os
from folium.plugins import MarkerCluster

st.set_page_config(layout="wide")

# 📌 Sidebar Info
st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | 
    [GitHub](https://github.com/deltares-desirmed) | 
    [Twitter](https://twitter.com/deltares) | 
    [YouTube](https://youtube.com/@deltares) | 
    [LinkedIn](https://www.linkedin.com/in/deltares)
    """
)

st.title("Landscape Characters)

# ✅ GitHub Raw Base URL for CSV Files
github_base_url = "https://raw.githubusercontent.com/deltares-desirmed/multi-gis-framework/main/database/"

# 📚 Community Systems CSV Files
community_files = {
    "Hospitals": "EU_healthservices.csv",
    "Schools": "EU_education.csv",
    # Add more datasets as needed
}

# 🌍 Create Map Centered on Europe
m = leafmap.Map(center=[50, 10], zoom=5)

# 📥 Load and Add Community Systems Layers with Marker Clustering
for system_name, filename in community_files.items():
    csv_url = os.path.join(github_base_url, filename)
    try:
        # Load CSV Data
        df = pd.read_csv(csv_url)

        if 'lat' in df.columns and 'lon' in df.columns:
            valid_df = df.dropna(subset=['lat', 'lon'])
            skipped = len(df) - len(valid_df)

            # ✅ Create a Feature Group and MarkerCluster
            fg = folium.FeatureGroup(name=system_name, show=False)
            marker_cluster = MarkerCluster().add_to(fg)

            for _, row in valid_df.iterrows():
                # Handle name fallback
                name = row.get('hospital_name') or row.get('site_name') or 'N/A'
                popup_info = f"""
                <b>{system_name}</b><br>
                Name: {name}<br>
                Address: {row.get('address', 'N/A')}<br>
                City: {row.get('city', 'N/A')}<br>
                Capacity (Beds): {row.get('cap_beds', 'N/A')}<br>
                Type: {row.get('facility_type', 'N/A')}
                """

                folium.Marker(
                    location=[row['lat'], row['lon']],
                    popup=folium.Popup(popup_info, max_width=300),
                    icon=folium.Icon(color="blue", icon="info-sign"),
                ).add_to(marker_cluster)

            m.add_child(fg)

            if skipped > 0:
                st.info(f"⚠️ {skipped} records without valid location skipped in '{system_name}' dataset.")
        else:
            st.warning(f"⚠️ '{system_name}' dataset missing required 'lat' and 'lon' columns.")

    except Exception as e:
        st.error(f"❌ Failed to load '{system_name}': {e}")

# 🧩 Add Layer Control and Display Map
m.add_layer_control()
m.to_streamlit(height=700)



# 🌍 Add Base Layers (Optional)
# regions = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_regions.geojson"
# m.add_geojson(regions, layer_name="US Regions")

# 🧩 Add Layer Control and Display Map
m.add_layer_control()
m.to_streamlit(height=700)
