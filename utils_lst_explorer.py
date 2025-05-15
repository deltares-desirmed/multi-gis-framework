import streamlit as st
import json
import geojson
import ee
import pandas as pd
import geopandas as gpd
import altair as alt
from streamlit_folium import folium_static 
import folium
from shapely.geometry import shape

def show_lst_explorer():
    MAP_EMOJI_URL = "https://em-content.zobj.net/source/apple/354/thermometer_1f321-fe0f.png"

    col1, col2, col3 = st.columns([1, 4, 1])
    col2.image(MAP_EMOJI_URL, width=80)
    col2.markdown("""
        # Land Surface Temperature - River Basins
        The app enables discovering land surface temperature data over river (hydrological) basins. 

        Temporal extent: 2017-01-01 till today.
        Library for visualizations - Vega-Altair.
        ---
        """)

    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    def convert_gdf(gdf):
        gdf['geometry'] = gdf['geometry'].astype('geometry') 
        gdf['Timestamp'] = gdf['Timestamp'].astype(str)
        return gdf.to_json()

    json_data = st.secrets["json_data"]
    service_account = st.secrets["service_account"]

    json_object = json.loads(json_data, strict=False)
    json_object = json.dumps(json_object)
    credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
    ee.Initialize(credentials)

    import src.gee as gee

    today = ee.Date(pd.to_datetime('today'))
    date_range = ee.DateRange('2017-01-01', today)

    region_name = col2.selectbox('Select the region.', ['Europe','USA', 'Australia and New Zealand', 'Near East', 'Southeast Asia'], key='region_name')

    if region_name:
        filename = "data/basins_" + region_name.lower() + "_mult.geojson"
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

                        st.subheader("Line Chart of LST")
                        st.altair_chart(alt.Chart(lst_df).mark_line(point=alt.OverlayMarkDef(color="red")).encode(
                            alt.X("Timestamp"),
                            alt.Y("LST_Day_1km", title='Land Surface Temperature, °C'),
                        ).interactive(), use_container_width=True)

                        with st.expander('Geometry Preview', expanded=False):
                            map_aoi = folium.Map(tiles="OpenStreetMap")
                            folium.Choropleth(geo_data = aoi_json, reset=True).add_to(map_aoi)
                            st.warning("Note: Map zoom may not auto-center due to Streamlit-Folium rendering issue.")
                            folium_static(map_aoi)

                        st.subheader("Download Data")
                        gdf = gpd.GeoDataFrame(lst_df, geometry=[shape(aoi_json)]*len(lst_df))
                        csv_data = convert_df(gdf)
                        geojson_data = convert_gdf(gdf)

                        st.download_button("Download CSV", data=csv_data, file_name=sub_name + "-LST.csv", mime="text/csv")
                        st.download_button("Download GeoJSON", data=geojson_data, file_name=sub_name + "-LST.geojson", mime="application/json")
