import streamlit as st
import ee
import folium
import geemap.foliumap as geemap 
from utils_ee import initialize_earth_engine  #  Auth from secret config
import zipfile
import os
import geopandas as gpd

# Initialize EE
initialize_earth_engine()

# Load FeatureCollections
admin0 = ee.FeatureCollection("projects/sat-io/open-datasets/geoboundaries/CGAZ_ADM0")
admin1 = ee.FeatureCollection("projects/sat-io/open-datasets/geoboundaries/CGAZ_ADM1")
admin2 = ee.FeatureCollection("projects/sat-io/open-datasets/geoboundaries/CGAZ_ADM2")

# UI setup
st.title("Know your landscapes")

# Step 1: AOI selection via dropdowns
countries = admin0.aggregate_array('shapeName').getInfo()
selected_country = st.selectbox("Select NUTS1", sorted(countries))
country_geom = admin0.filter(ee.Filter.eq('shapeName', selected_country)).geometry()

regions = admin1.filterBounds(country_geom).aggregate_array('shapeName').getInfo()
selected_region = st.selectbox("Select NUTS2", sorted(regions))
region_geom = admin1.filter(ee.Filter.eq('shapeName', selected_region)).geometry()

subregions = admin2.filterBounds(region_geom).aggregate_array('shapeName').getInfo()
selected_subregion = st.selectbox("Select NUTS3", sorted(subregions))
aoi = admin2.filter(ee.Filter.eq('shapeName', selected_subregion))

# Step 1: Upload user shapefile (if any)
uploaded = st.file_uploader("Optional: Upload your own AOI shapefile (.zip)", type=["zip"])
uploaded_aoi_fc = None  # Earth Engine FeatureCollection
uploaded_geom = None    # Earth Engine Geometry

if uploaded:
    with zipfile.ZipFile(uploaded, 'r') as zf:
        zf.extractall("temp_shp")

    shp_files = [f for f in os.listdir("temp_shp") if f.endswith(".shp")]
    if not shp_files:
        st.error(" No .shp file found in the uploaded .zip.")
    else:
        shp_path = os.path.join("temp_shp", shp_files[0])

        try:
            gdf = gpd.read_file(shp_path)
            if gdf.empty:
                st.error(" Shapefile is empty.")
            elif not gdf.geom_type.isin(["Polygon", "MultiPolygon"]).any():
                st.error(" Shapefile must contain polygon geometries.")
            else:
                uploaded_aoi_fc = geemap.gdf_to_ee(gdf)
                uploaded_geom = uploaded_aoi_fc.geometry()
                st.success(" AOI uploaded and converted successfully.")
        except Exception as e:
            st.error(f" Error reading shapefile: {e}")

# AOI used: uploaded shapefile or dropdown
# AOI used: uploaded shapefile or dropdown
final_aoi_fc = uploaded_aoi_fc if uploaded_aoi_fc else aoi            # For styling/layer display
final_aoi = uploaded_geom if uploaded_geom else aoi.geometry()         # For geometry-based operations
selected_subregion = "User_AOI" if uploaded_aoi_fc else selected_subregion



# Select CORINE year
CORINE_YEARS = {
    '2012': ee.Image('COPERNICUS/CORINE/V20/100m/2012').select('landcover'),
    '2018': ee.Image('COPERNICUS/CORINE/V20/100m/2018').select('landcover')
}

# Crosswalk mapping from CORINE classes to EUNIS numeric codes
corine_to_eunis = {
    111: 1, 112: 2, 121: 3, 122: 4, 123: 5, 124: 6, 131: 7, 132: 8, 133: 9,
    141: 10, 142: 1, 211: 11, 212: 12, 213: 13, 221: 14, 222: 15, 223: 16,
    231: 17, 241: 18, 242: 19, 243: 20, 244: 21, 311: 22, 312: 23, 313: 24,
    321: 25, 322: 26, 323: 27, 324: 28, 331: 29, 332: 30, 333: 31, 334: 32,
    335: 33, 411: 34, 412: 35, 421: 36, 422: 37, 423: 38, 511: 39, 512: 40,
    521: 41, 522: 42, 523: 43
}

# EUNIS color palette (43 classes)
eunis_palette = [
    '#b22222', '#ff4500', '#ffa07a', '#8b4513', '#d2691e', '#808080', '#556b2f',
    '#a0522d', '#d2b48c', '#deb887', '#32cd32', '#adff2f', '#ff7f50', '#8fbc8f',
    '#228b22', '#f4a460', '#006400', '#ffe4b5', '#6b8e23', '#f0e68c', '#d2b48c',
    '#008000', '#3cb371', '#20b2aa', '#7cfc00', '#8b0000', '#b0c4de', '#87cefa',
    '#fa8072', '#add8e6', '#708090', '#d3d3d3', '#556b2f', '#4169e1', '#00bfff',
    '#1e90ff', '#6495ed', '#ffdab9', '#87ceeb', '#2171b5', '#ffdab9', '#2171b5',
    '#87cefa'
]

# Clip both CORINE layers immediately to final AOI
CLIPPED_CORINE = {
    '2012': CORINE_YEARS['2012'].clip(final_aoi),
    '2018': CORINE_YEARS['2018'].clip(final_aoi)
}


# Year selection + retrieval of clipped image --> we can choose this or the other....full corine or only clipped to AOI
# selected_year = st.selectbox("Select CORINE Year", ['2012', '2018'])
# corine_img = CLIPPED_CORINE[selected_year]
# Year selection
selected_year = st.selectbox("Select CORINE Year", ['2012', '2018'])

# Optional clip toggle
clip_toggle = st.checkbox("Clip CORINE to AOI", value=True)

# CORINE image (clipped or full)
corine_img = (
    CORINE_YEARS[selected_year].clip(final_aoi)
    if clip_toggle else CORINE_YEARS[selected_year]
)


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
    "#ff0000", "#e6004d", "#cc4d00", "#cc0000", "#e6b3b3", "#a64d79",
    "#ffe6cc", "#999966", "#cc99ff", "#33cc33", "#66ff66", "#ffff99",
    "#ffcc99", "#ffffcc", "#ffcc66", "#f2f2f2", "#e6e600", "#c2f0c2",
    "#b3ffcc", "#d9f2e6", "#e6ffe6", "#003300", "#006600", "#339966",
    "#999933", "#cccc00", "#99cc00", "#669900", "#f2f2f2", "#cccccc",
    "#999999", "#ffcccc", "#ccffff", "#cce6ff", "#e6e6e6", "#99ccff",
    "#ccffff", "#9999ff", "#66cccc", "#6699ff", "#3333ff", "#0000cc",
    "#6666ff", "#000099"
]


# Reclassification logics
landscape_archetypes = {
    '1': {'classes': [111,112,121,122], 'color': '#636363', 'description': 'Urban'},
    '2': {'classes': [123,124], 'color': '#969696', 'description': 'Coastal Urban'},
    '3': {'classes': [131,132,133], 'color': '#cccccc', 'description': 'Industrial'},
    '4': {'classes': [141,142], 'color': '#91d700', 'description': 'Recreational'},
    '5': {'classes': [211,212,213], 'color': '#91d700', 'description': 'Rural (Flat)'},
    '6': {'classes': [221,222,223,231], 'color': '#df9f00', 'description': 'Rural (Hilly)'},
    '7': {'classes': [311,312,313,321,322,323,324], 'color': '#80ff00', 'description': 'Forested'},
    '8': {'classes': [332,333,334,335], 'color': '#a63603', 'description': 'Mountainous'},
    '9': {'classes': [241,242,243,244], 'color': '#78c679', 'description': 'Rural'},
    '10': {'classes': [331], 'color': '#ffcc99', 'description': 'Coastal (Beach)'},
    '11': {'classes': [421,422,423], 'color': '#7fff00', 'description': 'Coastal Rural'},
    '12': {'classes': [411,412], 'color': '#a6e6ff', 'description': 'Wetlands'},
    '13': {'classes': [511,512], 'color': '#4da6ff', 'description': 'Inland Water'},
    '14': {'classes': [521,522,523], 'color': '#00bfff', 'description': 'Marine'}
}


from_list, to_list, palette = [], [], []
legend_dict = {}

for k, v in landscape_archetypes.items():
    from_list.extend(v['classes'])
    to_list.extend([int(k)] * len(v['classes']))
    palette.append(v['color'])
    legend_dict[v['description']] = v['color']

def reclassify_to_eunis(image):
    from_list = list(corine_to_eunis.keys())
    to_list = list(corine_to_eunis.values())
    return image.remap(from_list, to_list).rename("eunis")

CLIPPED_EUNIS = {
    '2012': reclassify_to_eunis(CORINE_YEARS['2012']).clip(final_aoi),
    '2018': reclassify_to_eunis(CORINE_YEARS['2018']).clip(final_aoi)
}

def reclassify(img):
    remapped = img.remap(from_list, to_list).rename('archetype')
    return remapped.updateMask(remapped.neq(0))

corine_img = CLIPPED_CORINE[selected_year]

archetype_img = reclassify(corine_img).clip(final_aoi)

# Map Display
st.subheader(f"Check out and inspect Biophysical archetypes ({selected_year})")
# Map = geemap.Map(center=[51, 3], zoom=8)

# Map.addLayer(final_aoi.style(**{
#     "color": "red", "fillColor": "00000000", "width": 2
# }), {}, "AOI Boundary")

# Map.addLayer(archetype_img, {"min": 1, "max": 14, "palette": palette}, f"Archetypes {selected_year}")
# Create the map
# Compute center coordinates dynamically
# Handle both ee.Geometry and ee.FeatureCollection for centroid
aoi_geom_for_centroid = final_aoi if isinstance(final_aoi, ee.Geometry) else final_aoi.geometry()
aoi_centroid = aoi_geom_for_centroid.centroid().coordinates().getInfo()

# populations
ghs_years = [2015, 2020, 2025, 2030]

# Center map and add layers
Map = geemap.Map(center=[aoi_centroid[1], aoi_centroid[0]], zoom=10)

# Style and add AOI boundary
if isinstance(final_aoi_fc, ee.FeatureCollection):
    Map.addLayer(final_aoi_fc.style(**{
        "color": "red", "fillColor": "00000000", "width": 2
    }), {}, "AOI Boundary")
else:
    styled_geom = ee.FeatureCollection([ee.Feature(final_aoi)]).style(**{
        "color": "red", "fillColor": "00000000", "width": 2
    })
    Map.addLayer(styled_geom, {}, "AOI Boundary")

# Add archetype image
Map.addLayer(archetype_img, {"min": 1, "max": 14, "palette": palette}, f"Archetypes {selected_year}")

Map.addLayer(
    corine_img,
    {
        "min": 111,
        "max": 523,
        "palette": corine_palette
    },
    f"CORINE {selected_year}"
)

Map.addLayer(
    CLIPPED_EUNIS[selected_year],
    {"min": 1, "max": 43, "palette": eunis_palette},
    f"EUNIS {selected_year}"
)

for year in ghs_years:
    try:
        ghs_pop = ee.Image(f"projects/sat-io/open-datasets/GHS/GHS_POP/GHS_POP_E{year}_GLOBE_R2023A_54009_100_V1_0").clip(final_aoi)
        ghs_smod = ee.Image(f"projects/sat-io/open-datasets/GHS/GHS_SMOD/GHS_SMOD_E{year}_GLOBE_R2023A_54009_1000_V1_0").clip(final_aoi)

        Map.addLayer(
            ghs_pop,
            {
                "min": 0,
                "max": 125,
                "palette": ["#060606", "#337663", "#76c677", "#ffffff"]
            },
            f"GHS_POP: Population {year}",
            False
        )

        Map.addLayer(
            ghs_smod.mask(ghs_smod.neq(10)),
            {
                "min": 10,
                "max": 30,
                "palette": ['#7ab6f5', '#cdf57a', '#abcd66', '#375623', '#ffff00', '#a87000', '#732600', '#ff0000']
            },
            f"GHS_SMOD: Urbanization {year}",
            False
        )
    except Exception as e:
        st.warning(f"GHS data not available for {year}: {e}")

worldpop = ee.ImageCollection('WorldPop/GP/100m/pop_age_sex')\
    .filterBounds(final_aoi)\
    .filterDate('2020-01-01', '2021-01-01')\
    .mean()\
    .clip(final_aoi)

Map.addLayer(
    worldpop.select('population'),
    {
        "min": 0,
        "max": 200,
        "palette": ['#f7fcf0', '#ccebc5', '#7bccc4', '#2b8cbe', '#084081']
    },
    "WorldPop Population 2020",
    False
)

with st.expander("CORINE Legend (44 classes)"):

    col1_html, col2_html, col3_html = "", "", ""
    corine_codes = list(corine_classes.keys())
    corine_names = list(corine_classes.values())
    per_col = (len(corine_classes) + 2) // 3  # Divide evenly into 3 columns

    for idx, code in enumerate(corine_codes):
        name = corine_classes[code]
        color = corine_palette[idx]
        box = (
            f'<div style="display:flex;align-items:center;margin-bottom:4px;">'
            f'<div style="width:12px;height:12px;background:{color};margin-right:6px;"></div>'
            f'{code}: {name}</div>'
        )
        if idx < per_col:
            col1_html += box
        elif idx < 2 * per_col:
            col2_html += box
        else:
            col3_html += box

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between;">
            <div style="flex: 1; padding-right: 20px;">{col1_html}</div>
            <div style="flex: 1; padding-right: 20px;">{col2_html}</div>
            <div style="flex: 1;">{col3_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with st.expander("EUNIS Legend (43 classes)"):

    eunis_labels = {
        1: "Urban buildings", 2: "Suburban housing", 3: "Low density build",
        4: "Transport", 5: "Ports", 6: "Airports", 7: "Extractive industry",
        8: "Waste deposits", 9: "Construction", 10: "Parks", 11: "Arable land",
        12: "Crops (intensive)", 13: "Rice fields", 14: "Vineyards",
        15: "Fruit shrubs", 16: "Olive trees", 17: "Grassland",
        18: "Mixed crops", 19: "Garden crops", 20: "Low-intensity crops",
        21: "Wooded grassland", 22: "Broadleaf forest", 23: "Conifer forest",
        24: "Mixed woodland", 25: "Dry grasslands", 26: "Shrub heath",
        27: "Medit. brush", 28: "Fringes/clearings", 29: "Beaches/dunes",
        30: "Littoral rock", 31: "Sparse inland", 32: "Burnt land",
        33: "Snow/Ice", 34: "Inland shore", 35: "Peat bogs",
        36: "Salt marshes", 37: "Saline artificial", 38: "Littoral sand",
        39: "Rivers", 40: "Lakes", 41: "Lagoons", 42: "Estuaries",
        43: "Marine sand"
    }

    eunis_palette = [
        "#a50026", "#d73027", "#f46d43", "#fdae61", "#fee08b", "#ffffbf",
        "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850", "#006837", "#d4eeff",
        "#91bfdb", "#4575b4", "#313695", "#e6f598", "#ffffbf", "#fee08b",
        "#fdae61", "#f46d43", "#d73027", "#a50026", "#7fcdbb", "#41b6c4",
        "#1d91c0", "#225ea8", "#253494", "#081d58", "#d9f0a3", "#addd8e",
        "#78c679", "#41ab5d", "#238443", "#006837", "#fcbba1", "#fc9272",
        "#fb6a4a", "#ef3b2c", "#cb181d", "#a50f15", "#67000d", "#cccccc",
        "#969696"
    ]

    col1_html, col2_html, col3_html = "", "", ""
    per_col = (len(eunis_labels) + 2) // 3  # Divide into 3 equal parts

    for idx, i in enumerate(range(1, 44)):
        box = (
            f'<div style="display:flex;align-items:center;margin-bottom:4px;">'
            f'<div style="width:12px;height:12px;background:{eunis_palette[i-1]};margin-right:6px;"></div>'
            f'{i}: {eunis_labels[i]}</div>'
        )
        if idx < per_col:
            col1_html += box
        elif idx < 2 * per_col:
            col2_html += box
        else:
            col3_html += box

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between;">
            <div style="flex: 1; padding-right: 20px;">{col1_html}</div>
            <div style="flex: 1; padding-right: 20px;">{col2_html}</div>
            <div style="flex: 1;">{col3_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )



# --- Custom Toggleable Legend (HTML + JS) ---
legend_html = """
<div id="map-legend" style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 280px; 
    background-color: white; 
    border: 2px solid grey; 
    z-index: 9999; 
    font-size: 14px; 
    padding: 10px; 
    display: none;">
<b>Landscape Archetypes</b><br><hr>
"""

for desc, color in legend_dict.items():
    legend_html += f'<i style="background:{color};width:12px;height:12px;float:left;margin-right:8px;"></i>{desc}<br>'

legend_html += "</div>"

Map.get_root().html.add_child(folium.Element(legend_html))

# Toggle script
toggle_script = """
<script>
var legend = document.getElementById('map-legend');
var checkExist = setInterval(function() {
    var layers = document.querySelectorAll('.leaflet-control-layers-selector');
    layers.forEach(function(layer) {
        if (layer.nextSibling && layer.nextSibling.textContent.includes('Legend')) {
            layer.addEventListener('change', function() {
                legend.style.display = layer.checked ? 'block' : 'none';
            });
        }
    });
    if (layers.length > 0) clearInterval(checkExist);
}, 500);
</script>
"""
Map.get_root().html.add_child(folium.Element(toggle_script))

# Dummy layer to toggle legend
legend_layer = folium.FeatureGroup(name="Legend", show=False)
Map.add_child(legend_layer)

Map.add_child(folium.LayerControl())
Map.to_streamlit(height=600)

# --- Download Section for Displayed Layers ---
st.subheader("🧷 Quick Download")

# Use current AOI
download_region = final_aoi if isinstance(final_aoi, ee.Geometry) else final_aoi.geometry()
region_json = download_region.getInfo()  # Move to client-side for download

# Helper: Generate download URL
def get_download_url(image, label):
    try:
        url = image.getDownloadURL({
            'scale': 100,
            'crs': 'EPSG:3857',
            'region': region_json,
            'format': 'GeoTIFF'
        })
        st.markdown(
            f"[📁 Download {label} ({selected_year}) as GeoTIFF]({url})",
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f" Could not generate download for {label}: {e}")

# 1. CORINE (raw)
corine_raw = CLIPPED_CORINE[selected_year].toInt()
get_download_url(corine_raw, "CORINE Raw")

# 2. Archetypes (reclassified)
archetype_img = reclassify(corine_raw).clip(download_region).toInt()
get_download_url(archetype_img, "Landscape Archetypes")

# 3. EUNIS (reclassified)
try:
    def corine_to_eunis(image):
        landCoverToEunisNumeric = {
            111: 1, 112: 2, 121: 3, 122: 4, 123: 5, 124: 6,
            131: 7, 132: 8, 133: 9, 141: 10, 142: 1, 211: 11, 212: 12, 213: 13,
            221: 14, 222: 15, 223: 16, 231: 17, 241: 18, 242: 19, 243: 20,
            244: 21, 311: 22, 312: 23, 313: 24, 321: 25, 322: 26, 323: 27,
            324: 28, 331: 29, 332: 30, 333: 31, 334: 32, 335: 33, 411: 34,
            412: 35, 421: 36, 422: 37, 423: 38, 511: 39, 512: 40, 521: 41,
            522: 42, 523: 43
        }
        from_list = list(landCoverToEunisNumeric.keys())
        to_list = list(landCoverToEunisNumeric.values())
        return image.remap(from_list, to_list).rename('eunis')

    eunis_img = corine_to_eunis(corine_raw).clip(download_region).toInt()
    get_download_url(eunis_img, "EUNIS Reclassified")
except Exception:
    st.info("ℹ️ EUNIS layer not configured or skipped.")

with st.expander("Check this Population out!"):
    st.markdown("""
    Curious about how **population**, **urbanization**, and **age structures** have changed over time?

    📍 **Use this interactive app** to:

    - 🗺️ **Visualize** population density and degree of urbanization from **1975 to 2030**
    - 👥 Explore **WorldPop age and gender demographics** (2020)
    - 📊 **Download** results as **Excel tables** or **graph summaries** for your custom area

    🔧 **Note:** Use the **Draw Tool** on the map to outline your **Area of Interest (AOI)**. All statistics will be based on the area you draw.

    👉 [**Click here to launch the app**](https://desirmed.projects.earthengine.app/view/explore-population-and-sex-dynamics)

    """)


# -------------------- Export Options --------------------
st.subheader("📤 Export Options")

export_format = st.radio("Select Export Format", ["GeoTIFF", "SHP"])
selected_years = st.multiselect("Select CORINE Year(s)", ['2012', '2018'], default=['2012'])

export_folder = st.text_input("Drive folder name", value="desirmed/nbracer")
custom_prefix = st.text_input("File name prefix (base)", value="Archetypes")

def vectorize(image, geom, year):
    vectors = image.reduceToVectors(
        geometry=geom,
        geometryType='polygon',
        scale=100,
        reducer=ee.Reducer.countEvery(),
        maxPixels=1e13
    )
    return vectors.map(lambda f: f.set('year', year))

# Export to EE Asset
col1, col2 = st.columns(2)
export_base_name = f"{custom_prefix}_{selected_subregion}_{selected_year}"
region = final_aoi if isinstance(final_aoi, ee.Geometry) else final_aoi.geometry()

with col1:
    if st.button("Export to EE Asset"):
        asset_id = f"projects/ee-desmond/assets/{export_base_name}"
        task = ee.batch.Export.image.toAsset(
            image=archetype_img,
            description=export_base_name + "_Asset",
            assetId=asset_id,
            region=region,
            scale=100,
            maxPixels=1e13
        )
        task.start()
        st.success(f" Export to EE Asset started.\n📁 Asset ID: `{asset_id}`")

# Export to Drive
with col2:
    if st.button("Export Selected Years to Drive"):
        for year in selected_years:
            corine_img = CLIPPED_CORINE[year]
            archetype_img = reclassify(corine_img).clip(final_aoi)
            file_prefix = f"{custom_prefix}_{selected_subregion}_{year}"

            if export_format == "GeoTIFF":
                task = ee.batch.Export.image.toDrive(
                    image=archetype_img,
                    description=file_prefix + "_GeoTIFF",
                    folder=export_folder,
                    fileNamePrefix=file_prefix,
                    region=region,
                    scale=100,
                    maxPixels=1e13
                )
                task.start()
                st.success(f" GeoTIFF export for {year} started to Drive/{export_folder}/{file_prefix}.tif")

            elif export_format == "SHP":
                vector_fc = vectorize(archetype_img, region, year)
                task = ee.batch.Export.table.toDrive(
                    collection=vector_fc,
                    description=file_prefix + "_SHP",
                    folder=export_folder,
                    fileNamePrefix=file_prefix + "_Vector",
                    fileFormat='SHP'
                )
                task.start()
                st.success(f" SHP export for {year} started to Drive/{export_folder}/{file_prefix}_Vector.zip")

st.info("🕒 To check export progress, go to the [Earth Engine Code Editor](https://code.earthengine.google.com/) and click on the 'Tasks' tab.")

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
# st.sidebar.markdown(f"**Local Time (Amsterdam):** {current_time}")