import datetime
import ee
import streamlit as st
from utils_ee import initialize_earth_engine
import geemap.foliumap as geemap
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


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


# Load Microsoft Buildings for Croatia
ms_buildings_hr = ee.FeatureCollection('projects/sat-io/open-datasets/MSBuildings/Croatia')

# Optional: Filter to your region (e.g., Split)
split_bbox = ee.Geometry.BBox(16.3, 43.4, 16.6, 43.6)
ms_buildings_split = ms_buildings_hr.filterBounds(split_bbox)

# Style the layer (outline only, transparent fill)
ms_building_vis = ms_buildings_split.style(
    color='FF5500',
    fillColor='00000000',
    width=1
)

# Create tile layer
ms_building_layer = geemap.ee_tile_layer(ms_building_vis, {}, "Buildings (Microsoft)")


# Load GRIP4 Europe roads
grip4_europe = ee.FeatureCollection("projects/sat-io/open-datasets/GRIP4/Europe")

# Filter to the Split region
split_bbox = ee.Geometry.BBox(16.0, 42.8, 17.0, 43.7)
split_roads = grip4_europe.filterBounds(split_bbox)

# Style the roads (thin red lines)
road_style = split_roads.style(color='FF5500', width=1)

# Convert to tile layer
roads_layer = geemap.ee_tile_layer(road_style, {}, "Roads (GRIP4)")


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
    "Floods HP": hp_layer,
    "ESA Land Cover": geemap.ee_tile_layer(esa, esa_vis, "ESA Land Cover"),
    "Dynamic World": geemap.ee_tile_layer(dw, {}, "Dynamic World Land Cover"),
    "ESRI Land Cover": geemap.ee_tile_layer(esri, esri_vis, "ESRI Land Cover"),
    "Floods MP": mp_layer,
    "Floods LP": lp_layer,
    "CORINE 2012": corine_2012,
    "CORINE 2018": corine_2018,
    **pop_tile_layers,  # Unpack population layers
    

    
}
    layers["Buildings (Microsoft)"] = ms_building_layer
    layers["Roads (GRIP4)"] = roads_layer


    
    options = list(layers.keys())
    left = st.selectbox("Select a left layer", options, index=1)
    right = st.selectbox("Select a right layer", options, index=0)

    def get_layer(layer_key):
        if layer_key not in layers:
            return None
        layer_obj = layers[layer_key]
        if layer_obj == "PMTILES_BUILDINGS":
            return geemap.EmptyTileLayer(name="Buildings (Overture)")
        elif layer_obj == "PMTILES_ROADS":
            return geemap.EmptyTileLayer(name="Roads (Overture)")
        else:
            return layer_obj

    Map.split_map(get_layer(left), get_layer(right))


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

    elif legend == "Buildings (Microsoft)":
        Map.add_legend(
            title="Microsoft Buildings",
            legend_dict={
                "Building Footprint": "#FF5500"
            }
        )
    elif legend == "Roads (GRIP4)":
        Map.add_legend(
            title="GRIP4 Roads",
            legend_dict={"Roads": "#FF5500"}
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


# ---------------------- Settlement Selection ----------------------
with st.expander("📍 Select Settlement", expanded=True):
    settlement_names = population_fc.aggregate_array("NA_IME").distinct().sort().getInfo()
    settlement_name = st.selectbox("Select a Settlement", ["All Settlements"] + settlement_names)

    if settlement_name != "All Settlements":
        settlement_fc = population_fc.filter(ee.Filter.eq("NA_IME", settlement_name))
        settlement_geom = settlement_fc.first().geometry()
        filtered_buildings = ms_buildings_split.filterBounds(settlement_geom)
        filtered_roads = split_roads.filterBounds(settlement_geom)
    else:
        settlement_fc = population_fc
        settlement_geom = settlement_fc.geometry()
        filtered_buildings = ms_buildings_split
        filtered_roads = split_roads


# ---------------------- Exposure Analysis Panel ----------------------
with st.expander("📊 Step 2- CRICS - Exposure", expanded=True):
    scenario = st.selectbox("Select Flood Scenario for Exposure", ["High Probability", "Medium Probability", "Low Probability"])
    flood_geom = {
        "High Probability": floods_hp_img.geometry(),
        "Medium Probability": floods_mp_img.geometry(),
        "Low Probability": floods_lp_img.geometry()
    }[scenario]

    filtered_fc = settlement_fc.filterBounds(flood_geom)

    indicator = st.selectbox("Select Exposure Indicator", ["Population", "Roads", "Buildings"])

    if indicator == "Population":
        selected_year = st.selectbox("Select Year", ["2025", "2030"])
        selected_property = f"pop_{selected_year}"
        try:
            total_pop = settlement_fc.aggregate_sum(selected_property).getInfo()
            st.metric(f"Total Population Exposed ({selected_year})", f"{int(total_pop):,}")
        except Exception:
            st.error("Population data not available or aggregation failed.")

    elif indicator == "Roads":
        try:
            total_length = filtered_roads.geometry().length().divide(1000).getInfo()  # in km
            st.metric("Total Road Length Exposed (GRIP4)", f"{total_length:.2f} km")
        except Exception:
            st.error("Road data could not be computed.")

    elif indicator == "Buildings":
        try:
            building_count = filtered_buildings.size().getInfo()
            st.metric("Total Building Count (Microsoft)", f"{building_count:,}")
        except Exception:
            st.error("Building count computation failed.")


# ---------------------- Vulnerability Analysis Panel ----------------------
with st.expander("⚠️ Step 2- CRICS - Vulnerability", expanded=True):
    vuln_option = st.selectbox(
        "Select Vulnerability Group",
        ["Children (0–10)", "Elderly (65+)", "Female Total", "Male Total"]
    )

    children_props = [
        "female_F_0_2020", "female_F_5_2020", "female_F_10_2020",
        "male_M_0_2020", "male_M_5_2020", "male_M_10_2020"
    ]

    elderly_props = [
        "female_F_65_2020", "female_F_70_2020", "female_F_75_2020", "female_F_80_2020",
        "male_M_65_2020", "male_M_70_2020", "male_M_75_2020", "male_M_80_2020"
    ]

    try:
        if vuln_option == "Children (0–10)":
            total_children = sum(settlement_fc.aggregate_sum(p).getInfo() for p in children_props)
            st.metric("Children Exposed (0–10)", f"{int(total_children):,}")
        elif vuln_option == "Elderly (65+)":
            total_elderly = sum(settlement_fc.aggregate_sum(p).getInfo() for p in elderly_props)
            st.metric("Elderly (65+) Exposed", f"{int(total_elderly):,}")
        elif vuln_option == "Female Total":
            female_props = [p for p in settlement_fc.first().propertyNames().getInfo() if p.startswith("female_")]
            total_females = sum(settlement_fc.aggregate_sum(p).getInfo() for p in female_props)
            st.metric("Female Population Exposed", f"{int(total_females):,}")
        elif vuln_option == "Male Total":
            male_props = [p for p in settlement_fc.first().propertyNames().getInfo() if p.startswith("male_")]
            total_males = sum(settlement_fc.aggregate_sum(p).getInfo() for p in male_props)
            st.metric("Male Population Exposed", f"{int(total_males):,}")
    except Exception:
        st.error("⚠️ Could not compute vulnerability statistics. Please check property names and data availability.")


# ---------------------- Risk Assessment Panel ----------------------
# ---------------------- Risk Assessment Panel ----------------------
with st.expander("📉 Flood Risk Assessment", expanded=True):
    st.markdown("This panel estimates at-risk exposure using flood raster pixel coverage inside the selected settlement.")

    selected_year = st.selectbox("Select Population Year", ["2025", "2030"])
    selected_property = f"pop_{selected_year}"
    scenario = st.selectbox("Select Flood Scenario", ["High Probability", "Medium Probability", "Low Probability"])

    try:
        # Step 1: Get flood raster image based on selected scenario
        flood_raster = {
            "High Probability": floods_hp_img,
            "Medium Probability": floods_mp_img,
            "Low Probability": floods_lp_img
        }[scenario]

        # Step 2: Count flood pixels within the selected settlement
        flood_pixel_count_dict = flood_raster.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=settlement_geom,
            scale=30,
            maxPixels=1e13
        ).getInfo()

        flood_pixels = list(flood_pixel_count_dict.values())[0] or 0
        flood_area = flood_pixels * 30 * 30  # pixel area = 900 m²
        settlement_area = settlement_geom.area().getInfo()  # m²

        proportion_affected = flood_area / settlement_area if settlement_area else 0

        # Step 3: Total values from the full settlement
        total_pop = settlement_fc.aggregate_sum(selected_property).getInfo()
        total_children = sum(settlement_fc.aggregate_sum(p).getInfo() for p in children_props)
        total_elderly = sum(settlement_fc.aggregate_sum(p).getInfo() for p in elderly_props)
        total_road_km = filtered_roads.geometry().length().divide(1000).getInfo()
        total_buildings = filtered_buildings.size().getInfo()

        # Step 4: Compute affected using flood proportion
        exposed_pop = total_pop * proportion_affected
        exposed_children = total_children * proportion_affected
        exposed_elderly = total_elderly * proportion_affected
        exposed_roads_km = total_road_km * proportion_affected
        exposed_buildings_count = total_buildings * proportion_affected

        # Step 5: Percentages
        pct_pop = (exposed_pop / total_pop * 100) if total_pop else 0
        pct_children = (exposed_children / total_children * 100) if total_children else 0
        pct_elderly = (exposed_elderly / total_elderly * 100) if total_elderly else 0
        pct_roads = (exposed_roads_km / total_road_km * 100) if total_road_km else 0
        pct_buildings = (exposed_buildings_count / total_buildings * 100) if total_buildings else 0

        # Step 6: Display results
        st.metric(f"🧍 Exposed Population ({selected_year})", f"{int(exposed_pop):,}", f"{pct_pop:.1f}%")
        st.metric("🧒 Vulnerable Children (0–10)", f"{int(exposed_children):,}", f"{pct_children:.1f}%")
        st.metric("👵 Vulnerable Elderly (65+)", f"{int(exposed_elderly):,}", f"{pct_elderly:.1f}%")
        st.metric("🛣️ Roads at Risk", f"{exposed_roads_km:.2f} km", f"{pct_roads:.1f}%")
        st.metric("🏘️ Buildings at Risk", f"{int(exposed_buildings_count):,}", f"{pct_buildings:.1f}%")

        st.success(f"✔ Risk assessment for {scenario} flood scenario using {selected_year} population and vulnerability data completed.")
    except Exception as e:
        st.error(f"⚠️ Error during risk summary: {str(e)}")


with st.expander(" Risk Summary", expanded=True):
    st.markdown("Visual breakdown of exposure indicators, actual values at risk, and composite risk index dynamics.")

    # Data prep
    indicators = ['Exposed Population', 'Vulnerable Children (0–10)', 'Vulnerable Elderly (65+)', 'Roads at Risk', 'Buildings at Risk']
    raw_values = [exposed_pop, exposed_children, exposed_elderly, exposed_roads_km, exposed_buildings_count]
    percentages = [pct_pop, pct_children, pct_elderly, pct_roads, pct_buildings]
    weights = [0.3, 0.2, 0.2, 0.15, 0.15]
    weighted_contrib = [p * w for p, w in zip(percentages, weights)]
    risk_index = sum(weighted_contrib)

    df = pd.DataFrame({
        "Indicator": indicators,
        "Exposed Value": raw_values,
        "Exposure (%)": percentages,
        "Weight": weights,
        "Weighted Contribution": weighted_contrib
    })

    # Row 1: Bar of exposed values and Pie
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📦 Actual Values at Risk**")
        fig_val = px.bar(df, x="Indicator", y="Exposed Value", color="Indicator",
                         title="Quantity of Assets/People at Risk", text_auto='.2s')
        st.plotly_chart(fig_val, use_container_width=True)

    with col2:
        st.markdown("**📎 Contribution to Risk Index**")
        fig_pie = px.pie(df, names="Indicator", values="Weighted Contribution",
                         title="Weighted Share of Composite Risk Index")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Row 2: Violin and new Total vs At-Risk comparison
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**🎻 Risk Distribution by Indicator & Type**")

        # Simulate data for violin plot
        noise_scale = 0.4
        num_points = 50
        use_facet = False

        violin_data = []
        for i, indicator in enumerate(indicators):
            raw_sim = np.random.normal(loc=percentages[i], scale=noise_scale, size=num_points)
            weighted_sim = np.random.normal(loc=weighted_contrib[i], scale=noise_scale, size=num_points)

            for val in raw_sim:
                violin_data.append({
                    "Indicator": indicator,
                    "Risk Type": "Raw %",
                    "Value": val,
                    "Settlement": settlement_name,
                    "Flood Scenario": scenario,
                    "Year": selected_year
                })
            for val in weighted_sim:
                violin_data.append({
                    "Indicator": indicator,
                    "Risk Type": "Weighted %",
                    "Value": val,
                    "Settlement": settlement_name,
                    "Flood Scenario": scenario,
                    "Year": selected_year
                })

        violin_df = pd.DataFrame(violin_data)

        fig_violin = px.violin(
            violin_df,
            x="Indicator",
            y="Value",
            color="Risk Type",
            box=True,
            points="all",
            hover_data=["Settlement", "Flood Scenario", "Year"],
            facet_col="Risk Type" if use_facet else None,
            title="Distribution of Raw vs Weighted Risk per Indicator",
            color_discrete_map={
                "Raw %": "orange",
                "Weighted %": "crimson"
            }
        )

        st.plotly_chart(fig_violin, use_container_width=True)

    with col4:
        st.markdown("**📊 Total Exposure vs People/Assets at Risk**")

        # Simulate total population/assets for demo: reverse-calculate
        total_values = [raw * (100 / pct) if pct else raw for raw, pct in zip(raw_values, percentages)]

        fig_exposure = go.Figure()
        fig_exposure.add_trace(go.Bar(x=indicators, y=total_values, name="Total Exposed (Estimate)", marker_color="lightgrey"))
        fig_exposure.add_trace(go.Bar(x=indicators, y=raw_values, name="At Risk", marker_color="firebrick"))

        fig_exposure.update_layout(
            barmode='group',
            title="Comparison of Total Exposed vs People/Assets Actually at Risk",
            yaxis_title="Count or Length (km)",
            legend_title="Exposure Type"
        )

        st.plotly_chart(fig_exposure, use_container_width=True)

    # Composite Risk Index metric
    risk_level = "Low" if risk_index <= 5 else "Moderate" if risk_index <= 10 else "High"
    st.metric("📌 Composite Risk Index", f"{risk_index:.1f}", help=f"Risk Level: {risk_level}")

    # Export CSV
    df["Settlement"] = settlement_name
    df["Flood Scenario"] = scenario
    df["Year"] = selected_year
    df["Risk Index"] = risk_index

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Risk Summary CSV", csv, file_name=f"{settlement_name}_risk_summary.csv", mime="text/csv")


# Explanation of the Risk Index
# with st.expander("ℹ️ How is the Risk Index Calculated?", expanded=False):
#     st.markdown("""
#     The **Composite Risk Index** gives an overall sense of exposure by combining key indicators using weighted contributions:

#     **Formula:**  
#     `Index = ∑ (Exposure % × Weight)` for each indicator

#     **Weights:**  
#     - Population = 30%  
#     - Children = 20%  
#     - Elderly = 20%  
#     - Roads = 15%  
#     - Buildings = 15%  

#     **Example Calculation:**  
#     If `Exposed Population = 20%`, then contribution = `20 × 0.3 = 6.0`  
#     (and so on for each indicator)

#     **Interpretation Scale:**  
#     - 🟢 0–5 → **Low Risk**  
#     - 🟠 5–10 → **Moderate Risk**  
#     - 🔴 >10 → **High Risk**
                
#     """)






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