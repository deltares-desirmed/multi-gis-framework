import streamlit as st
import ee
import leafmap.foliumap as leafmap
import folium

# Initialize Earth Engine (assuming authenticated)
ee.Initialize()

st.set_page_config(layout="wide")

st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/deltares-desirmed)
    """
)

st.title("CORINE Land Cover 2018 Visualization via Google Earth Engine")

# ✅ Register add_ee_layer if not already registered
def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict["tile_fetcher"].url_format,
        attr="Google Earth Engine",
        name=name,
        overlay=True,
        control=True,
    ).add_to(self)

folium.Map.add_ee_layer = add_ee_layer

with st.expander("See source code"):
    with st.echo():
        # Centered on Europe
        m = leafmap.Map(center=[50, 10], zoom=5)

        # Load CORINE Data from GEE
        corine = ee.ImageCollection("COPERNICUS/CORINE/V20/100m/2018").first()

        # Visualization Parameters for CORINE
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

        # ✅ Add CORINE Layer using the custom EE method
        m.add_ee_layer(corine, vis_params, "CORINE Land Cover 2018")

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