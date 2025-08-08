import streamlit as st
import pandas as pd

# ----- Page Configuration ----- #
st.set_page_config(page_title="GeoAI Repository", layout="wide")

# ----- Load Excel Data ----- #
@st.cache_data
def load_data(sheet_name):
    """Load data from a specific Excel sheet."""
    df = pd.read_excel("Geospatial Data Repository (1).xlsx", sheet_name=sheet_name)
    df.columns = df.iloc[0]  # First row as header
    df = df[1:]  # Remove header row from data
    df = df.dropna(how="all")  # Drop fully empty rows
    df = df.dropna(subset=[df.columns[0]])  # Drop rows where first column is empty
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

# ----- Sidebar Footer ----- #
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Developed by Shubh**  
    📧 [dhadiwalshubh348@gmail.com](mailto:dhadiwalshubh348@gmail.com)  
    © 2025 GeoAI Repository
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
    st.markdown("📧 [dhadiwalshubh348@gmail.com](mailto:dhadiwalshubh348@gmail.com)")
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

# ----- Filter for "Type" column ----- #
if "Type" in df.columns:
    type_filter = st.sidebar.multiselect("📂 Filter by Type", df["Type"].dropna().unique())
    if type_filter:
        df = df[df["Type"].isin(type_filter)]

# ========================= #
#  CARD LAYOUT FOR SECTIONS #
# ========================= #
resource_tabs = ["Data Sources", "Tools", "Courses", "Python Codes (GEE)", "Free Tutorials"]

if selected_tab in resource_tabs:
    st.title(f"📚 Explore Geospatial {selected_tab}")

    # Possible title column names for different sheets
    possible_title_cols = [
        "Data Source", "Tool Name", "Course Name",
        "Python Code Name", "Tutorial Name", "Name", "Title"
    ]

    for _, row in df.iterrows():
        title_col = next((col for col in possible_title_cols if col in df.columns), None)

        if title_col:
            val = row[title_col]
            resource_title = str(val).strip() if pd.notna(val) else "Unnamed Resource"
        else:
            resource_title = "Unnamed Resource"

        description = str(row["Description"]).strip() if "Description" in df.columns and pd.notna(row["Description"]) else ""
        link_html = ""
        if "Links" in df.columns and pd.notna(row["Links"]):
            link_html = f'<p><a href="{row["Links"]}" target="_blank">🔗 Access Resource</a></p>'

        type_html = f"<p>📂 <b>Type:</b> {row['Type']}</p>" if "Type" in df.columns and pd.notna(row["Type"]) else ""
        version_html = f"<p>🧾 <b>Version:</b> {row['Version']}</p>" if "Version" in df.columns and pd.notna(row["Version"]) else ""
        date_html = f"<p>📅 <b>Year/Month:</b> {row['Year/Month of Data Availability']}</p>" if "Year/Month of Data Availability" in df.columns and pd.notna(row["Year/Month of Data Availability"]) else ""
        purpose_html = f"<p>🎯 <b>Purpose:</b> {row['Purpose']}</p>" if "Purpose" in df.columns and pd.notna(row["Purpose"]) else ""

        st.markdown(
            f"""
            <div style="border:1px solid #ddd; border-radius:10px; padding:15px; margin-bottom:15px; background-color:#fafafa;">
                <h3 style="margin-bottom:5px;">🔹 {resource_title}</h3>
                <p>{description}</p>
                {link_html}
                {type_html}
                {version_html}
                {date_html}
                {purpose_html}
            </div>
            """,
            unsafe_allow_html=True
        )
    st.stop()

# ----- Default Table View ----- #
st.dataframe(df, use_container_width=True)

# ========================= #
#           FOOTER          #
# ========================= #
st.markdown("<hr style='border:1px solid #ddd'/>", unsafe_allow_html=True)
st.markdown(
    """
    **Developed by Shubh**  
    📧 [dhadiwalshubh348@gmail.com](mailto:dhadiwalshubh348@gmail.com)  
    📘 Powered by [Streamlit](https://streamlit.io) | © 2025 GeoAI Repository
    """
)
