import streamlit as st
import pandas as pd

# ===== PAGE CONFIG ===== #
st.set_page_config(page_title="GeoAI Repository", layout="wide")

# ===== LOAD DATA ===== #
@st.cache_data
def load_data(sheet_name):
    df = pd.read_excel("Geospatial Data Repository (1).xlsx", sheet_name=sheet_name)
    df.columns = df.iloc[0]  # Use first row as header
    df = df[1:]  # Skip header row from data
    df = df.dropna(subset=[df.columns[0]])  # Ensure first column is not empty
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Drop unnamed columns
    return df

# ===== SIDEBAR NAV ===== #
st.sidebar.header("🧭 GeoAI Repository")

sheet_options = {
    "About": "About",
    "Data Sources": "Data Sources",
    "Tools": "Tools",
    "Free Tutorials": "Free Tutorials",
    "Python Codes (GEE)": "Google Earth EnginePython Codes",
    "Courses": "Courses",
    "Submit New Resource": "Submit New Resource"
}
selected_tab = st.sidebar.radio("Select Section", list(sheet_options.keys()))

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    © 2025 GeoAI Repository  
    📧 [dhadiwalshubh348@gmail.com](mailto:dhadiwalshubh348@gmail.com)
    """
)

# ===== ABOUT ===== #
if selected_tab == "About":
    st.title("📘 About GeoAI Repository")
    st.markdown("""
    The **GeoAI Repository** is a free and open resource hub for students, researchers, and professionals 
    working in geospatial analytics, machine learning, and urban/climate planning.

    This repository curates:
    - 🌐 **Public geospatial datasets**
    - 🛠️ **Open-source tools and platforms**
    - 📘 **Free learning tutorials**
    - 💻 **Python codes (especially for Google Earth Engine)**

    Our goal is to foster inclusive learning, open innovation, and rapid knowledge sharing in the geospatial-AI community.
    """)

    st.subheader("💡 Vision")
    st.markdown("""
    - Democratize access to GeoAI tools and knowledge  
    - Promote open science and reproducibility  
    - Connect learners with meaningful resources
    """)

    st.subheader("📬 Contact / Feedback")
    st.markdown("📧 Reach out at: [dhadiwalshubh348@gmail.com](mailto:dhadiwalshubh348@gmail.com)")
    st.stop()

# ===== SUBMIT RESOURCE ===== #
if selected_tab == "Submit New Resource":
    st.title("📤 Submit a New Resource")
    st.markdown("Help us grow this repository by contributing useful links and resources.")

    with st.form("submit_form"):
        title = st.text_input("📌 Title")
        description = st.text_area("📝 Description")
        link = st.text_input("🔗 Link")
        category = st.selectbox("📁 Category", list(sheet_options.keys())[1:-1])
        resource_type = st.text_input("📂 Type (e.g. Satellite, Tool, Course)")
        purpose = st.text_input("🎯 Purpose or Use Case")

        submitted = st.form_submit_button("Submit")

        if submitted:
            if title and description and link:
                st.success("✅ Thank you! Your resource has been submitted for review.")
            else:
                st.error("⚠️ Please fill out all required fields.")
    st.stop()

# ===== LOAD DATA ===== #
df = load_data(sheet_options[selected_tab])

# ===== SEARCH ===== #
search_term = st.sidebar.text_input("🔍 Search")
if search_term:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]

# ===== FILTERS ===== #
if selected_tab == "Data Sources" and "Type" in df.columns:
    type_filter = st.sidebar.multiselect("📂 Filter by Type", sorted(df["Type"].dropna().unique()))
    if type_filter:
        df = df[df["Type"].isin(type_filter)]

# ===== TITLE COLUMN MAP ===== #
title_map = {
    "Data Sources": "Data Source",
    "Tools": "Tool Name",
    "Courses": "Course Name",
    "Python Codes (GEE)": "Python Code Name",
    "Free Tutorials": "Tutorial Name"
}
title_col = title_map.get(selected_tab, df.columns[0])

# ===== MAIN TITLE ===== #
st.title(f"🌍 GeoAI Repository – {selected_tab}")

# ===== SHOW DATAFRAME ===== #
st.dataframe(df, use_container_width=True)

# ===== CARD VIEW ===== #
for _, row in df.iterrows():
    resource_title = str(row.get(title_col, "Unnamed Resource")).strip()
    st.subheader(f"🔹 {resource_title}")

    # Description
    if "Description" in df.columns and pd.notna(row.get("Description")):
        st.write(row["Description"])

    # Links
    link_col = next((c for c in ["Links", "Link", "Link to the codes"] if c in df.columns), None)
    if link_col and pd.notna(row.get(link_col)):
        st.markdown(f"[🔗 Access Resource]({row[link_col]})", unsafe_allow_html=True)

    # Purpose
    if "Purpose" in df.columns and pd.notna(row.get("Purpose")):
        st.markdown(f"**🎯 Purpose:** {row['Purpose']}")

    # Show all other non-empty relevant fields
    for col in df.columns:
        if col not in [title_col, "Description", link_col, "Purpose"] and pd.notna(row.get(col)):
            st.markdown(f"**{col}:** {row[col]}")

    st.markdown("---")

# ===== FOOTER ===== #
st.markdown("<hr style='border:1px solid #ddd'/>", unsafe_allow_html=True)
st.markdown(
    """
    📘 Powered by [Streamlit](https://streamlit.io) | © 2025 GeoAI Repository  
    📧 [dhadiwalshubh348@gmail.com](mailto:dhadiwalshubh348@gmail.com)
    """
)
