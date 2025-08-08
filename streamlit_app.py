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
    """)
    st.info("""
    - 🌐 Public geospatial datasets  
    - 🛠️ Open-source tools  
    - 📘 Free tutorials  
    - 💻 Python codes for Google Earth Engine  
    """)
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

# ===== INTERACTIVE SEARCH & FILTER ===== #
search_term = st.sidebar.text_input("🔍 Search")
if search_term:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]

if selected_tab == "Data Sources" and "Type" in df.columns:
    type_filter = st.sidebar.multiselect("📂 Filter by Type", sorted(df["Type"].dropna().unique()))
    if type_filter:
        df = df[df["Type"].isin(type_filter)]

# ===== TITLE MAPPING ===== #
title_map = {
    "Data Sources": "Data Source",
    "Tools": "Tool Name",
    "Courses": "Tutorial Name",
    "Python Codes (GEE)": "Title",
    "Free Tutorials": "Tutorials"
}
title_col = title_map.get(selected_tab, df.columns[0])

# ===== MAIN TITLE ===== #
st.title(f"🌍 GeoAI Repository – {selected_tab}")

# ===== VIEW MODE SWITCH ===== #
view_mode = st.radio("Choose view mode:", ["📄 Table View", "📇 Card View"], horizontal=True)

if view_mode == "📄 Table View":
    st.dataframe(df, use_container_width=True)

elif view_mode == "📇 Card View":
    for _, row in df.iterrows():
        with st.expander(f"🔹 {row.get(title_col, 'Unnamed Resource')}"):
            if "Description" in df.columns and pd.notna(row.get("Description")):
                st.write(row["Description"])

            link_col = next((c for c in ["Links", "Link", "Link to the codes"] if c in df.columns), None)
            if link_col and pd.notna(row.get(link_col)):
                st.markdown(f"[🔗 Access Resource]({row[link_col]})", unsafe_allow_html=True)

            if "Purpose" in df.columns and pd.notna(row.get("Purpose")):
                st.markdown(f"**🎯 Purpose:** {row['Purpose']}")

            for col in df.columns:
                if col not in [title_col, "Description", link_col, "Purpose"] and pd.notna(row.get(col)):
                    st.markdown(f"**{col}:** {row[col]}")

# ===== FOOTER ===== #
st.markdown("<hr style='border:1px solid #ddd'/>", unsafe_allow_html=True)
st.caption("📘 Powered by Streamlit | © 2025 GeoAI Repository")
