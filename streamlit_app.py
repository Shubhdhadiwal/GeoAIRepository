import streamlit as st
import pandas as pd

# ----- Page Configuration ----- #
st.set_page_config(page_title="GeoAI Repository", layout="wide")

# ----- Load Excel Data ----- #
@st.cache_data
def load_data(sheet_name):
    df = pd.read_excel("Geospatial Data Repository (1).xlsx", sheet_name=sheet_name)
    df.columns = df.iloc[0]  # First row as header
    df = df[1:]  # Remove first row from data
    df = df.dropna(how="all")  # Drop fully empty rows
    df = df.dropna(subset=[df.columns[0]])  # Ensure first col not empty
    df.columns = [str(c).strip() for c in df.columns]  # Keep all, just strip spaces
    df.reset_index(drop=True, inplace=True)
    return df

# ----- Sidebar Navigation ----- #
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

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Developed by Shubh**  
📧 [dhadiwalshubh348@gmail.com](mailto:dhadiwalshubh348@gmail.com)  
© 2025 GeoAI Repository
""")

# ----- About Section ----- #
if selected_tab == "About":
    st.title("📘 About GeoAI Repository")
    st.markdown("""
    The **GeoAI Repository** is a free and open resource hub for students, researchers, and professionals 
    working in geospatial analytics, machine learning, and urban/climate planning.
    """)
    st.stop()

# ----- Submit Form ----- #
if selected_tab == "Submit New Resource":
    st.title("📤 Submit a New Resource")
    with st.form("submit_form"):
        title = st.text_input("📌 Title")
        description = st.text_area("📝 Description")
        link = st.text_input("🔗 Link")
        category = st.selectbox("📁 Category", list(sheet_options.keys())[1:-1])
        purpose = st.text_input("🎯 Purpose or Use Case")
        if st.form_submit_button("Submit"):
            if title and description and link:
                st.success("✅ Thank you! Your resource has been submitted for review.")
            else:
                st.error("⚠️ Please fill out all required fields.")
    st.stop()

# ----- Field Configuration Per Sheet ----- #
FIELD_CONFIG = {
    "Data Sources": ["Name of Source", "Link", "Description", "Year/Month", "Countries Covered", "Type", "Spatial Resolution", "Version", "Purpose"],
    "Tools": ["Tool Name", "Description", "Link", "Datasets Availability", "Type", "Applicability", "Purpose", "Availability"],
    "Free Tutorials": ["Tutorial Name", "Description", "Purpose", "Link"],
    "Python Codes (GEE)": ["Title", "Purpose", "Link"],
    "Courses": ["Course Name", "Description", "Purpose", "Version", "Link"]
}

# ----- Map sheet names to title columns ----- #
TITLE_MAP = {
    "Data Sources": "Name of Source",
    "Tools": "Tool Name",
    "Courses": "Course Name",
    "Python Codes (GEE)": "Title",
    "Free Tutorials": "Tutorial Name"
}

# ----- Load Data ----- #
df = load_data(sheet_options[selected_tab])

# ----- Search ----- #
search_term = st.sidebar.text_input("🔍 Search")
if search_term:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]

# ----- Filters for Data Sources ----- #
if selected_tab == "Data Sources" and "Type" in df.columns:
    type_filter = st.sidebar.multiselect("📂 Filter by Type", df["Type"].dropna().unique())
    if type_filter:
        df = df[df["Type"].isin(type_filter)]

# ----- Display Section Title ----- #
st.title(f"🌍 GeoAI Repository – {selected_tab}")

# ----- Determine title column for this tab ----- #
title_field = TITLE_MAP.get(selected_tab, df.columns[0])
fields_to_display = FIELD_CONFIG.get(selected_tab, [title_field])

# ----- Render Cards ----- #
for _, row in df.iterrows():
    resource_title = str(row.get(title_field, "")).strip() if pd.notna(row.get(title_field)) else "Unnamed Resource"
    st.subheader(f"🔹 {resource_title}")

    for field in fields_to_display[1:]:  # Skip title
        if field in df.columns and pd.notna(row.get(field)) and str(row.get(field)).strip():
            value = row[field]
            if "link" in field.lower():
                st.markdown(f"[🔗 {field}]({value})", unsafe_allow_html=True)
            else:
                st.markdown(f"**{field}:** {value}")

    st.markdown("---")

# ----- Footer ----- #
st.markdown("<hr style='border:1px solid #ddd'/>", unsafe_allow_html=True)
st.markdown("""
**Developed by Shubh**  
📧 [dhadiwalshubh348@gmail.com](mailto:dhadiwalshubh348@gmail.com)  
📘 Powered by [Streamlit](https://streamlit.io) | © 2025 GeoAI Repository
""")
