import os
import streamlit as st
import leafmap.foliumap as leafmap
import ee

# Set API Key for MapTiler 3D Terrain
os.environ["MAPTILER_KEY"] = "iiyRi7eIx4NmHrMOEZsc"

st.set_page_config(layout="wide")

# st.sidebar.title("Info")
# st.sidebar.info(
#     """
#     Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | 
#     [GitHub](https://github.com/deltares-desirmed) | 
#     [YouTube](https://youtube.com/@deltares) | 
#     [LinkedIn](https://www.linkedin.com/in/deltares)
#     """
# )

# st.title("Multi-GIS Viewer: Split Map and 3D Visualization")

# # === Split-panel Map ===
# st.header("🔀 Split-panel Map")
# with st.expander("See Split Map Source Code"):
#     with st.echo():
#         m = leafmap.Map()
#         m.split_map(
#             left_layer="ESA WorldCover 2020 S2 FCC", 
#             right_layer="ESA WorldCover 2020"
#         )
#         m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
# m.to_streamlit(height=600)

import streamlit as st
import pydeck as pdk
import ee
import os

# Streamlit Page Config
# st.set_page_config(layout="wide")

# Load your MapTiler API key
os.environ["MAPTILER_KEY"] = "iiyRi7eIx4NmHrMOEZsc"

# Initialize Earth Engine
if not ee.data._initialized:
    try:
        ee.Initialize()
    except Exception as e:
        st.error(f"Earth Engine initialization failed: {e}")

st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/deltares-desirmed) | [Twitter](https://twitter.com/deltares) | [YouTube](https://youtube.com/@deltares) | [LinkedIn](https://www.linkedin.com/in/deltares)
    """
)

st.title("Split-panel Map and 3D Visualization")

# Split Map Section
with st.expander("See Split Map Source Code"):
    with st.echo():
        import leafmap.foliumap as leafmap
        m = leafmap.Map()
        m.split_map(
            left_layer="ESA WorldCover 2020 S2 FCC", right_layer="ESA WorldCover 2020"
        )
        m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
    m.to_streamlit(height=600)

st.subheader("3D Data Visualization with Earth Engine Data")

# Load ESA WorldCover Data
dataset = ee.ImageCollection("ESA/WorldCover/v200").first()
vis_params = {"bands": ["Map"]}

# Get Map ID and Token for Visualization
map_id_dict = ee.data.getMapId({
    'image': dataset.visualize(**vis_params)
})

tile_url = map_id_dict['tile_fetcher'].url_format

# Create Pydeck 3D Globe View
view_state = pdk.ViewState(
    latitude=0,
    longitude=0,
    zoom=0.5,
    pitch=30,
)

raster_layer = pdk.Layer(
    "TileLayer",
    data=tile_url,
    minZoom=0,
    maxZoom=6,
    tileSize=256,
    opacity=0.7,
)

deck = pdk.Deck(
    layers=[raster_layer],
    initial_view_state=view_state,
    map_provider='maptiler',
    map_style=f"https://api.maptiler.com/maps/3d-terrain/style.json?key={os.getenv('MAPTILER_KEY')}"
)

st.pydeck_chart(deck)
