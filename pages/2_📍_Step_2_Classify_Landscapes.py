import streamlit as st
import leafmap.foliumap as leafmap
import folium
import os
import requests
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

st.title("Landscape Characters - Community Systems Explorer")

# ✅ GitHub Raw Base URL for GeoJSON Files
github_base_url = "https://raw.githubusercontent.com/deltares-desirmed/multi-gis-framework/main/database/"

# 📚 Community Systems Files (Use GeoJSON Where Available)
community_files = {
    "Hospitals": "EU_healthservices.geojson",
    # Add other converted files here, e.g., "Schools": "EU_education.geojson"
}

# 🌍 Create Map Centered on Europe
m = leafmap.Map(center=[50, 10], zoom=5)

# 📥 Load and Add Community Systems Layers from GeoJSON
for system_name, filename in community_files.items():
    geojson_url = os.path.join(github_base_url, filename)
    try:
        response = requests.get(geojson_url)
        response.raise_for_status()
        geojson_data = response.json()

        # ✅ Create a Feature Group and Marker Cluster
        fg = folium.FeatureGroup(name=system_name, show=False)
        marker_cluster = MarkerCluster().add_to(fg)

        # 📍 Plot each feature in the GeoJSON safely
        for feature in geojson_data.get("features", []):
            geometry = feature.get("geometry")
            if geometry and geometry.get("type") == "Point":
                coords = geometry.get("coordinates")
                if coords and len(coords) >= 2:
                    lon, lat = coords[:2]  # GeoJSON always uses [lon, lat]

                    props = feature.get("properties", {})
                    name = props.get('hospital_name') or props.get('site_name') or 'N/A'

                    popup_info = f"""
                    <b>{system_name}</b><br>
                    Name: {name}<br>
                    Address: {props.get('address', 'N/A')}<br>
                    City: {props.get('city', 'N/A')}<br>
                    Capacity (Beds): {props.get('cap_beds', 'N/A')}<br>
                    Type: {props.get('facility_type', 'N/A')}
                    """

                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_info, max_width=300),
                        icon=folium.Icon(color="blue", icon="info-sign"),
                    ).add_to(marker_cluster)
            else:
                # Optionally log skipped invalid or missing geometries if needed
                continue

        m.add_child(fg)

    except Exception as e:
        st.error(f"❌ Failed to load '{system_name}': {e}")

# 🧩 Add Layer Control and Display Map
m.add_layer_control()
m.to_streamlit(height=700)





# 🌍 Add Base Layers (Optional)
# regions = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_regions.geojson"
# m.add_geojson(regions, layer_name="US Regions")

