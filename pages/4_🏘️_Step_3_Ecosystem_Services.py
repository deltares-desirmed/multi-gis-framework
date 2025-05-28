import ee
import geemap.foliumap as geemap
import geopandas as gpd
import streamlit as st

st.set_page_config(layout="wide")


def ee_authenticate(token_name="EARTHENGINE_TOKEN"):
    geemap.ee_initialize(token_name=token_name)


st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/deltares-desirmed) | [Twitter](https://twitter.com/deltares) | [YouTube](https://youtube.com/@deltares) | [LinkedIn](https://www.linkedin.com/in/deltares)
    """
)

st.title("Biodiversity and Ecosystem Services")

col1, col2 = st.columns([8, 2])


@st.cache_data
def read_data(url):
    return gpd.read_file(url)


countries = (
    "https://github.com/giswqs/geemap/raw/master/examples/data/countries.geojson"
)
states = "https://github.com/giswqs/geemap/raw/master/examples/data/us_states.json"

countries_gdf = read_data(countries)
states_gdf = read_data(states)

country_names = countries_gdf["NAME"].values.tolist()
country_names.remove("United States of America")
country_names.append("USA")
country_names.sort()
country_names = [name.replace(".", "").replace(" ", "_") for name in country_names]

state_names = states_gdf["name"].values.tolist()

basemaps = list(geemap.basemaps)

Map = geemap.Map()

with col2:

    basemap = st.selectbox("Select a basemap", basemaps, index=basemaps.index("HYBRID"))
    Map.add_basemap(basemap)

    country = st.selectbox(
        "Select a country", country_names, index=country_names.index("Croatia")
    )

    if country == "USA":
        state = st.selectbox(
            "Select a state", state_names, index=state_names.index("Florida")
        )
        layer_name = state

        try:
            fc = ee.FeatureCollection(
                f"projects/sat-io/open-datasets/MSBuildings/US/{state}"
            )
        except:
            st.error("No data available for the selected state.")

    else:
        try:
            fc = ee.FeatureCollection(
                f"projects/sat-io/open-datasets/MSBuildings/{country}"
            )
        except:
            st.error("No data available for the selected country.")

        layer_name = country

    color = st.color_picker("Select a color", "#FF5500")

    style = {"fillColor": "00000000", "color": color}

    split = st.checkbox("Split-panel map")

    if split:
        left = geemap.ee_tile_layer(fc.style(**style), {}, "Left")
        right = left
        Map.split_map(left, right)
    else:
        Map.addLayer(fc.style(**style), {}, layer_name)

    Map.centerObject(fc.first(), zoom=16)

    with st.expander("Data Sources"):
        st.info(
            """
            [Microsoft Building Footprints](https://gee-community-catalog.org/projects/msbuildings/)
            """
        )


with col1:

    Map.to_streamlit(height=1000)



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