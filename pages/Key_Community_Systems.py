import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
import ee
import geemap.foliumap as geemap 
from folium.plugins import Draw

st.set_page_config(layout="wide")
st.title("🗺️ Community Systems Mapping Tool")

# Initialize session state to store point data
if "points" not in st.session_state:
    st.session_state.points = []

# Create base map
m = folium.Map(location=[45, 10], zoom_start=4)

# Add drawing controls with predefined icons
draw = Draw(
    draw_options={
        "polyline": False,
        "polygon": False,
        "circle": False,
        "rectangle": False,
        "circlemarker": False,
        "marker": True
    },
    edit_options={"edit": True}
)
draw.add_to(m)

# Display map
output = st_folium(m, height=500, width=1000, returned_objects=["last_clicked", "all_drawings"])

# Category options with emojis for readability
categories = {
    "School 🏫": "school",
    "Hospital 🏥": "hospital",
    "Economic Center 💼": "economic",
    "Other Critical Site ⚠️": "other"
}

# Form to enter metadata if marker was placed
if output["last_clicked"]:
    st.subheader("📍 Enter Details for Selected Point")
    with st.form("point_form"):
        name = st.text_input("Name of Site")
        description = st.text_area("Description")
        category = st.selectbox("Category", list(categories.keys()))
        importance = st.text_input("Socio-Economic Importance")
        image_url = st.text_input("Image URL")
        link = st.text_input("External Link")
        submit = st.form_submit_button("Add Point")

        if submit:
            point_data = {
                "Name": name,
                "Description": description,
                "Category": category,
                "Importance": importance,
                "Image URL": image_url,
                "Link": link,
                "Latitude": output["last_clicked"]["lat"],
                "Longitude": output["last_clicked"]["lng"]
            }
            st.session_state.points.append(point_data)
            st.success(f"Added: {name}")

# Display table of added points
if st.session_state.points:
    st.subheader("🗂️ Community Systems Table")
    df = pd.DataFrame(st.session_state.points)
    st.dataframe(df, use_container_width=True)

    # Export option
    st.download_button(
        label="📥 Download as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="community_systems.csv",
        mime="text/csv"
    )

    st.download_button(
        label="📥 Download as Excel",
        data=df.to_excel(index=False, engine="openpyxl"),
        file_name="community_systems.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Drop a marker on the map and fill the form to begin collecting data.")
