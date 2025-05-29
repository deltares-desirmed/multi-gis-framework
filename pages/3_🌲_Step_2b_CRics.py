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

# CORINE Land Cover
CORINE_YEARS = {
    '2012': ee.Image('COPERNICUS/CORINE/V20/100m/2012').select('landcover'),
    '2018': ee.Image('COPERNICUS/CORINE/V20/100m/2018').select('landcover'),
}

# CORINE class name mapping and palette
corine_classes = {
    111: 'Continuous Urban Fabric', 112: 'Discontinuous Urban Fabric',
    121: 'Industrial/Commercial Units', 122: 'Road/rail networks', 123: 'Port areas',
    124: 'Airports', 131: 'Mineral extraction sites', 132: 'Dump sites', 133: 'Construction sites',
    141: 'Green urban areas', 142: 'Sport/leisure facilities', 211: 'Non-irrigated arable land',
    212: 'Permanently irrigated land', 213: 'Rice fields', 221: 'Vineyards', 222: 'Fruit trees',
    223: 'Olive groves', 231: 'Pastures', 241: 'Annual crops with permanent crops',
    242: 'Complex cultivation patterns', 243: 'Agro-forestry', 244: 'Agro-natural mosaic',
    311: 'Broad-leaved forest', 312: 'Coniferous forest', 313: 'Mixed forest',
    321: 'Natural grasslands', 322: 'Moors/heathland', 323: 'Sclerophyllous vegetation',
    324: 'Transitional woodland-shrub', 331: 'Beaches/dunes/sands', 332: 'Bare rocks',
    333: 'Sparsely vegetated areas', 334: 'Burnt areas', 335: 'Glaciers and snow',
    411: 'Inland marshes', 412: 'Peat bogs', 421: 'Salt marshes', 422: 'Salines',
    423: 'Intertidal flats', 511: 'Water courses', 512: 'Water bodies',
    521: 'Coastal lagoons', 522: 'Estuaries', 523: 'Sea and ocean',
}
corine_palette = [
    "#ff0000", "#e6004d", "#cc4d00", "#cc0000", "#e6b3b3", "#a64d79",
    "#ffe6cc", "#999966", "#cc99ff", "#33cc33", "#66ff66", "#ffff99",
    "#ffcc99", "#ffffcc", "#ffcc66", "#f2f2f2", "#e6e600", "#c2f0c2",
    "#b3ffcc", "#d9f2e6", "#e6ffe6", "#003300", "#006600", "#339966",
    "#999933", "#cccc00", "#99cc00", "#669900", "#f2f2f2", "#cccccc",
    "#999999", "#ffcccc", "#ccffff", "#cce6ff", "#e6e6e6", "#99ccff",
    "#ccffff", "#9999ff", "#66cccc", "#6699ff", "#3333ff", "#0000cc",
    "#6666ff", "#000099"
]


# Sidebar controls
with col2:
    # Fixed location center and zoom (Split, Croatia)
    longitude = 16.4402
    latitude = 43.5081
    zoom = 11
    Map.setCenter(longitude, latitude, zoom)

    # Dynamic World time range
    start = st.date_input("Start Date for Dynamic World", datetime.date(2020, 1, 1))
    end = st.date_input("End Date for Dynamic World", datetime.date(2021, 1, 1))
    start_date = start.strftime("%Y-%m-%d")
    end_date = end.strftime("%Y-%m-%d")

        # CORINE year selection
    corine_year = st.selectbox("Select CORINE Year", list(CORINE_YEARS.keys()), index=1)
    corine_img = CORINE_YEARS[corine_year]
    corine_layer = geemap.ee_tile_layer(
        corine_img, {"min": 111, "max": 523, "palette": corine_palette}, f"CORINE {corine_year}"
    )


    # Set region for Dynamic World globally (you can later restrict this if needed)
    region = ee.Geometry.BBox(-179, -89, 179, 89)
    dw = geemap.dynamic_world(region, start_date, end_date, return_type="hillshade")


    # Layer toggle and split map interface
    layers = {
        "Dynamic World": geemap.ee_tile_layer(dw, {}, "Dynamic World Land Cover"),
        "ESA Land Cover": geemap.ee_tile_layer(esa, esa_vis, "ESA Land Cover"),
        "ESRI Land Cover": geemap.ee_tile_layer(esri, esri_vis, "ESRI Land Cover"),
        "Floods HP": hp_layer,
        "Floods MP": mp_layer,
        "Floods LP": lp_layer,
        f"CORINE {corine_year}": corine_layer,

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
    elif legend.startswith("CORINE"):
        legend_dict = {f"{k} - {v}": corine_palette[i] for i, (k, v) in enumerate(corine_classes.items())}
        Map.add_legend(title=f"CORINE Land Cover {corine_year}", legend_dict=legend_dict)


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