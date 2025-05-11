import streamlit as st
import leafmap.foliumap as leafmap
import leafmap.maplibregl as maplibre
import os

# Set MapTiler API Key for 3D terrain
os.environ["MAPTILER_KEY"] = "iiyRi7eIx4NmHrMOEZsc"

st.set_page_config(layout="wide")

st.sidebar.title("Info")
st.sidebar.info(
    """
    Deltares at [NbS Knowledge Hub](https://nbs-tutorials-and-tips) | [GitHub](https://github.com/deltares-desirmed) | [Twitter](https://twitter.com/deltares) | [YouTube](https://youtube.com/@deltares) | [LinkedIn](https://www.linkedin.com/in/deltares)
    """
)

st.title("Split-panel Map with 3D Visualization")

# Split layout into two columns for side-by-side maps
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Split Panel Map")
    with st.expander("See source code for 2D map"):
        with st.echo():
            m = leafmap.Map()
            m.split_map(
                left_layer="ESA WorldCover 2020 S2 FCC", right_layer="ESA WorldCover 2020"
            )
            m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
    m.to_streamlit(height=600)

with col2:
    st.subheader("3D Globe Visualization")

    with st.expander("See source code for 3D map"):
        with st.echo():
            m3d = maplibre.Map(style="3d-terrain", projection="globe")
            m3d.add_basemap("Esri.WorldImagery")
            m3d.add_overture_3d_buildings()
            m3d.add_layer_control()

    m3d.to_streamlit(height=600)
