import streamlit as st
import ee
import leafmap.foliumap as leafmap
import folium
from utils_ee import initialize_earth_engine

#  Initialize Earth Engine Using Cloud Secrets
st.set_page_config(layout="wide")
initialize_earth_engine()

# Streamlit Sidebar
st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | 
    [GitHub](https://github.com/deltares-desirmed)
    """
)

st.title("Functional Units-cORINE 2018")

#  Register Custom Method to Add EE Tile Layers
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
                "#a6ffe6", "#e6f2ff"
            ]
        }

        m.add_ee_tile_layer(corine, vis_params, "CORINE Land Cover 2018")

        #  Create Legend HTML Content
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
            "Water courses", "Water bodies", "Coastal lagoons", "Estuaries", "Sea and ocean"
        ]

        colors = [
            "#ff0000", "#e97419", "#a00000", "#ffff64", "#009900", "#006400",
            "#00ff00", "#00a000", "#dcdcdc", "#c8c8c8", "#ff0000", "#ffffa8",
            "#ffff00", "#e6e600", "#e68000", "#f2a64d", "#e6a600", "#e6e64d",
            "#ffe6a6", "#ffe64d", "#e6cc4d", "#f2cca6", "#80ff00", "#00a600",
            "#4dff00", "#ccf24d", "#a6ff80", "#a6e64d", "#a6f200", "#e6e6e6",
            "#cccccc", "#ccffcc", "#000000", "#a6e6cc", "#a6a6ff", "#4d4dff",
            "#ccccff", "#e6e6ff", "#a6a6e6", "#00ccf2", "#80f2e6", "#00ffa6",
            "#a6ffe6", "#e6f2ff"
        ]

        legend_html = """
        <div id="map-legend" style="
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

        # Inject Legend HTML
        m.get_root().html.add_child(folium.Element(legend_html))

        # Inject JavaScript to Control Legend Visibility via Layer Control
        js_toggle = """
        <script>
        var legend = document.getElementById('map-legend');
        var checkExist = setInterval(function() {
            var layers = document.querySelectorAll('.leaflet-control-layers-selector');
            layers.forEach(function(layer) {
                if (layer.nextSibling && layer.nextSibling.textContent.includes('Legend')) {
                    layer.addEventListener('change', function() {
                        if (layer.checked) {
                            legend.style.display = 'block';
                        } else {
                            legend.style.display = 'none';
                        }
                    });
                }
            });
            if (layers.length > 0) clearInterval(checkExist);
        }, 500);
        </script>
        """
        m.get_root().html.add_child(folium.Element(js_toggle))

        # Add Legend as a Dummy Layer to Appear in the Layer Control
        legend_layer = folium.FeatureGroup(name="Legend", show=False)
        m.add_child(legend_layer)

        # Finalize Map Display
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