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

flood_depth_classes = {
    1: "< 0.5 m",
    2: "0.5 – 1.5 m",
    3: "1.5 – 2.5 m",
    4: "> 2.5 m",
    5: "Extreme depth",
}
flood_palette = ['blue', 'cyan', 'yellow', 'orange', 'red']

# Flood visualization
flood_palette = ['blue', 'cyan', 'yellow', 'orange', 'red']
flood_vis = {"min": 1, "max": 5, "palette": flood_palette}

# Create tile layers for floods
hp_layer = geemap.ee_tile_layer(floods_hp_img, flood_vis, "Floods HP")
mp_layer = geemap.ee_tile_layer(floods_mp_img, flood_vis, "Floods MP")
lp_layer = geemap.ee_tile_layer(floods_lp_img, flood_vis, "Floods LP")


# Define Overture Maps PMTiles URLs
building_pmtiles = "https://overturemaps-tiles-us-west-2-beta.s3.amazonaws.com/2025-04-23/buildings.pmtiles"
road_pmtiles = "https://overturemaps-tiles-us-west-2-beta.s3.amazonaws.com/2025-04-23/transportation.pmtiles"

# Define styles
building_style = {
    "layers": [
        {
            "id": "Buildings",
            "source": "buildings",
            "source-layer": "building",
            "type": "line",
            "paint": {
                "line-color": "#ff0000",
                "line-width": 1,
            },
        },
    ]
}

road_style = {
    "layers": [
        {
            "id": "Roads",
            "source": "transportation",
            "source-layer": "segment",
            "type": "line",
            "paint": {
                "line-color": "#ffffff",
                "line-width": 2,
            },
        },
    ]
}



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

# Load the FeatureCollection once
population_fc = ee.FeatureCollection("projects/ee-desmond/assets/desirmed/settlements_population_with_gender_age")

# Define years to visualize
pop_years = ["2011", "2021", "2025", "2030"]

# Define visualization settings
pop_vis = {
    "min": 0,
    "max": 200,
    "palette": ["#ffffcc", "#a1dab4", "#41b6c4", "#2c7fb8", "#253494"]
}

pop_tile_layers = {
    f"Population {year}": geemap.ee_tile_layer(
        population_fc.reduceToImage([f"pop_{year}"], ee.Reducer.first()).reproject(crs=eco_crs, scale=eco_scale),
        pop_vis,
        f"Population {year}"
    )
    for year in pop_years
}

# Define visualization parameters
pop_vis = {
    "min": 0,
    "max": 2000,
    "palette": ["#ffffcc", "#a1dab4", "#41b6c4", "#2c7fb8", "#253494"]
}

# Add to map


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

Map.add_pmtiles(
    url=building_pmtiles,
    style=building_style,
    tooltip=True,
    fit_bounds=False
)

Map.add_pmtiles(
    url=road_pmtiles,
    style=road_style,
    tooltip=True,
    fit_bounds=False
)

# CORINE Land Cover
CORINE_YEARS = {
    '2012': ee.Image('COPERNICUS/CORINE/V20/100m/2012').select('landcover'),
    '2018': ee.Image('COPERNICUS/CORINE/V20/100m/2018').select('landcover'),
}

# CORINE class name mapping and palette
# Full CORINE class palette (44 values)
corine_classes = {
    111: 'Continuous Urban Fabric',
    112: 'Discontinuous Urban Fabric',
    121: 'Industrial/Commercial Units',
    122: 'Road/rail networks',
    123: 'Port areas',
    124: 'Airports',
    131: 'Mineral extraction sites',
    132: 'Dump sites',
    133: 'Construction sites',
    141: 'Green urban areas',
    142: 'Sport/leisure facilities',
    211: 'Non-irrigated arable land',
    212: 'Permanently irrigated land',
    213: 'Rice fields',
    221: 'Vineyards',
    222: 'Fruit trees',
    223: 'Olive groves',
    231: 'Pastures',
    241: 'Annual crops associated with permanent crops',
    242: 'Complex cultivation patterns',
    243: 'Agro-forestry',
    244: 'Agro-natural mosaic',
    311: 'Broad-leaved forest',
    312: 'Coniferous forest',
    313: 'Mixed forest',
    321: 'Natural grasslands',
    322: 'Moors/heathland',
    323: 'Sclerophyllous vegetation',
    324: 'Transitional woodland-shrub',
    331: 'Beaches/dunes/sands',
    332: 'Bare rocks',
    333: 'Sparsely vegetated areas',
    334: 'Burnt areas',
    335: 'Glaciers and perpetual snow',
    411: 'Inland marshes',
    412: 'Peat bogs',
    421: 'Salt marshes',
    422: 'Salines',
    423: 'Intertidal flats',
    511: 'Water courses',
    512: 'Water bodies',
    521: 'Coastal lagoons',
    522: 'Estuaries',
    523: 'Sea and ocean'
}


corine_palette = [
    "#ff0000", "#e97419", "#a00000", "#ffff64", "#009900", "#006400",
    "#00ff00", "#00a000", "#dcdcdc", "#c8c8c8", "#ff0000", "#ffffa8",
    "#ffff00", "#e6e600", "#e68000", "#f2a64d", "#e6a600", "#e6e64d",
    "#ffe6a6", "#ffe64d", "#e6cc4d", "#f2cca6", "#80ff00", "#00a600",
    "#4dff00", "#ccf24d", "#a6ff80", "#a6e64d", "#a6f200", "#e6e6e6",
    "#cccccc", "#ccffcc", "#000000", "#a6e6cc", "#a6a6ff", "#4d4dff",
    "#ccccff", "#e6e6ff", "#a6a6e6", "#00ccf2", "#80f2e6", "#00ffa6",
    "#a6ffe6", "#e6f2ff"]


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


    # Set region for Dynamic World globally (you can later restrict this if needed)
    region = ee.Geometry.BBox(-179, -89, 179, 89)
    dw = geemap.dynamic_world(region, start_date, end_date, return_type="hillshade")


    # Layer toggle and split map interface
    # Add CORINE 2012 and 2018 directly to selectable layers
    corine_2012 = geemap.ee_tile_layer(
        CORINE_YEARS["2012"], {"min": 111, "max": 523, "palette": corine_palette}, "CORINE 2012"
    )
    corine_2018 = geemap.ee_tile_layer(
        CORINE_YEARS["2018"], {"min": 111, "max": 523, "palette": corine_palette}, "CORINE 2018"
    )

    layers = {
    "Dynamic World": geemap.ee_tile_layer(dw, {}, "Dynamic World Land Cover"),
    "ESA Land Cover": geemap.ee_tile_layer(esa, esa_vis, "ESA Land Cover"),
    "ESRI Land Cover": geemap.ee_tile_layer(esri, esri_vis, "ESRI Land Cover"),
    "Floods HP": hp_layer,
    "Floods MP": mp_layer,
    "Floods LP": lp_layer,
    "CORINE 2012": corine_2012,
    "CORINE 2018": corine_2018,
    **pop_tile_layers,  # Unpacks population layers
    "Buildings (Overture)": "PMTILES_BUILDINGS",  # placeholder
    "Roads (Overture)": "PMTILES_ROADS",          # placeholder
}




    
    options = list(layers.keys())
    left = st.selectbox("Select a left layer", options, index=1)
    right = st.selectbox("Select a right layer", options, index=0)

    # Handle PMTiles layers for split map
    def get_layer(layer_key):
        if layer_key in layers:
            layer_obj = layers[layer_key]
            if layer_obj == "PMTILES_BUILDINGS":
                return geemap.EmptyTileLayer(name="Buildings (Overture)")
            elif layer_obj == "PMTILES_ROADS":
                return geemap.EmptyTileLayer(name="Roads (Overture)")
            else:
                return layer_obj
        return None

    # Use custom logic to assign layers for split map
    left_layer = get_layer(left)
    right_layer = get_layer(right)


    Map.split_map(left_layer, right_layer)


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
    elif legend.startswith("Floods"):
        legend_dict = {
            f"{k} - {v}": flood_palette[i]
            for i, (k, v) in enumerate(flood_depth_classes.items())
        }
        Map.add_legend(title=f"{legend} Depth Categories", legend_dict=legend_dict)
    elif legend.startswith("Population"):
        pop_legend_dict = {
            "0–400": "#ffffcc",
            "400–800": "#a1dab4",
            "800–1200": "#41b6c4",
            "1200–1600": "#2c7fb8",
            ">1600": "#253494"
        }
        Map.add_legend(title=f"{legend}", legend_dict=pop_legend_dict)

    elif legend.startswith("Buildings"):
        Map.add_legend(
            title="Building Confidence",
            legend_dict={
                "50–60%": "lightgrey",
                "60–80%": "blue",
                "80–100%": "darkblue"
            }
        )

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