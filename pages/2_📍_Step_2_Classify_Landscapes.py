import os
import re
import requests
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import leafmap.foliumap as leafmap
import streamlit as st
from io import BytesIO

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

st.title("Landscape Characters - 3-domain")



# GitHub raw base URL
github_base_url = "https://raw.githubusercontent.com/deltares-desirmed/multi-gis-framework/main/database/"

# List of datasets hosted on GitHub (geojson or feather)
layer_files = [
    "EU_education.feather",
    "EU_healthservices.geojson"
    
]

# Create map centered on Europe
m = leafmap.Map(center=[50, 10], zoom=5)

# Load each layer from GitHub
for filename in layer_files:
    system_name = re.sub(r'[_\.]', ' ', os.path.splitext(filename)[0]).title()
    url = github_base_url + filename

    try:
        response = requests.get(url)
        response.raise_for_status()

        if filename.endswith(".geojson"):
            gdf = gpd.GeoDataFrame.from_features(response.json()["features"])

        elif filename.endswith(".feather"):
            gdf = gpd.read_feather(BytesIO(response.content))

        else:
            continue  # skip unsupported files

        # Convert to __geo_interface__ to allow folium rendering
        geojson_data = gdf.__geo_interface__

        fg = folium.FeatureGroup(name=system_name, show=True)
        marker_cluster = MarkerCluster().add_to(fg)

        for feature in geojson_data.get("features", []):
            geometry = feature.get("geometry")
            if geometry and geometry.get("type") == "Point":
                coords = geometry.get("coordinates")
                if coords and len(coords) >= 2:
                    lon, lat = coords[:2]
                    props = feature.get("properties", {})

                    popup_lines = [f"<b>{system_name}</b><br>"]
                    for key, value in props.items():
                        if pd.notna(value) and value != '':
                            key_clean = re.sub(r'[_\-]', ' ', key).title()
                            popup_lines.append(f"{key_clean}: {value}<br>")
                    popup_info = "".join(popup_lines)

                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_info, max_width=300),
                        icon=folium.Icon(color="blue", icon="info-sign"),
                    ).add_to(marker_cluster)

        m.add_child(fg)

    except Exception as e:
        st.error(f"Failed to load '{system_name}': {e}")

# Add layer controls and display
m.add_layer_control()
m.to_streamlit(height=700)







# 🌍 Add Base Layers (Optional)
# regions = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_regions.geojson"
# m.add_geojson(regions, layer_name="US Regions")

