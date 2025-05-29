import datetime
import ee
import streamlit as st
from utils_ee import initialize_earth_engine
import geemap.foliumap as geemap

# Must be first Streamlit command
st.set_page_config(layout="wide")

# Initialize Earth Engine
initialize_earth_engine()

# Load Flood FeatureCollections
floods_HP = ee.FeatureCollection("projects/ee-desmond/assets/desirmed/floods_HP_2019")
floods_MP = ee.FeatureCollection("projects/ee-desmond/assets/desirmed/floods_MP_2019")
floods_LP = ee.FeatureCollection("projects/ee-desmond/assets/desirmed/floods_LP_2019")

# Load Ecosystem Services raster to extract CRS and scale
eco_img = ee.Image("projects/ee-desmond/assets/desirmed/Ecosystem_Services_2018_Raster_Asset")
eco_crs = eco_img.projection()
eco_scale = eco_img.projection().nominalScale()

# Function to rasterize floods
def rasterize_floods(fc, property_name='M_KL_DUB', scale=eco_scale, crs=eco_crs):
    return fc.reduceToImage(properties=[property_name], reducer=ee.Reducer.first()).reproject(crs=crs, scale=scale)

# Rasterized flood hazard layers
floods_hp_img = rasterize_floods(floods_HP)
floods_mp_img = rasterize_floods(floods_MP)
floods_lp_img = rasterize_floods(floods_LP)

# Flood visualization
flood_palette = ['blue', 'cyan', 'yellow', 'orange', 'red']
flood_vis = {"min": 1, "max": 5, "palette": flood_palette}

# Create tile layers for floods
hp_layer = geemap.ee_tile_layer(floods_hp_img, flood_vis, "Floods HP")
mp_layer = geemap.ee_tile_layer(floods_mp_img, flood_vis, "Floods MP")
lp_layer = geemap.ee_tile_layer(floods_lp_img, flood_vis, "Floods LP")

# Load other base datasets
esa = ee.ImageCollection("ESA/WorldCover/v100").first()
esa_vis = {"bands": ["Map"]}

esri = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m").mosaic()
esri_vis = {
    "min": 1,
    "max": 10,
    "palette": [
        "#1A5BAB", "#358221", "#A7D282", "#87D19E", "#FFDB5C",
        "#EECFA8", "#ED022A", "#EDE9E4", "#F2FAFF", "#C8C8C8",
    ],
}

# UI Sidebar Info
st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/deltares-desirmed) | [Twitter](https://twitter.com/deltares) | [YouTube](https://youtube.com/@deltares) | [LinkedIn](https://www.linkedin.com/in/deltares)
    """
)

# Main title
st.title("Climate Risk Impact Assessment")

# Layout
col1, col2 = st.columns([4, 1])
Map = geemap.Map()
Map.add_basemap("ESA WorldCover 2020 S2 FCC")
Map.add_basemap("ESA WorldCover 2020 S2 TCC")
Map.add_basemap("HYBRID")

# Sidebar controls
with col2:
    # Fixed center on Split-Dalmatia (e.g., Split, Croatia)
    Map.setCenter(16.4402, 43.0886, 11)

    # Dynamic World time range
    start = st.date_input("Start Date for Dynamic World", datetime.date(2020, 1, 1))
    end = st.date_input("End Date for Dynamic World", datetime.date(2021, 1, 1))
    start_date = start.strftime("%Y-%m-%d")
    end_date = end.strftime("%Y-%m-%d")

    region = ee.Geometry.BBox(-179, -89, 179, 89)
    dw = geemap.dynamic_world(region, start_date, end_date, return_type="hillshade")

    # Combine all selectable layers (land cover + floods)
    layers = {
        "Dynamic World": geemap.ee_tile_layer(dw, {}, "Dynamic World Land Cover"),
        "ESA Land Cover": geemap.ee_tile_layer(esa, esa_vis, "ESA Land Cover"),
        "ESRI Land Cover": geemap.ee_tile_layer(esri, esri_vis, "ESRI Land Cover"),
        "Floods HP": hp_layer,
        "Floods MP": mp_layer,
        "Floods LP": lp_layer,
    }

    options = list(layers.keys())
    left = st.selectbox("Select a left layer", options, index=1)
    right = st.selectbox("Select a right layer", options, index=0)

    Map.split_map(layers[left], layers[right])

    # Dynamic legend
    legend = st.selectbox("Select a legend", options, index=options.index(right))
    if legend == "Dynamic World":
        Map.add_legend(title="Dynamic World Land Cover", builtin_legend="Dynamic_World")
    elif legend == "ESA Land Cover":
        Map.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
    elif legend == "ESRI Land Cover":
        Map.add_legend(title="ESRI Land Cover", builtin_legend="ESRI_LandCover")

    with st.expander("Data sources"):
        st.markdown("""
        - [Dynamic World Land Cover](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1?hl=en)
        - [ESA Global Land Cover](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v100)
        - [ESRI Global Land Cover](https://samapriya.github.io/awesome-gee-community-datasets/projects/esrilc2020)
        """)


    # Layer toggle and split map interface
    layers = {
        "Dynamic World": geemap.ee_tile_layer(dw, {}, "Dynamic World Land Cover"),
        "ESA Land Cover": geemap.ee_tile_layer(esa, esa_vis, "ESA Land Cover"),
        "ESRI Land Cover": geemap.ee_tile_layer(esri, esri_vis, "ESRI Land Cover"),
        "Floods HP": hp_layer,
        "Floods MP": mp_layer,
        "Floods LP": lp_layer,
    }

    options = list(layers.keys())
    left = st.selectbox("Select a left layer", options, index=1)
    right = st.selectbox("Select a right layer", options, index=0)
    Map.split_map(layers[left], layers[right])

    # Dynamic legend for selected right layer
    legend = st.selectbox("Select a legend", options, index=options.index(right))
    if legend == "Dynamic World":
        Map.add_legend(title="Dynamic World Land Cover", builtin_legend="Dynamic_World")
    elif legend == "ESA Land Cover":
        Map.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
    elif legend == "ESRI Land Cover":
        Map.add_legend(title="ESRI Land Cover", builtin_legend="ESRI_LandCover")

    # Data Sources
    with st.expander("Data sources"):
        st.markdown("""
        - [Dynamic World Land Cover](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1?hl=en)
        - [ESA Global Land Cover](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v100)
        - [ESRI Global Land Cover](https://samapriya.github.io/awesome-gee-community-datasets/projects/esrilc2020)
        """)

# Show map in main panel
with col1:
    Map.add_layer_control()
    Map.to_streamlit(height=750)



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

st.sidebar.markdown(f"**Last Updated:** {last_updated}")

# st.sidebar.markdown(f"**Last Updated:** {last_updated} | {current_time}")
# st.sidebar.markdown(f"**Local Time (Amsterdam):** {current_time}")