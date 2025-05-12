import streamlit as st
import ee
import leafmap.foliumap as leafmap
import folium

# Initialize Earth Engine (already authenticated)
ee.Initialize()

st.set_page_config(layout="wide")

st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/deltares-desirmed)
    """
)

st.title("CORINE Land Cover 2018 Visualization via Google Earth Engine")

# ✅ Register custom method to add EE Tile Layers
def add_ee_tile_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee_image_object.getMapId(vis_params)
    folium.TileLayer(
        tiles=map_id_dict["tile_fetcher"].url_format,
        attr="Google Earth Engine",
        name=name,
        overlay=True,
        control=True
    ).add_to(self)

folium.Map.add_ee_tile_layer = add_ee_tile_layer

with st.expander("See source code"):
    with st.echo():
        # Create the Map centered on Europe
        m = leafmap.Map(center=[50, 10], zoom=5)

        # ✅ Correct: Load CORINE Land Cover 2018 as ee.Image, NOT ImageCollection
        corine = ee.Image("COPERNICUS/CORINE/V20/100m/2018")

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

        # ✅ Correct way: Add EE Tile Layer using the registered method
        m.add_ee_tile_layer(corine, vis_params, "CORINE Land Cover 2018")

        # Add Layer Control and Display Map
        m.add_layer_control()
        m.to_streamlit(height=700)

# Add a manual legend for CORINE classes
m.add_legend(
    title="CORINE Land Cover 2018",
    labels=[
        "Continuous urban fabric", "Discontinuous urban fabric", "Industrial/Commercial units",
        "Road and rail networks", "Port areas", "Airports", "Mineral extraction sites",
        "Dump sites", "Construction sites", "Green urban areas", "Sport/leisure facilities",
        "Non-irrigated arable land", "Permanently irrigated land", "Rice fields",
        "Vineyards", "Fruit trees and berry plantations", "Olive groves",
        "Pastures", "Annual crops associated with permanent crops", 
        "Complex cultivation patterns", "Land principally occupied by agriculture",
        "Agro-forestry areas", "Broad-leaved forest", "Coniferous forest",
        "Mixed forest", "Natural grassland", "Moors and heathland",
        "Sclerophyllous vegetation", "Transitional woodland-shrub",
        "Beaches, dunes, sands", "Bare rocks", "Sparsely vegetated areas",
        "Burnt areas", "Glaciers and perpetual snow", "Inland wetlands",
        "Peat bogs", "Salt marshes", "Salines", "Intertidal flats",
        "Water courses", "Water bodies", "Coastal lagoons", "Estuaries", "Sea and ocean"
    ],
    colors=[
        "#ff0000", "#e97419", "#a00000", "#ffff64", "#009900", "#006400",
        "#00ff00", "#00a000", "#dcdcdc", "#c8c8c8", "#ff0000", "#ffff64",
        "#ffff64", "#009900", "#009900", "#009900", "#009900", "#006400",
        "#00ff00", "#00ff00", "#00a000", "#00a000", "#dcdcdc", "#c8c8c8",
        "#ff0000", "#e97419", "#a00000", "#e5e5e5", "#70a3ba", "#0000ff",
        "#0000a0", "#707070", "#00ff00", "#00a000", "#00ffff", "#00a0a0",
        "#70a3ba", "#0000ff", "#0000a0", "#70a3ba", "#0000ff", "#0000a0",
        "#707070"
    ]
)


# with st.expander("See source code"):
#     with st.echo():
#         m = leafmap.Map()
#         m.split_map(
#             left_layer="ESA WorldCover 2020 S2 FCC", right_layer="ESA WorldCover 2020"
#         )
#         m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")


m.to_streamlit(height=700)