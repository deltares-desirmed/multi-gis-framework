import streamlit as st
import geopandas as gpd
import pandas as pd
import json
import folium
import altair as alt
from shapely.geometry import shape
from streamlit_folium import folium_static
import ee
from utils_ee import initialize_earth_engine
import src.gee as gee

# Moved chart rendering inline instead of importing

def show_lst_explorer():
    initialize_earth_engine()

    MAP_EMOJI_URL = "https://pbs.twimg.com/profile_images/1206882243278462976/rr11Zc6-_400x400.jpg"

    col1, col2, col3 = st.columns([1, 4, 1])
    col2.markdown("<br>", unsafe_allow_html=True)
    col2.image(MAP_EMOJI_URL, width=80)
    col2.markdown("""
        # Land Surface Temperature - River Basins
        [![Follow](https://img.shields.io/twitter/follow/deltares?style=social)](https://x.com/deltares)
        [![Follow](https://img.shields.io/badge/LinkedIn-blue?style=flat&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/deltares/)

        ## Details

        The app enables discovering land surface temperature data over river (hydrological) basins. 

        Temporal extent: 2017-01-01 till today.
        Library for visualizations - [Vega-Altair](https://altair-viz.github.io/index.html).

        ---
    """)

    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    def convert_gdf(gdf):
        gdf['geometry'] = gdf['geometry'].astype('geometry') 
        gdf['Timestamp'] = gdf['Timestamp'].astype(str)
        return gdf.to_json()

    today = ee.Date(pd.to_datetime('today'))
    date_range = ee.DateRange('2017-01-01', today)

    region_name = col2.selectbox('Select the region.', ['Europe','USA', 'Australia and New Zealand', 'Near East', 'Southeast Asia'], key='region_name')
    if region_name:
        filename = "database/basins_" + region_name.lower() + "_mult.geojson"
        file = open(filename)
        gdf = gpd.read_file(file)
        maj_name = col2.selectbox('Select the major hydrological basin.', sorted(pd.unique(gdf['MAJ_NAME'])), key='maj_name')
        if maj_name:
            sub_name = col2.selectbox('Select the river basin within the major one', sorted(gdf[gdf['MAJ_NAME'] == maj_name]['SUB_NAME']), key='sub_name')
            if col2.button('Discover the Land Surface Temperature data!'):
                with col2:
                    with st.spinner("Collecting data using Google Earth Engine..."):
                        aoi_json = json.loads(gdf.loc[gdf['SUB_NAME'] == sub_name, 'geometry'].to_json())['features'][0]['geometry']
                        aoi = ee.FeatureCollection(ee.Geometry(aoi_json)).geometry()
                        lst = ee.ImageCollection('MODIS/061/MOD11A2').filterDate(date_range).select('LST_Day_1km')
                        reduce_lst = gee.create_reduce_region_function(geometry=aoi, reducer=ee.Reducer.mean(), scale=1000, crs='EPSG:4326')
                        lst_stat_fc = ee.FeatureCollection(lst.map(reduce_lst)).filter(ee.Filter.notNull(lst.first().bandNames()))
                        lst_dict = gee.fc_to_dict(lst_stat_fc).getInfo()
                        lst_df = pd.DataFrame(lst_dict)
                        lst_df['LST_Day_1km'] = (lst_df['LST_Day_1km'] * 0.02 - 273.5)
                        lst_df = gee.add_date_info(lst_df)

                        with st.expander('Geometry Preview', expanded=False):
                            map_aoi = folium.Map(tiles="OpenStreetMap")
                            folium.Choropleth(geo_data=aoi_json, reset=True).add_to(map_aoi)
                            bounds = map_aoi.get_bounds()
                            map_aoi.fit_bounds(bounds)
                            st.warning("Sometimes the map does not zoom to the selected area most likely because of [this issue](https://github.com/randyzwitch/streamlit-folium/issues/152).")
                            folium_static(map_aoi)

                # Charts
                col2.markdown("### 📊 Land Surface Temperature Time Series")
                line_chart = alt.Chart(lst_df).mark_line(
                    point=alt.OverlayMarkDef(color="red")
                ).encode(
                    alt.X("Timestamp"),
                    alt.Y("LST_Day_1km", title='Land Surface Temperature, °C'),
                ).interactive()
                col2.altair_chart(line_chart, use_container_width=True)

                # Data download
                col1, col2, col3 = st.columns([1, 4, 1]) 
                col2.markdown("""
                    ---
                    ## Data download
                    """)
                gdf_out = gpd.GeoDataFrame(lst_df, geometry=[shape(aoi_json)]*len(lst_df))
                csv_data = convert_df(gdf_out)
                geojson_data = convert_gdf(gdf_out)
                with col2.container(border=True):
                    cont1_1, cont1_2 = st.columns([1, 3])
                    with cont1_1:
                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name=sub_name + "-LST.csv",
                            mime="text/csv",
                            key='download-csv'
                        )
                    with cont1_2:
                        st.write("The CSV includes temperature data, dates, and geometry.")

                with col2.container(border=True):
                    cont2_1, cont2_2 = st.columns([1, 3])
                    with cont2_1:
                        st.download_button(
                            label="Download GeoJSON",
                            data=geojson_data,
                            file_name=sub_name + "-LST.geojson",
                            mime="application/json",
                            key='download-geojson'
                        )
                    with cont2_2:
                        st.write("The GeoJSON includes average LST per timestep.")

col1, col2, col3 = st.columns([1, 4, 1])
col2.markdown("""
    ---
    ## References
    * Hydrological basins in Europe - [FAO Map Catalog.](https://data.apps.fao.org/map/catalog/srv/api/records/1849e279-67bd-4e6f-a789-9918925a11a1)
    * Watershed Boundary Dataset in the USA - [USGS.](https://www.usgs.gov/national-hydrography/watershed-boundary-dataset)
    * Hydrological basins in Australia and New Zealand - [FAO Map Catalog.](https://data.apps.fao.org/catalog/dataset/a1a0e9ee-5062-4950-a6b9-fdd2284b2607)
    * Hydrological basins in Near East - [FAO Map Catalog.](https://data.apps.fao.org/catalog/iso/7ae00a40-642b-4637-b1d3-ffacb13360db)
    * Hydrological basins in Southeast Asia - [FAO Map Catalog.](https://data.apps.fao.org/catalog/iso/ee616dc4-3118-4d67-ba05-6e93dd3e962f)
    * Land Surface Temperature - [MODIS via Google Earth Engine.](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A2)
    """)