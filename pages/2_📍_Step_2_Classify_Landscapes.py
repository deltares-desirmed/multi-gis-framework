import streamlit as st
import leafmap.foliumap as leafmap
import folium
import os
import requests
from folium.plugins import MarkerCluster
import re
import pandas as pd

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

import os
import re
import json
import requests
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import leafmap.foliumap as leafmap
import streamlit as st

# GitHub Raw Base URL for GeoJSON files
github_base_url = "https://raw.githubusercontent.com/deltares-desirmed/multi-gis-framework/main/database/"
local_base_path = "https://raw.githubusercontent.com/deltares-desirmed/multi-gis-framework/main/database/"  # Folder for local .feather files

# Automatically detect available files
available_files = os.listdir(local_base_path)
layer_files = [f for f in available_files if f.endswith((".geojson", ".feather"))]

# Create the map
m = leafmap.Map(center=[50, 10], zoom=5)

# Load and add each community system layer
for filename in layer_files:
    system_name = re.sub(r'[_\.]', ' ', os.path.splitext(filename)[0]).title()

    try:
        if filename.endswith(".feather"):
            filepath = os.path.join(local_base_path, filename)
            gdf = gpd.read_feather(filepath)

        elif filename.endswith(".geojson"):
            geojson_url = os.path.join(github_base_url, filename)
            response = requests.get(geojson_url)
            response.raise_for_status()
            gdf = gpd.GeoDataFrame.from_features(response.json()["features"])

        else:
            continue  # Unsupported format

        # Convert GeoDataFrame to __geo_interface__ for folium
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

# Add controls and display
m.add_layer_control()
m.to_streamlit(height=700)






# 🌍 Add Base Layers (Optional)
# regions = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_regions.geojson"
# m.add_geojson(regions, layer_name="US Regions")

