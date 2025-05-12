import streamlit as st
import leafmap.foliumap as leafmap
import leafmap.maplibregl as maplibre
import ee
import os


st.set_page_config(layout="wide")




st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/deltares-desirmed) | [Twitter](https://twitter.com/deltares) | [YouTube](https://youtube.com/@deltares) | [LinkedIn](https://www.linkedin.com/in/deltares)
    """
)

st.title("Funxtional Units")

with st.expander("See source code"):
    with st.echo():
        m = leafmap.Map()
        m.split_map(
            left_layer="COPERNICUS/CORINE/V20/100m/2018",
            right_layer="COPERNICUS/CORINE/V20/100m/2018"
        )
        m.add_legend(
            title="CORINE Land Cover 2018",
            labels=[
                "Artificial Surfaces", "Agricultural Areas", "Forest", 
                "Wetlands", "Water Bodies"
            ],
            colors=["#FF0000", "#FFFF00", "#008000", "#00FFFF", "#0000FF"]
        )


m.to_streamlit(height=700)