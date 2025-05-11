import streamlit as st
import leafmap.foliumap as leafmap
import ee
import os
import datetime

# Set up Streamlit page config
st.set_page_config(layout="wide", page_title="Split Map & 3D Visualization")

# Set MapTiler API key for 3D Terrain visualization
os.environ["MAPTILER_KEY"] = "iiyRi7eIx4NmHrMOEZsc"

# Sidebar Info
st.sidebar.title("About This Platform")
st.sidebar.info(
    """
    Multi-GIS Support Platform for DesirMED (Tasks 4.1, 4.2, 4.4) and NBRACER (D5.1, D5.3, D5.5).  
    Developed by Deltares | [wetlands.io](https://wetlands.io)
    """
)

# Footer with Last Updated Date
current_date = datetime.datetime.now().strftime("%B %d, %Y")
st.sidebar.markdown(f"📅 **Last Updated:** {current_date}")

# Main Title
st.title("🗺️ Split Map and 🌍 3D Geospatial Visualization")

# --------------------------
# SPLIT PANEL MAP SECTION
# --------------------------
st.header("🔀 Split-Panel Map Visualization")
with st.expander("See Source Code for Split Map"):
    with st.echo():
        m_split = leafmap.Map()
        m_split.split_map(
            left_layer="ESA WorldCover 2020 S2 FCC", right_layer="ESA WorldCover 2020"
        )
        m_split.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")

m_split.to_streamlit(height=600)

# --------------------------
# 3D VISUALIZATION SECTIONS
# --------------------------
st.header("🌐 3D Globe Projection with Overture 3D Buildings")
m1 = leafmap.Map(center=[-100, 40], zoom=3, style="positron", projection="globe")
m1.add_overture_3d_buildings()
m1.add_basemap("Esri.WorldImagery")
m1.add_layer_control()
m1.to_streamlit(height=600)

st.header("🛰️ ESA Land Cover Visualization (Earth Engine)")
m2 = leafmap.Map(style="3d-terrain", projection="globe")
m2.add_ee_layer(asset_id="ESA/WorldCover/v200", opacity=0.5)
m2.add_legend(builtin_legend="ESA_WorldCover", title="ESA Landcover")
m2.add_overture_3d_buildings()
m2.add_layer_control()
m2.to_streamlit(height=600)

st.header("🌱 Land Cover Data (ESA WorldCover) with Legend")
m3 = leafmap.Map(style="3d-terrain", projection="globe")
dataset = ee.ImageCollection("ESA/WorldCover/v200").first()
vis_params = {"bands": ["Map"]}
m3.add_ee_layer(dataset, vis_params, name="ESA Worldcover", opacity=0.5)
m3.add_legend(builtin_legend="ESA_WorldCover", title="ESA Landcover")
m3.add_layer_control()
m3.to_streamlit(height=600)

st.header("🌃 Nighttime Light Data (NOAA VIIRS)")
m4 = leafmap.Map(style="darkmatter", projection="globe")
night_dataset = ee.ImageCollection("NOAA/VIIRS/DNB/ANNUAL_V22").filter(
    ee.Filter.date("2022-01-01", "2023-01-01")
)
nighttime = night_dataset.select("maximum")
night_vis = {"min": 0.0, "max": 60.0}
m4.add_ee_layer(nighttime, night_vis, name="Nighttime Lights")

countries = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017")
style_params = {"fillColor": "00000000", "color": "ff0000", "width": 1.0}
countries_styled = countries.style(**style_params)
m4.add_ee_layer(countries_styled, {}, name="Country Boundaries")
m4.add_layer_control()
m4.to_streamlit(height=600)
