import os
import streamlit as st
import leafmap.foliumap as leafmap
import ee

# Set API Key for MapTiler 3D Terrain
os.environ["MAPTILER_KEY"] = "iiyRi7eIx4NmHrMOEZsc"

st.set_page_config(layout="wide")

st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | 
    [GitHub](https://github.com/deltares-desirmed) | 
    [YouTube](https://youtube.com/@deltares) | 
    [LinkedIn](https://www.linkedin.com/in/deltares)
    """
)

st.title("Multi-GIS Viewer: Split Map and 3D Visualization")

# === Split-panel Map ===
st.header("🔀 Split-panel Map")
with st.expander("See Split Map Source Code"):
    with st.echo():
        m = leafmap.Map()
        m.split_map(
            left_layer="ESA WorldCover 2020 S2 FCC", 
            right_layer="ESA WorldCover 2020"
        )
        m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
m.to_streamlit(height=600)

# === 3D Visualization Section ===
st.header("🌍 Data Visualization in 3D")

# 3D Globe - Basic Projection
st.subheader("1️⃣ Globe Projection with Basic Control")
m1 = leafmap.Map(center=[-100, 40], zoom=3, style="liberty")
m1.add_globe_control()
m1.to_streamlit(height=500)

# 3D Globe - Overture 3D Buildings
st.subheader("2️⃣ Overture 3D Buildings")
m2 = leafmap.Map(center=[-100, 40], zoom=3, style="positron", projection="globe")
m2.add_overture_3d_buildings()
m2.to_streamlit(height=500)

# 3D Globe - Basemaps + 3D Buildings
st.subheader("3️⃣ Add Basemaps with 3D Buildings")
m3 = leafmap.Map(center=[-100, 40], zoom=3, style="positron", projection="globe")
m3.add_basemap("Esri.WorldImagery")
m3.add_overture_3d_buildings()
m3.add_layer_control()
m3.to_streamlit(height=500)

# 3D Globe - Visualizing ESA Land Cover with 3D Terrain
st.subheader("4️⃣ Visualize ESA Land Cover in 3D Terrain")
m4 = leafmap.Map(style="3d-terrain", projection="globe")
m4.add_ee_layer(asset_id="ESA/WorldCover/v200", opacity=0.5)
m4.add_legend(builtin_legend="ESA_WorldCover", title="ESA Landcover")
m4.add_overture_3d_buildings()
m4.add_layer_control()
m4.to_streamlit(height=500)

# 3D Globe - ESA Land Cover with Visualization Parameters
st.subheader("5️⃣ ESA Land Cover Data Visualization")
dataset = ee.ImageCollection("ESA/WorldCover/v200").first()
vis_params = {"bands": ["Map"]}
m5 = leafmap.Map(style="3d-terrain", projection="globe")
m5.add_ee_layer(dataset, vis_params, name="ESA Worldcover", opacity=0.5)
m5.add_legend(builtin_legend="ESA_WorldCover", title="ESA Landcover")
m5.add_layer_control()
m5.to_streamlit(height=500)

# 3D Globe - Nighttime Light Data
st.subheader("6️⃣ Nighttime Light Data Visualization")
dataset = ee.ImageCollection("NOAA/VIIRS/DNB/ANNUAL_V22").filter(
    ee.Filter.date("2022-01-01", "2023-01-01")
)
nighttime = dataset.select("maximum")
nighttime_vis = {"min": 0.0, "max": 60.0}
m6 = leafmap.Map(style="darkmatter", projection="globe")
m6.add_ee_layer(nighttime, nighttime_vis, name="Nighttime Lights")

countries = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017")
style_params = {"fillColor": "00000000", "color": "ff0000", "width": 1.0}
countries = countries.style(**style_params)
m6.add_ee_layer(countries, {}, name="Country Boundaries")
m6.add_layer_control()
m6.to_streamlit(height=500)

# Footer - Last Updated Info
import datetime
current_date = datetime.datetime.now().strftime("%B %d, %Y")
st.sidebar.markdown(f"**Last Updated:** {current_date}")
