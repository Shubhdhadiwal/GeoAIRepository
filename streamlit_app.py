import streamlit as st
import pandas as pd

# ----- Page Configuration ----- #
st.set_page_config(page_title="GeoAI Repository", layout="wide")

# ----- Load Excel Data ----- #
@st.cache_data
def load_data(sheet_name):
    df = pd.read_excel("Geospatial Data Repository (1).xlsx", sheet_name=sheet_name)
    df.columns = df.iloc[0]  # Set first row as header
    df = df[1:]  # Skip header row
    df = df.dropna(subset=[df.columns[0]])  # Drop rows with empty first column
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

# ----- Sidebar Footer ----- #
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    © 2025 GeoAI Repository  
    📧 [dhadiwalshubh348@gmail.com](mailto:dhadiwalshubh348@gmail.com)
    """
)

# ========================= #
#       ABOUT SECTION       #
# ========================= #
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

# ========================= #
#   SUBMIT NEW RESOURCE     #
# ========================= #
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

# ========================= #
#     LOAD DATA SECTION     #
# ========================= #
df = load_data(sheet_options[selected_tab])

# ----- Search ----- #
search_term = st.sidebar.text_input("🔍 Search")
if search_term:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]

# ----- Filter for "Data Sources" Type ----- #
if selected_tab == "Data Sources" and "Type" in df.columns:
    type_filter = st.sidebar.multiselect("📂 Filter by Type", df["Type"].dropna().unique())
    if type_filter:
        df = df[df["Type"].isin(type_filter)]

# ========================= #
#     MAIN CONTENT VIEW     #
# ========================= #
st.title(f"🌍 GeoAI Repository – {selected_tab}")

# Show table in a scrollable container (fixed deprecated parameter)
st.dataframe(df, use_container_width=True)

# ----- Detailed View ----- #
for _, row in df.iterrows():
    title = row.get("Data Source") or row.get("Tools") or row.get("Title") or row.get("Tutorials") or "Unnamed Resource"
    st.subheader(f"🔹 {title}")

    if "Description" in row and pd.notna(row["Description"]):
        st.write(row["Description"])

    link = row.get("Links") or row.get("Link") or row.get("Link to the codes")
    if pd.notna(link):
        st.markdown(f"[🔗 Access Resource]({link})", unsafe_allow_html=True)

    if selected_tab == "Data Sources":
        if pd.notna(row.get("Type")):
            st.markdown(f"**📂 Type:** {row['Type']}")
        if pd.notna(row.get("Spatial Resolution")):
            st.markdown(f"**📏 Spatial Resolution:** {row['Spatial Resolution']}")
        if pd.notna(row.get("Version")):
            st.markdown(f"**🧾 Version:** {row['Version']}")
        if pd.notna(row.get("Year/Month of Data Availability")):
            st.markdown(f"**📅 Year/Month:** {row['Year/Month of Data Availability']}")

    elif selected_tab == "Tools":
        if pd.notna(row.get("Applicability")):
            st.markdown(f"**🛠️ Applicability:** {row['Applicability']}")
        if pd.notna(row.get("Type")):
            st.markdown(f"**📂 Type:** {row['Type']}")
        if pd.notna(row.get("Datasets Availability")):
            st.markdown(f"**📊 Datasets Availability:** {row['Datasets Availability']}")

    if pd.notna(row.get("Purpose")):
        st.markdown(f"**🎯 Purpose:** {row['Purpose']}")

    st.markdown("---")

# ========================= #
#           FOOTER          #
# ========================= #
st.markdown("<hr style='border:1px solid #ddd'/>", unsafe_allow_html=True)
st.markdown(
    """
    📘 Powered by [Streamlit](https://streamlit.io) | © 2025 GeoAI Repository  
    📧 [dhadiwalshubh348@gmail.com](mailto:dhadiwalshubh348@gmail.com)
    """
)
