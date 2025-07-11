import ee
import json
import streamlit as st
import geemap.foliumap as geemap

st.set_page_config(layout="wide")

st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/deltares-desirmed) | [Twitter](https://twitter.com/deltares) | [YouTube](https://youtube.com/@deltares) | [LinkedIn](https://www.linkedin.com/in/deltares)
    """
)


def nlcd():

    # st.header("National Land Cover Database (NLCD)")

    row1_col1, row1_col2 = st.columns([3, 1])
    width = 950
    height = 600

    Map = geemap.Map(center=[40, -100], zoom=4)

    # Select the seven NLCD epoches after 2000.
    years = ["2001", "2004", "2006", "2008", "2011", "2013", "2016", "2019"]

    # Get an NLCD image by year.
    def getNLCD(year):
        # Import the NLCD collection.
        dataset = ee.ImageCollection("USGS/NLCD_RELEASES/2019_REL/NLCD")

        # Filter the collection by year.
        nlcd = dataset.filter(ee.Filter.eq("system:index", year)).first()

        # Select the land cover band.
        landcover = nlcd.select("landcover")
        return landcover

    with row1_col2:
        selected_year = st.multiselect("Select a year", years)
        add_legend = st.checkbox("Show legend")

    if selected_year:
        for year in selected_year:
            Map.addLayer(getNLCD(year), {}, "NLCD " + year)

        if add_legend:
            Map.add_legend(
                legend_title="NLCD Land Cover Classification", builtin_legend="NLCD"
            )
        with row1_col1:
            Map.to_streamlit(width=width, height=height)

    else:
        with row1_col1:
            Map.to_streamlit(width=width, height=height)


def search_data():

    # st.header("Search Earth Engine Data Catalog")

    Map = geemap.Map()

    if "ee_assets" not in st.session_state:
        st.session_state["ee_assets"] = None
    if "asset_titles" not in st.session_state:
        st.session_state["asset_titles"] = None

    col1, col2 = st.columns([2, 1])

    dataset = None
    with col2:
        keyword = st.text_input("Enter a keyword to search (e.g., elevation)", "")
        if keyword:
            ee_assets = geemap.search_ee_data(keyword)
            asset_titles = [x["title"] for x in ee_assets]
            asset_types = [x["type"] for x in ee_assets]

            translate = {
                "image_collection": "ee.ImageCollection('",
                "image": "ee.Image('",
                "table": "ee.FeatureCollection('",
                "table_collection": "ee.FeatureCollection('",
            }

            dataset = st.selectbox("Select a dataset", asset_titles)
            if len(ee_assets) > 0:
                st.session_state["ee_assets"] = ee_assets
                st.session_state["asset_titles"] = asset_titles

            if dataset is not None:
                with st.expander("Show dataset details", True):
                    index = asset_titles.index(dataset)

                    html = geemap.ee_data_html(st.session_state["ee_assets"][index])
                    html = html.replace("\n", "")
                    st.markdown(html, True)

                ee_id = ee_assets[index]["id"]
                uid = ee_assets[index]["uid"]
                st.markdown(f"""**Earth Engine Snippet:** `{ee_id}`""")
                ee_asset = f"{translate[asset_types[index]]}{ee_id}')"

                if ee_asset.startswith("ee.ImageCollection"):
                    ee_asset = ee.ImageCollection(ee_id)
                elif ee_asset.startswith("ee.Image"):
                    ee_asset = ee.Image(ee_id)
                elif ee_asset.startswith("ee.FeatureCollection"):
                    ee_asset = ee.FeatureCollection(ee_id)

                vis_params = st.text_input(
                    "Enter visualization parameters as a dictionary", {}
                )
                layer_name = st.text_input("Enter a layer name", uid)
                button = st.button("Add dataset to map")
                if button:
                    vis = {}
                    try:
                        if vis_params.strip() == "":
                            # st.error("Please enter visualization parameters")
                            vis_params = "{}"
                        vis = json.loads(vis_params.replace("'", '"'))
                        if not isinstance(vis, dict):
                            st.error("Visualization parameters must be a dictionary")
                        try:
                            Map.addLayer(ee_asset, vis, layer_name)
                        except Exception as e:
                            st.error(f"Error adding layer: {e}")
                    except Exception as e:
                        st.error(f"Invalid visualization parameters: {e}")

            with col1:
                Map.to_streamlit()
        else:
            with col1:
                Map.to_streamlit()


def app():
    st.title("Earth Engine Data Catalog")

    apps = ["Search Earth Engine Data Catalog", "National Land Cover Database (NLCD)"]

    selected_app = st.selectbox("Select an app", apps)

    if selected_app == "National Land Cover Database (NLCD)":
        nlcd()
    elif selected_app == "Search Earth Engine Data Catalog":
        search_data()


app()

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