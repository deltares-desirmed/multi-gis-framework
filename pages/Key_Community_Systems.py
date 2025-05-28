import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw, Geocoder
import io

st.set_page_config(layout="wide")
st.title(" Community Systems Mapping Tool")

# Initialize session state
if "points" not in st.session_state:
    st.session_state.points = []

# ✅ Only create the map ONCE here
m = folium.Map(location=[45, 10], zoom_start=4)

# Add tools
Draw(
    draw_options={
        "polyline": False,
        "polygon": False,
        "circle": False,
        "rectangle": False,
        "circlemarker": False,
        "marker": True
    },
    edit_options={"edit": True}
).add_to(m)

Geocoder(collapsed=False, add_marker=True).add_to(m)

st.markdown("""
    <style>
    .folium-map {
        height: 600px !important;
        margin-bottom: 0px !important;
    }
    iframe {
        height: 600px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Display the map
output = st_folium(m, height=600, width="100%", returned_objects=["last_clicked", "all_drawings"])



# Category options
categories = {
    "School 🏫": "school",
    "Hospital 🏥": "hospital",
    "Economic Center 💼": "economic",
    "Other Critical Site ⚠️": "other"
}

# Metadata entry form
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

# Display and download table
if st.session_state.points:
    st.subheader("🗂️ Community Systems Table")
    df = pd.DataFrame(st.session_state.points)
    st.dataframe(df, use_container_width=True)

    # Download as CSV
    st.download_button(
        label="📥 Download as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="community_systems.csv",
        mime="text/csv"
    )

    # Download as Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    st.download_button(
        label="📥 Download as Excel",
        data=excel_buffer.getvalue(),
        file_name="community_systems.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Drop a marker on the map and fill the form to begin collecting data.")
