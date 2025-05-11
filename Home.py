import streamlit as st

# This MUST be the first Streamlit command
st.set_page_config(layout="wide")

import leafmap.foliumap as leafmap
import utils_ee

# Now safe to call Streamlit functions
utils_ee.initialize_earth_engine()

st.title("Multi-GIS Support Platform")

st.markdown(
    """
    This platform is developed by Deltares to support regional partners in advancing their work under the **DesirMED** (Tasks 4.1, 4.2, 4.4) and **NBRACER** (Tasks D5.1, D5.3, D5.5) projects. To fully understand the methodologies applied here, users are encouraged to consult the relevant project deliverables. This platform primarily serves to **visualize and demonstrate the operational frameworks** developed within these tasks.

    The platform integrates **on-the-fly web-mapping and decision-support** based on globally recognized datasets.
    *Note: The datasets used here are coarser. For region-specific, higher-resolution customised analyses, please refer to the dedicated WebGIS and QuickScan tool.*

    **Key Applications:**
    - **DesirMED Task 4.1:** Landscape Characterisation  
    - **DesirMED Task 4.2:** Risk Assessment and Vulnerability Analysis  
    - **DesirMED Task 4.4:** Balanced Portfolios and Adaptation Pathways  
    - **NBRACER Task D5.1:** Conceptual Framework for NbS Design and Implementation  
    - **NBRACER Task D5.3:** Tools for Biodiversity and Ecosystem Services Characterisation  
    - **NBRACER Task D5.5:** Tools and Guidelines for Adaptation & Transformation Pathways  

    """
)


st.sidebar.title("Contact")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/desirmed) | [Twitter](https://twitter.com/deltares) | [YouTube](https://youtube.com/@deltares) | [LinkedIn](https://www.linkedin.com/in/deltares)
    """
)






st.info("Click on the left sidebar menu to navigate to the different apps.")

st.subheader("Timelapse of Satellite Imagery")
# st.markdown(
#     """
#     The following timelapse animations were created using the Timelapse web app. Click `Timelapse` on the left sidebar menu to create your own timelapse for any location around the globe.
#     """
# )

row1_col1, row1_col2, row1_col3 = st.columns(2)
with row1_col1:
    st.image("https://github.com/giswqs/data/raw/main/timelapse/spain.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/las_vegas.gif")

with row1_col2:
    st.image("https://github.com/giswqs/data/raw/main/timelapse/goes.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/fire.gif")

with row1_col3:
    st.image("https://github.com/deltares-desirmed/multi-gis-framework/blob/main/img/nbs.png")
    st.image("https://github.com/deltares-desirmed/multi-gis-framework/blob/main/img/nbs.png")


st.markdown(
    """
    **Key Applications:**
    - **DesirMED Task 4.1:** Landscape Characterisation  
    - **DesirMED Task 4.2:** Risk Assessment and Vulnerability Analysis  
    - **DesirMED Task 4.4:** Balanced Portfolios and Adaptation Pathways  
    - **NBRACER Task D5.1:** Conceptual Framework for NbS Design and Implementation  
    - **NBRACER Task D5.3:** Tools for Biodiversity and Ecosystem Services Characterisation  
    - **NBRACER Task D5.5:** Tools and Guidelines for Adaptation & Transformation Pathways  

    """
)


st.markdown(
    """
    This multi-page web app demonstrates various interactive web apps created using [streamlit](https://streamlit.io) and open-source mapping libraries,
    such as [leafmap](https://leafmap.org), [geemap](https://geemap.org), [pydeck](https://deckgl.readthedocs.io), and [kepler.gl](https://docs.kepler.gl/docs/keplergl-jupyter).
    This is an open-source project and you are very welcome to contribute your comments, questions, resources, and apps as [issues](https://github.com/deltares-desirmed/multi-gis-support/issues) or
    [pull requests](https://github.com/giswqs/multi-gis-support/pulls) to the [GitHub repository](https://github.com/deltares-desirmed/multi-gis-support).

    """
)