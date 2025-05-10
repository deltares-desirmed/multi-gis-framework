import streamlit as st

# This MUST be the first Streamlit command
st.set_page_config(layout="wide")

import leafmap.foliumap as leafmap
import utils_ee

# Now safe to call Streamlit functions
utils_ee.initialize_earth_engine()

# st.sidebar.title("About")
st.title("Streamlit for Geospatial Applications")
st.markdown(
    """
    This multi-GIS support platform is developed by Deltares to assist regional partners in advancing their work under the DesirMED (Tasks 4.1, 4.2, and 4.4) and NBRACER (Tasks D5.1, D5.3, and D5.5) projects.To get the ost of out of why analysis is done the way it is done here, you have to consult to deliverables. This webpage on visualise and demonstrate the operational frameworks developed under these tasks.

    The platform provides integrated web-mapping and decision-support based on uniform and globally recognized datasets, aligned with European data standards. It offers practical demonstrations of methodologies for climate resilience assessments, ecosystem services valuation, and Nature-based Solutions (NbS) mainstreaming across marine, coastal, urban, and rural landscapes. Note that most datasets used here are coarser. For a customised version tailored to a more regional specific needs, check this webGIS tool and the quiclscan tool.

    Users can explore solutions to support:
    - Landscape Characterisation and NbS Potential Mapping (DesirMED Task 4.1)
    - Risk Assessment (DesirMED Task 4.2)
    - Balanced Portofios and Pathways (DesirMED Task 4.4)
    - Conceptual framework for the design and implementation of NBS (NBRACER Task D5.1)
    - Tool for characterisation and modelling of biodiversity and ecosystem services (NBRACER Task D5.3)
    - Tool & guide for adaptation & transformation paths for Landscapes (NBRACER Task D5.5)
    
    This platform aims to foster data-driven dialogue, accelerate systemic adaptation, and strengthen regional governance capacities through interactive visualizations and scenario analyses.
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/desirmed) | [Twitter](https://twitter.com/deltares) | [YouTube](https://youtube.com/@deltares) | [LinkedIn](https://www.linkedin.com/in/deltares)
    """
)

# st.sidebar.title("Support")
# st.sidebar.info(
#     """
#     If you want to reward my work, I'd love a cup of coffee from you. Thanks!
#     [buymeacoffee.com/giswqs](http://buymeacoffee.com/giswqs)
#     """
# )



st.markdown(
    """
    This multi-page web app demonstrates various interactive web apps created using [streamlit](https://streamlit.io) and open-source mapping libraries,
    such as [leafmap](https://leafmap.org), [geemap](https://geemap.org), [pydeck](https://deckgl.readthedocs.io), and [kepler.gl](https://docs.kepler.gl/docs/keplergl-jupyter).
    This is an open-source project and you are very welcome to contribute your comments, questions, resources, and apps as [issues](https://github.com/desirmed/multi-gis-support/issues) or
    [pull requests](https://github.com/giswqs/multi-gis-support/pulls) to the [GitHub repository](https://github.com/desirmed/multi-gis-support).

    """
)

st.info("Click on the left sidebar menu to navigate to the different apps.")

st.subheader("Timelapse of Satellite Imagery")
# st.markdown(
#     """
#     The following timelapse animations were created using the Timelapse web app. Click `Timelapse` on the left sidebar menu to create your own timelapse for any location around the globe.
#     """
# )

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.image("https://github.com/giswqs/data/raw/main/timelapse/spain.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/las_vegas.gif")

with row1_col2:
    st.image("https://github.com/giswqs/data/raw/main/timelapse/goes.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/fire.gif")
