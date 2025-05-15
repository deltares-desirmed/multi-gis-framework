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

st.title("Landscape Characters")

# ✅ GitHub Raw Base URL
github_base_url = "https://raw.githubusercontent.com/deltares-desirmed/multi-gis-framework/main/database/"

# 📚 List all GeoJSON files dynamically (Hardcoded here, but can be automated via GitHub API)
geojson_files = ["EU_healthservices.geojson", "EU_education1.geojson", "EU_education2.geojson"]  # Add new files here or automate!

# 🌍 Create Map Centered on Europe
m = leafmap.Map(center=[50, 10], zoom=5)

# 📥 Load and Add Community Systems Layers Dynamically
for filename in geojson_files:
    system_name = re.sub(r'[_\.]', ' ', os.path.splitext(filename)[0]).title()  # Clean Layer Name
    geojson_url = os.path.join(github_base_url, filename)

    try:
        response = requests.get(geojson_url)
        response.raise_for_status()
        geojson_data = response.json()

        fg = folium.FeatureGroup(name=system_name, show=False)
        marker_cluster = MarkerCluster().add_to(fg)

        for feature in geojson_data.get("features", []):
            geometry = feature.get("geometry")
            if geometry and geometry.get("type") == "Point":
                coords = geometry.get("coordinates")
                if coords and len(coords) >= 2:
                    lon, lat = coords[:2]
                    props = feature.get("properties", {})

                    # 🧩 Dynamically build the popup content
                    popup_lines = [f"<b>{system_name}</b><br>"]
                    for key, value in props.items():
                        if pd.notna(value) and value != '':
                            # Format attribute key nicely: cap_beds → Capacity (Beds)
                            key_clean = re.sub(r'[_\-]', ' ', key).title()
                            popup_lines.append(f"{key_clean}: {value}<br>")
                    popup_info = "".join(popup_lines)

                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_info, max_width=300),
                        icon=folium.Icon(color="blue", icon="info-sign"),
                    ).add_to(marker_cluster)
            else:
                continue

        m.add_child(fg)

    except Exception as e:
        st.error(f"❌ Failed to load '{system_name}': {e}")

# 🧩 Add Layer Control and Display Map
m.add_layer_control()
m.to_streamlit(height=700)


import streamlit as st
import datetime
from zoneinfo import ZoneInfo  # Requires Python 3.9+

logo = "https://www.informatiehuismarien.nl/publish/pages/113886/deltares-logo.jpg"
st.sidebar.image(logo)

# Custom CSS to hide GitHub icon and other elements
# hide_github_icon = """
#     <style>
#         .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob, 
#         .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, 
#         .viewerBadge_text__1JaDK { display: none; } 
#         #MainMenu { visibility: hidden; } 
#         footer { visibility: hidden; } 
#         header { visibility: hidden; }
#     </style>
# """
# st.markdown(hide_github_icon, unsafe_allow_html=True)

# Amsterdam time
amsterdam_time = datetime.datetime.now(ZoneInfo("Europe/Amsterdam"))

# Footer content
current_year = amsterdam_time.year
st.sidebar.markdown(f"© {current_year}  Stichting Deltares")

# Display date and time in Amsterdam timezone
last_updated = amsterdam_time.strftime("%B %d, %Y")
current_time = amsterdam_time.strftime("%H:%M:%S")

st.sidebar.markdown(f"**Last Updated:** {last_updated} | {current_time}")
# st.sidebar.markdown(f"**Local Time (Amsterdam):** {current_time}")

# 🌍 Add Base Layers (Optional)
# regions = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_regions.geojson"
# m.add_geojson(regions, layer_name="US Regions")

