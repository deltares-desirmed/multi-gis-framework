import streamlit as st
import ee
import leafmap.foliumap as leafmap

# Initialize Earth Engine (assuming you’ve already authenticated)
ee.Initialize()

st.set_page_config(layout="wide")

st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/deltares-desirmed)
    """
)

st.title("CORINE Land Cover 2018 Visualization via Google Earth Engine")

with st.expander("See source code"):
    with st.echo():
        # Create Map Centered on Europe
        m = leafmap.Map(center=[50, 10], zoom=5)

        # Load CORINE Land Cover 2018 from GEE
        corine = ee.ImageCollection("COPERNICUS/CORINE/V20/100m/2018").first()

        # Visualization Parameters
        vis_params = {
            "bands": ["landcover"],
            "min": 1,
            "max": 44,
            "palette": [
                "#ffff64", "#ffff64", "#ffff64", "#ffff64", "#009900", "#009900", "#009900",
                "#009900", "#006400", "#006400", "#006400", "#00ff00", "#00ff00", "#00ff00",
                "#00ff00", "#00a000", "#00a000", "#00a000", "#dcdcdc", "#c8c8c8", "#ff0000",
                "#ff0000", "#ff0000", "#e97419", "#e97419", "#e97419", "#a00000", "#a00000",
                "#a00000", "#e5e5e5", "#e5e5e5", "#e5e5e5", "#70a3ba", "#70a3ba", "#70a3ba",
                "#0000ff", "#0000ff", "#0000ff", "#0000a0", "#0000a0", "#0000a0", "#707070"
            ]
        }

        # Add the CORINE Layer to the Map
        m.add_ee_layer(corine, vis_params, "CORINE Land Cover 2018")

        # Add Layer Control and Legend (you can customize this legend if you want)
        m.add_layer_control()
        m.to_streamlit(height=700)


# with st.expander("See source code"):
#     with st.echo():
#         m = leafmap.Map()
#         m.split_map(
#             left_layer="ESA WorldCover 2020 S2 FCC", right_layer="ESA WorldCover 2020"
#         )
#         m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")


m.to_streamlit(height=700)