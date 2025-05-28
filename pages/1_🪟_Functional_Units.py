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
    [GitHub](https://github.com/deltares-desirmed)
    """
)

st.title("Functional Unit - coRINE 2018")

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


# Reclassification rules
archetypes = {
    '1': [111,112,121,122], '2': [123,124], '3': [131,132,133],
    '4': [141,142], '5': [211,212,213], '6': [221,222,223,231],
    '7': [311,312,313,321,322,323,324], '8': [332,333,334,335],
    '9': [241,242,243,244], '10': [331], '11': [421,422,423],
    '12': [411,412], '13': [511,512], '14': [521,522,523]
}
arch_from, arch_to, arch_palette = [], [], []
for k, v in archetypes.items():
    arch_from.extend(v)
    arch_to.extend([int(k)] * len(v))
    arch_palette.append("#{:06x}".format(0x100000 + int(k)*123456 % 0xFFFFFF))  # simple varied colors

def reclassify_archetype(img):
    return img.remap(arch_from, arch_to).rename("archetype")

# CORINE to EUNIS mapping
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

def reclassify_eunis(img):
    return img.remap(eunis_from, eunis_to).rename("eunis")

# CORINE base
corine_2018 = ee.Image("COPERNICUS/CORINE/V20/100m/2018").select("landcover")

# Reclassified images
archetype_img = reclassify_archetype(corine_2018)
eunis_img = reclassify_eunis(corine_2018)

# Add all to map
m.add_ee_tile_layer(archetype_img, {
    "min": 1, "max": 14, "palette": arch_palette
}, "Archetypes (14 Classes)")

m.add_ee_tile_layer(eunis_img, {
    "min": 1, "max": 43, "palette": arch_palette  # You can customize this palette too
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

st.sidebar.markdown(f"**Last Updated:** {last_updated} | {current_time}")
# st.sidebar.markdown(f"**Local Time (Amsterdam):** {current_time}")