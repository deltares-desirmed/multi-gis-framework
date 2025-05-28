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
st.title("Landscape Archetypes Classification (CORINE)")

# Step 1: AOI selection via dropdowns
countries = admin0.aggregate_array('shapeName').getInfo()
selected_country = st.selectbox("Select Country", sorted(countries))
country_geom = admin0.filter(ee.Filter.eq('shapeName', selected_country)).geometry()

regions = admin1.filterBounds(country_geom).aggregate_array('shapeName').getInfo()
selected_region = st.selectbox("Select Region", sorted(regions))
region_geom = admin1.filter(ee.Filter.eq('shapeName', selected_region)).geometry()

subregions = admin2.filterBounds(region_geom).aggregate_array('shapeName').getInfo()
selected_subregion = st.selectbox("Select Sub-region", sorted(subregions))
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

def reclassify(img):
    remapped = img.remap(from_list, to_list).rename('archetype')
    return remapped.updateMask(remapped.neq(0))

corine_img = CLIPPED_CORINE[selected_year]

archetype_img = reclassify(corine_img).clip(final_aoi)

# Map Display
st.subheader(f"Reclassified Landscape Archetypes ({selected_year})")
Map = geemap.Map(center=[51, 3], zoom=8)

# Map.addLayer(final_aoi.style(**{
#     "color": "red", "fillColor": "00000000", "width": 2
# }), {}, "AOI Boundary")

# Map.addLayer(archetype_img, {"min": 1, "max": 14, "palette": palette}, f"Archetypes {selected_year}")
# Create the map
# Compute center coordinates dynamically
# Handle both ee.Geometry and ee.FeatureCollection for centroid
aoi_geom_for_centroid = final_aoi if isinstance(final_aoi, ee.Geometry) else final_aoi.geometry()
aoi_centroid = aoi_geom_for_centroid.centroid().coordinates().getInfo()

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


with st.expander("CORINE Legend (44 classes)"):
    for code, name in corine_classes.items():
        color = corine_palette[list(corine_classes.keys()).index(code)]
        st.markdown(
            f'<div style="display:flex;align-items:center;">'
            f'<div style="width:12px;height:12px;background:{color};margin-right:6px;"></div>'
            f'{code}: {name}</div>',
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

# -------------------- Export Options --------------------
st.subheader("📤 Export Options")

export_format = st.radio("Select Export Format", ["GeoTIFF", "SHP"])
selected_years = st.multiselect("Select CORINE Year(s)", ['2012', '2018'], default=['2012'])

export_folder = st.text_input("Drive folder name", value="nbracer")
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
