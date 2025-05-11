import streamlit as st
import leafmap.foliumap as leafmap
import leafmap.maplibregl as maplibre
import ee
import os

# Set MapTiler API Key
os.environ["MAPTILER_KEY"] = "iiyRi7eIx4NmHrMOEZsc"

# Initialize Earth Engine
ee.Initialize()

st.set_page_config(layout="wide")

st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/deltares-desirmed) | [Twitter](https://twitter.com/deltares) | [YouTube](https://youtube.com/@deltares) | [LinkedIn](https://www.linkedin.com/in/deltares)
    """
)

st.title("Split-panel Map with 3D Visualization (EE Data)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Split Panel Map")
    m = leafmap.Map()
    m.split_map(
        left_layer="ESA WorldCover 2020 S2 FCC", right_layer="ESA WorldCover 2020"
    )
    m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
    m.to_streamlit(height=600)

with col2:
    st.subheader("3D Globe Visualization with ESA WorldCover")

    # Get EE Tile URL for WorldCover
    dataset = ee.ImageCollection("ESA/WorldCover/v200").first()
    vis_params = {"bands": ["Map"], "min": 10, "max": 100, "palette": [
        "006400", "ffbb22", "ffff4c", "f096ff", "fa0000", 
        "b4b4b4", "f0f0f0", "0064c8", "0096a0", "00cf75", "fae6a0"
    ]}

    map_id_dict = ee.Image(dataset).getMapId(vis_params)
    tile_url = map_id_dict["tile_fetcher"].url_format

    # Create 3D Globe Map
    m3d = maplibre.Map(style="3d-terrain", projection="globe")
    m3d.add_basemap("Esri.WorldImagery")
    m3d.add_tile_layer(
        url=tile_url,
        name="ESA WorldCover 2020",
        attribution="ESA WorldCover via GEE",
        opacity=0.7
    )
    m3d.add_overture_3d_buildings()
    m3d.add_layer_control()
    m3d.to_streamlit(height=600)
-