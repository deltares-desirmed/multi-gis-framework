import streamlit as st
import ee
import folium
import geemap.foliumap as geemap 
from utils_ee import initialize_earth_engine  #  Auth from secret config
import zipfile
import os

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

# Optional: Upload user AOI shapefile
uploaded = st.file_uploader("Optional: Upload your own AOI shapefile (.zip)", type=["zip"])
uploaded_aoi = None  # Define variable early to avoid NameError

if uploaded:
    with zipfile.ZipFile(uploaded, 'r') as zf:
        zf.extractall("temp_shp")
    try:
        uploaded_aoi = geemap.shp_to_ee("temp_shp")
        st.success("AOI uploaded successfully.")
    except Exception as e:
        st.error(f"Error reading shapefile: {e}")

# AOI used: uploaded shapefile or dropdown
final_aoi = uploaded_aoi if uploaded_aoi else aoi


# Select CORINE year
CORINE_YEARS = {
    '2012': ee.Image('COPERNICUS/CORINE/V20/100m/2012').select('landcover'),
    '2018': ee.Image('COPERNICUS/CORINE/V20/100m/2018').select('landcover')
}
selected_year = st.selectbox("Select CORINE Year", ['2012', '2018'])

# Reclassification logic
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

corine_img = CORINE_YEARS[selected_year]
archetype_img = reclassify(corine_img).clip(final_aoi)

# Map Display
st.subheader(f"Reclassified Landscape Archetypes ({selected_year})")
Map = geemap.Map(center=[51, 3], zoom=8)
Map.addLayer(final_aoi.style(**{
    "color": "red", "fillColor": "00000000", "width": 2
}), {}, "AOI Boundary")

Map.addLayer(archetype_img, {"min": 1, "max": 14, "palette": palette}, f"Archetypes {selected_year}")
# Create the map
Map = geemap.Map(center=[51, 3], zoom=8)
Map.addLayer(final_aoi.style(**{
    "color": "red", "fillColor": "00000000", "width": 2
}), {}, "AOI Boundary")
Map.addLayer(archetype_img, {"min": 1, "max": 14, "palette": palette}, f"Archetypes {selected_year}")

# --- Custom Toggleable Legend (HTML + JS) ---

# HTML for legend box
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

# Add legend to map
Map.get_root().html.add_child(folium.Element(legend_html))

# Toggle script for showing/hiding legend
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

# Add dummy layer to trigger legend toggle
legend_layer = folium.FeatureGroup(name="Legend", show=False)
Map.add_child(legend_layer)

# Add controls and render map
Map.add_child(folium.LayerControl())
Map.to_streamlit(height=600)


# Export Buttons
col1, col2, col3, col4 = st.columns(4)
export_base_name = f"Archetypes_{selected_subregion}_{selected_year}"

with col1:
    if st.button("Export to EE Asset"):
        task = ee.batch.Export.image.toAsset(
            image=archetype_img,
            description=export_base_name + "_Asset",
            assetId=f"projects/ee-desmond/assets/{export_base_name}",
            region=final_aoi.geometry(),
            scale=100,
            maxPixels=1e13
        )
        task.start()
        st.success("Export to asset started.")

with col2:
    if st.button("Export to Drive (GeoTIFF)"):
        task = ee.batch.Export.image.toDrive(
            image=archetype_img,
            description=export_base_name + "_Drive",
            folder="nbracer",
            fileNamePrefix=export_base_name,
            region=final_aoi.geometry(),
            scale=100,
            maxPixels=1e13
        )
        task.start()
        st.success("Export to Drive (GeoTIFF) started.")

# Vectorization and Export
def vectorize(image, geom, year):
    vectors = image.reduceToVectors(
        geometry=geom,
        geometryType='polygon',
        scale=100,
        reducer=ee.Reducer.countEvery(),
        maxPixels=1e13
    )
    return vectors.map(lambda f: f.set('year', year))

with col3:
    if st.button("Export as Vector (SHP)"):
        vector_fc = vectorize(archetype_img, final_aoi.geometry(), selected_year)
        task = ee.batch.Export.table.toDrive(
            collection=vector_fc,
            description=export_base_name + "_Shapefile",
            folder="nbracer",
            fileNamePrefix=export_base_name + "_Vector",
            fileFormat='SHP'
        )
        task.start()
        st.success("Vector export (SHP) started.")
