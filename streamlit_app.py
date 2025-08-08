import streamlit as st
import pandas as pd

# ----- PAGE CONFIGURATION -----
st.set_page_config(page_title="GeoAI Repository", layout="wide")

# ----- CUSTOM CSS -----
st.markdown("""
    <style>
        .block-container {
            padding: 2rem 2rem 2rem 2rem;
        }
        .stButton>button {
            color: white;
            background: #4CAF50;
        }
        .stRadio > div {
            flex-direction: row;
        }
        .title-style {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1a73e8;
        }
        .desc-style {
            font-size: 0.95rem;
        }
        .link-style {
            font-size: 0.9rem;
            color: #007BFF;
        }
    </style>
""", unsafe_allow_html=True)

# ----- FIELD CONFIG -----
FIELD_CONFIG = {
    "Data Sources": ["Name of Source", "Link", "Description", "Year/Month", "Countries Covered", "Type", "Spatial Resolution", "Version", "Purpose"],
    "Tools": ["Tool Name", "Description", "Link", "Datasets Availability", "Type", "Applicability", "Purpose", "Availability"],
    "Free Tutorials": ["Tutorial Name", "Description", "Purpose", "Link"],
    "Python Codes (GEE)": ["Title", "Purpose", "Link"],
    "Courses": ["Course Name", "Description", "Purpose", "Version", "Link"]
}

# ----- LOAD DATA FUNCTION -----
@st.cache_data
def load_data(sheet_name):
    df = pd.read_excel("Geospatial Data Repository (1).xlsx", sheet_name=sheet_name)
    df.columns = df.iloc[0]  # First row as header
    df = df[1:]  # Remove header row from data
    df = df.dropna(how="all")  # Drop fully empty rows
    df = df.dropna(subset=[df.columns[0]])  # Ensure first col not empty
    df.columns = [str(c).strip() for c in df.columns]  # Clean column names
    return df

# ----- SIDEBAR NAVIGATION -----
st.sidebar.header("🧭 Navigation")
sheet_options = {
    "Data Sources": "Data Sources",
    "Tools": "Tools",
    "Free Tutorials": "Free Tutorials",
    "Python Codes (GEE)": "Google Earth EnginePython Codes",
    "Courses": "Courses",
}
selected_tab = st.sidebar.radio("Select Category", list(sheet_options.keys()))

# ----- LOAD DATA -----
df = load_data(sheet_options[selected_tab])

# ----- SIDEBAR FILTERS -----
st.sidebar.markdown("---")
search_term = st.sidebar.text_input("🔍 Search Repository")
if search_term:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]

if selected_tab == "Data Sources" and "Type" in df.columns:
    type_filter = st.sidebar.multiselect("📁 Filter by Type", df["Type"].dropna().unique())
    if type_filter:
        df = df[df["Type"].isin(type_filter)]

# ----- MAIN TITLE -----
st.title(f"🌍 GeoAI Repository – {selected_tab}")

# ----- GET FIELDS FOR THIS TAB -----
fields_to_display = FIELD_CONFIG.get(selected_tab, [df.columns[0]])
title_field = fields_to_display[0]

# ----- DISPLAY DATA AS CARDS -----
if df.empty:
    st.warning("No results found. Try adjusting your search or filters.")
else:
    cols = st.columns(2)
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i % 2]:
            # Title
            resource_title = str(row.get(title_field, "")).strip() if pd.notna(row.get(title_field)) else "Unnamed Resource"
            st.markdown(f"<div class='title-style'>🔹 {resource_title}</div>", unsafe_allow_html=True)

            # Display other fields in order
            for field in fields_to_display[1:]:
                if field in df.columns and pd.notna(row.get(field)) and str(row.get(field)).strip():
                    value = row[field]
                    if "link" in field.lower():
                        st.markdown(f"<div class='link-style'>🔗 [{field}]({value})</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{field}:** {value}")

            st.markdown("---")
