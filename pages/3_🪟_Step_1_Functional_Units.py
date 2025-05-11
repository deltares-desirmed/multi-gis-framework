import os
import streamlit as st
import leafmap.foliumap as leafmap
import ee

# Set API Key for MapTiler 3D Terrain
os.environ["MAPTILER_KEY"] = "iiyRi7eIx4NmHrMOEZsc"

# st.set_page_config(layout="wide")

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
import os
import ee
import leafmap.kepler as leafmap  # Use Kepler for 3D visualizations

# Initialize Earth Engine
if not ee.data._initialized:
    ee.Initialize()

# Set the MapTiler API key for 3D terrain visualization
os.environ["MAPTILER_KEY"] = "iiyRi7eIx4NmHrMOEZsc"

st.set_page_config(layout="wide")

st.sidebar.title("Navigation")
mode = st.sidebar.radio("Select Visualization Mode", ["2D Split Map", "3D Visualization"])

st.sidebar.title("Contact")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/deltares-desirmed) | 
    [LinkedIn](https://www.linkedin.com/in/deltares)
    """
)

if mode == "2D Split Map":
    st.title("2D Split-panel Map")
    with st.expander("See source code"):
        with st.echo():
            m = leafmap.Map()
            m.split_map(
                left_layer="ESA WorldCover 2020 S2 FCC",
                right_layer="ESA WorldCover 2020"
            )
            m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
    m.to_streamlit(height=700)

elif mode == "3D Visualization":
    st.title("3D Data Visualization with Globe Projection")

    m = leafmap.Map(style="3d-terrain", center=[0, 0], zoom=1)

    dataset = ee.ImageCollection("ESA/WorldCover/v200").first()
    vis_params = {"bands": ["Map"], "min": 0, "max": 100, "opacity": 0.5}

    # Proper way to add EE Image in Kepler
    m.add_ee_layer(dataset, vis_params, "ESA WorldCover")

    # Add Overture 3D buildings
    m.add_overture_3d_buildings()

    if st.checkbox("Show Nighttime Lights"):
        night_dataset = ee.ImageCollection("NOAA/VIIRS/DNB/ANNUAL_V22") \
            .filterDate("2022-01-01", "2023-01-01").select("maximum")
        night_vis = {"min": 0.0, "max": 60.0, "opacity": 0.5}
        m.add_ee_layer(night_dataset.mean(), night_vis, "Nighttime Lights")

    # Country Boundaries Layer
    countries = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017").style(
        fillColor="00000000", color="ff0000", width=1.0
    )
    m.add_ee_layer(countries, {}, "Country Boundaries")

    m.to_streamlit(height=700)
