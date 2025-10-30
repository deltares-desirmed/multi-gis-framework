import streamlit as st
import ee
import folium
import leafmap.foliumap as leafmap
from utils_ee import initialize_earth_engine  #  Auth from secret config

st.set_page_config(layout="wide")

#  Initialize Earth Engine
initialize_earth_engine()


st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | 
    [GitHub](https://github.com/desirmed)
    """
)

st.title("Land Use/cover & Habitats")

#  Add EE tile layer registration
folium.Map.add_ee_tile_layer = lambda self, ee_img, vis_params, name: folium.TileLayer(
    tiles=ee_img.getMapId(vis_params)["tile_fetcher"].url_format,
    attr="Google Earth Engine",
    name=name,
    overlay=True,
    control=True
).add_to(self)

#  Control code visibility
show_code = False

if show_code:
    with st.expander("See source code", expanded=False):
        with st.echo():
            m = leafmap.Map(center=[50, 10], zoom=5)
            corine = ee.Image("COPERNICUS/CORINE/V20/100m/2018")
            vis_params = {
                "bands": ["landcover"],
                "min": 111,
                "max": 523,
                "palette": [
                    "#e6004d", "#ff0000", "#cc4df2", "#cc0000", "#e6cccc", "#e6cce6",
                    "#a600cc", "#a64dcc", "#ff4dff", "#ffa6ff", "#ffe6ff", "#ffffa8",
                    "#ffff00", "#e6e600", "#e68000", "#f2a64d", "#e6a600", "#e6e64d",
                    "#ffe6a6", "#ffe64d", "#e6cc4d", "#f2cca6", "#80ff00", "#00a600",
                    "#4dff00", "#ccf24d", "#a6ff80", "#a6e64d", "#a6f200", "#e6e6e6",
                    "#cccccc", "#ccffcc", "#000000", "#a6e6cc", "#a6a6ff", "#4d4dff",
                    "#ccccff", "#e6e6ff", "#a6a6e6", "#00ccf2", "#80f2e6", "#00ffa6",
                    "#a6ffe6", "#e6f2ff"]
            }
            m.add_ee_tile_layer(corine, vis_params, "CORINE Land Cover 2018")
else:
    m = leafmap.Map(center=[50, 10], zoom=5)
    corine = ee.Image("COPERNICUS/CORINE/V20/100m/2018")
    vis_params = {
        "bands": ["landcover"],
        "min": 111,
        "max": 523,
        "palette": [
            "#e6004d", "#ff0000", "#cc4df2", "#cc0000", "#e6cccc", "#e6cce6",
            "#a600cc", "#a64dcc", "#ff4dff", "#ffa6ff", "#ffe6ff", "#ffffa8",
            "#ffff00", "#e6e600", "#e68000", "#f2a64d", "#e6a600", "#e6e64d",
            "#ffe6a6", "#ffe64d", "#e6cc4d", "#f2cca6", "#80ff00", "#00a600",
            "#4dff00", "#ccf24d", "#a6ff80", "#a6e64d", "#a6f200", "#e6e6e6",
            "#cccccc", "#ccffcc", "#000000", "#a6e6cc", "#a6a6ff", "#4d4dff",
            "#ccccff", "#e6e6ff", "#a6a6e6", "#00ccf2", "#80f2e6", "#00ffa6",
            "#a6ffe6", "#e6f2ff"]
    }
    m.add_ee_tile_layer(corine, vis_params, "CORINE Land Cover 2018")

#  Legend content
labels = [
    "Continuous urban fabric", "Discontinuous urban fabric", "Industrial/Commercial units",
    "Road and rail networks", "Port areas", "Airports", "Mineral extraction sites",
    "Dump sites", "Construction sites", "Green urban areas", "Sport/leisure facilities",
    "Non-irrigated arable land", "Permanently irrigated land", "Rice fields",
    "Vineyards", "Fruit trees and berry plantations", "Olive groves", "Pastures",
    "Annual crops with permanent crops", "Complex cultivation patterns",
    "Agriculture + natural areas", "Agro-forestry areas", "Broad-leaved forest",
    "Coniferous forest", "Mixed forest", "Natural grassland", "Moors and heathland",
    "Sclerophyllous vegetation", "Transitional woodland-shrub", "Beaches, dunes, sands",
    "Bare rocks", "Sparsely vegetated areas", "Burnt areas", "Glaciers and perpetual snow",
    "Inland wetlands", "Peat bogs", "Salt marshes", "Salines", "Intertidal flats",
    "Water courses", "Water bodies", "Coastal lagoons", "Estuaries", "Sea and ocean"]

colors = [
    "#ff0000", "#e97419", "#a00000", "#ffff64", "#009900", "#006400",
    "#00ff00", "#00a000", "#dcdcdc", "#c8c8c8", "#ff0000", "#ffffa8",
    "#ffff00", "#e6e600", "#e68000", "#f2a64d", "#e6a600", "#e6e64d",
    "#ffe6a6", "#ffe64d", "#e6cc4d", "#f2cca6", "#80ff00", "#00a600",
    "#4dff00", "#ccf24d", "#a6ff80", "#a6e64d", "#a6f200", "#e6e6e6",
    "#cccccc", "#ccffcc", "#000000", "#a6e6cc", "#a6a6ff", "#4d4dff",
    "#ccccff", "#e6e6ff", "#a6a6e6", "#00ccf2", "#80f2e6", "#00ffa6",
    "#a6ffe6", "#e6f2ff"]

legend_html = """
<div id=\"map-legend\" style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 300px; height: 400px; 
    overflow: auto; 
    background-color: white; 
    border:2px solid grey; 
    z-index:9999; 
    font-size:14px;
    padding: 10px;
    display: none;">
<b>CORINE Land Cover 2018</b><br>
<hr>
"""
for label, color in zip(labels, colors):
    legend_html += f'<i style="background:{color};width:10px;height:10px;float:left;margin-right:8px;"></i>{label}<br>'
legend_html += "</div>"
m.get_root().html.add_child(folium.Element(legend_html))


# --- Archetype reclassification with custom colors ---
archetypes = {
    '1': [111,112,121,122],  # Urban
    '2': [123,124],          # Transport
    '3': [131,132,133],      # Extraction
    '4': [141,142],          # Greenspace
    '5': [211,212,213],      # Arable land
    '6': [221,222,223,231],  # Permanent crops
    '7': [311,312,313,321,322,323,324],  # Forests
    '8': [332,333,334,335],  # Sparse/Barren
    '9': [241,242,243,244],  # Mosaic crops
    '10': [331],             # Sand dunes
    '11': [421,422,423],     # Wetlands
    '12': [411,412],         # Inland wetlands
    '13': [511,512],         # Rivers/Lakes
    '14': [521,522,523]      # Marine/coastal
}
arch_from, arch_to = [], []

# Custom color palette for archetypes based on earlier example
arch_palette = [
    '#636363',  # Urban
    '#969696',  # Transport
    '#cccccc',  # Extraction
    '#91d700',  # Greenspace
    '#91d700',  # Arable land
    '#df9f00',  # Permanent crops
    '#80ff00',  # Forests
    '#a63603',  # Sparse/Barren
    '#78c679',  # Mosaic crops
    '#ffcc99',  # Sand dunes
    '#7fff00',  # Wetlands
    '#a6e6ff',  # Inland wetlands
    '#4da6ff',  # Rivers/Lakes
    '#00bfff'   # Marine/coastal
]

for k, v in archetypes.items():
    arch_from.extend(v)
    arch_to.extend([int(k)] * len(v))

def reclassify_archetype(img):
    return img.remap(arch_from, arch_to).rename("archetype")

# --- EUNIS reclassification ---
eunis_map = {
    111: 1, 112: 2, 121: 3, 122: 4, 123: 5, 124: 6, 131: 7, 132: 8, 133: 9,
    141: 10, 142: 1, 211: 11, 212: 12, 213: 13, 221: 14, 222: 15, 223: 16,
    231: 17, 241: 18, 242: 19, 243: 20, 244: 21, 311: 22, 312: 23, 313: 24,
    321: 25, 322: 26, 323: 27, 324: 28, 331: 29, 332: 30, 333: 31, 334: 32,
    335: 33, 411: 34, 412: 35, 421: 36, 422: 37, 423: 38, 511: 39, 512: 40,
    521: 41, 522: 42, 523: 43
}

eunis_from = list(eunis_map.keys())
eunis_to = list(eunis_map.values())

# Your custom EUNIS palette
eunis_palette = [
    '#b22222', '#ff4500', '#ffa07a', '#8b4513', '#d2691e', '#808080', '#556b2f',
    '#a0522d', '#d2b48c', '#deb887', '#32cd32', '#adff2f', '#ff7f50', '#8fbc8f',
    '#228b22', '#f4a460', '#006400', '#ffe4b5', '#6b8e23', '#f0e68c', '#d2b48c',
    '#008000', '#3cb371', '#20b2aa', '#7cfc00', '#8b0000', '#b0c4de', '#87cefa',
    '#fa8072', '#add8e6', '#708090', '#d3d3d3', '#556b2f', '#4169e1', '#00bfff',
    '#1e90ff', '#6495ed', '#ffdab9', '#87ceeb', '#2171b5', '#ffdab9', '#2171b5',
    '#87cefa'
]

def reclassify_eunis(img):
    return img.remap(eunis_from, eunis_to).rename("eunis")

# --- Base CORINE 2018 image ---
corine_2018 = ee.Image("COPERNICUS/CORINE/V20/100m/2018").select("landcover")

# --- Reclassify images ---
archetype_img = reclassify_archetype(corine_2018)
eunis_img = reclassify_eunis(corine_2018)


# --- Add layers to map ---
m.add_ee_tile_layer(archetype_img, {
    "min": 1, "max": 14, "palette": arch_palette
}, "Archetypes (14 Classes)")

m.add_ee_tile_layer(eunis_img, {
    "min": 1, "max": 43, "palette": eunis_palette
}, "EUNIS (43 Classes)")


# Add toggle functionality
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
m.get_root().html.add_child(folium.Element(toggle_script))

# Dummy layer to toggle legend
legend_layer = folium.FeatureGroup(name="Legend", show=False)
m.add_child(legend_layer)

# Add controls and show map
m.add_layer_control()
m.to_streamlit(height=700)

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

with st.expander("CORINE Legend (44 classes)"):
    corine_codes = list(corine_classes.keys())
    corine_names = list(corine_classes.values())
    corine_colors = vis_params["palette"]
    col1_html, col2_html, col3_html = "", "", ""
    per_col = (len(corine_codes) + 2) // 3

    for idx, code in enumerate(corine_codes):
        name = corine_names[idx]
        color = corine_colors[idx]
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
    col1_html, col2_html, col3_html = "", "", ""
    per_col = (len(eunis_labels) + 2) // 3

    for idx, class_id in enumerate(eunis_labels.keys()):
        color = eunis_palette[idx]
        label = f"{class_id}: {eunis_labels[class_id]}"
        box = (
            f'<div style="display:flex;align-items:center;margin-bottom:4px;">'
            f'<div style="width:12px;height:12px;background:{color};margin-right:6px;"></div>'
            f'{label}</div>'
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




# with st.expander("See source code"):
#     with st.echo():
#         m = leafmap.Map()
#         m.split_map(
#             left_layer="ESA WorldCover 2020 S2 FCC", right_layer="ESA WorldCover 2020"
#         )
#         m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
# m.to_streamlit(height=700)

import streamlit as st
import datetime
from zoneinfo import ZoneInfo  # Requires Python 3.9+

logo = "https://www.desirmed.eu/theme17/img/logos/6_Deltares.png"
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
st.sidebar.markdown(f"© {current_year}  Foundation Deltares")

# Display date and time in Amsterdam timezone
last_updated = amsterdam_time.strftime("%B %d, %Y")
current_time = amsterdam_time.strftime("%H:%M:%S")

st.sidebar.markdown(f"**Last Updated:** {last_updated}")
# st.sidebar.markdown(f"**Local Time (Amsterdam):** {current_time}")