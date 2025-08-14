import streamlit as st
import pandas as pd
import hashlib
import re
import os
import streamlit.components.v1 as components
import json
import os
from datetime import date

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="GeoAI Repository",
    page_icon="https://raw.githubusercontent.com/Shubhdhadiwal/GeoAIRepository/main/geoai_logo.png",
    layout="wide"
)

# ===== LOGO =====
st.image(
    "https://raw.githubusercontent.com/Shubhdhadiwal/GeoAIRepository/main/geoai_logo.png",
    width=200
)

# ===== GITHUB RAW EXCEL URL =====
GITHUB_RAW_URL = "https://github.com/Shubhdhadiwal/GeoAIRepository/raw/main/Geospatial%20Data%20Repository%20(2).xlsx"

# ===== VISITOR COUNTER =====
VISITOR_COUNT_FILE = "visitor_count_by_date.json"

def get_visitor_count_today():
    today_str = str(date.today())
    if not os.path.exists(VISITOR_COUNT_FILE):
        with open(VISITOR_COUNT_FILE, "w") as f:
            json.dump({}, f)
        return 0
    with open(VISITOR_COUNT_FILE, "r") as f:
        try:
            counts = json.load(f)
        except json.JSONDecodeError:
            counts = {}
    return counts.get(today_str, 0)

def get_total_visitor_count():
    if not os.path.exists(VISITOR_COUNT_FILE):
        return 0
    with open(VISITOR_COUNT_FILE, "r") as f:
        try:
            counts = json.load(f)
        except json.JSONDecodeError:
            counts = {}
    return sum(counts.values())

def increment_visitor_count_today():
    today_str = str(date.today())
    if not os.path.exists(VISITOR_COUNT_FILE):
        counts = {}
    else:
        with open(VISITOR_COUNT_FILE, "r") as f:
            try:
                counts = json.load(f)
            except json.JSONDecodeError:
                counts = {}
    counts[today_str] = counts.get(today_str, 0) + 1
    with open(VISITOR_COUNT_FILE, "w") as f:
        json.dump(counts, f)
    return counts[today_str]

# Only increment once per session
if 'visitor_counted' not in st.session_state:
    st.session_state.today_visitor_count = increment_visitor_count_today()
    st.session_state.total_visitor_count = get_total_visitor_count()
    st.session_state.visitor_counted = True

# ===== WELCOME MESSAGE =====
st.markdown("### Welcome to GeoAI Repository!")
st.markdown(
    f"""
    <p style='font-size:14px; color:gray;'>
    📅 Today's Visitors: <b>{st.session_state.today_visitor_count}</b>  
    📈 Total Visitors: <b>{st.session_state.total_visitor_count}</b>
    </p>
    """,
    unsafe_allow_html=True
)

# ===== PASSWORD UTILS =====
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ===== USER CREDENTIALS =====
USER_CREDENTIALS = {
    "Shubh1301": hash_password("Shubh130127")
}

# ===== SESSION AUTH SETUP =====
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['username'] = None

def login():
    st.title("🔐 Login to GeoAI Repository")

    # Support/contact info
    st.markdown("""
    <hr>
    <p style="font-size:12px; color:gray;">
    🛠️ <b>Need login access or help?</b><br>
    Please contact the developer for login credentials:<br>
    👉 <a href="https://www.linkedin.com/in/shubh-dhadiwal/" target="_blank">Shubh Dhadiwal on LinkedIn</a>
    </p>
    <hr>
    """, unsafe_allow_html=True)
    
    username = st.text_input("Username", key="username_input")
    password = st.text_input("Password", type="password", key="password_input")
    
    if st.button("Login"):
        hashed_input = hash_password(password)
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == hashed_input:
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
        else:
            st.error("❌ Invalid username or password")

if not st.session_state['authenticated']:
    login()
    st.stop()

# ===== SIDEBAR =====
if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.rerun()
    
st.sidebar.title(f"Welcome, {st.session_state['username']}!")

# ===== SHEET OPTIONS =====
sheet_options = {
    "About": "About",
    "Data Sources": "Data Sources",
    "Tools": "Tools",
    "Free Tutorials": "Free Tutorials",
    "Python Codes (GEE)": "Google Earth EnginePython Codes",
    "Courses": "Courses",
    "Dashboards": "Dashboards",
    "Submit New Resource": "Submit New Resource",
    "Favorites": "Favorites",
    "FAQ": "FAQ"
}

# ===== DATA LOADING =====
@st.cache_data(show_spinner=False)
def load_data(sheet_name):
    try:
        df = pd.read_excel("Geospatial Data Repository (2).xlsx", sheet_name=sheet_name)
        df.columns = df.iloc[0]
        df = df[1:]
        df = df.dropna(subset=[df.columns[0]])
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        if sheet_name == "Tools":
            new_cols = {col: "Link" for col in df.columns if isinstance(col, str) and col.startswith("Column")}
            if new_cols:
                df = df.rename(columns=new_cols)

        return df
    except Exception as e:
        st.error(f"Error loading sheet '{sheet_name}': {e}")
        return pd.DataFrame()

# ===== SIDEBAR NAVIGATION ===== #
st.sidebar.header("🧭 GeoAI Repository")
selected_tab = st.sidebar.radio("Select Section", list(sheet_options.keys()))

# ===== HANDLE SPECIAL TABS WITHOUT EXCEL SHEETS ===== #
if selected_tab == "Dashboards":
    st.title("🌍 Dashboards")

    # Common iframe height
    iframe_height = 700

    # Function for adding uniform dashboards
    def add_dashboard_expander(title, description_md, doc_links, iframe_url, code_editor_url=None, note_md=None, citation_md=None):
        """
        title: Dashboard title (string)
        description_md: Markdown description text
        doc_links: List of tuples -> [(text, url), ...]
        iframe_url: URL to embed
        code_editor_url: Optional Earth Engine code link
        note_md: Optional Markdown notes
        citation_md: Optional Markdown citation text
        """
        with st.expander(f"▶️ {title}"):
            st.markdown(description_md)
            if doc_links:
                for text, url in doc_links:
                    st.markdown(f"🔗 [{text}]({url})")
            st.markdown("---")
            st.markdown(
                f"""
                <iframe 
                    src="{iframe_url}" 
                    width="100%" 
                    height="{iframe_height}" 
                    frameborder="0" 
                    allowfullscreen>
                </iframe>
                """,
                unsafe_allow_html=True
            )
            if code_editor_url:
                st.markdown(
                    f"""
                    Dashboard created by Shubh Dhadiwal using Google Earth Engine.  
                    [🚀 Open Earth Engine Code Editor here]({code_editor_url})
                    """,
                    unsafe_allow_html=True
                )
            if note_md:
                st.markdown("**Note:**")
                st.markdown(note_md, unsafe_allow_html=True)
            if citation_md:
                st.markdown("---")
                st.markdown("**Citation:**")
                st.markdown(citation_md, unsafe_allow_html=True)

    # ================= DASHBOARDS ================= #

    # 1. Google Open Building Dashboard
    add_dashboard_expander(
        "Google Open Building Dashboard",
        """
        This large-scale open dataset consists of outlines of buildings derived from high-resolution 50 cm satellite imagery.  
        It contains **1.8B building detections** in Africa, Latin America, Caribbean, South Asia and Southeast Asia.  
        The inference spanned an area of 58M km², carried out in May 2023.
        
        Each building includes:
        - Polygon footprint geometry  
        - Confidence score (building likelihood)  
        - Plus Code (center of building)  

        **Applications:**  
        - Population estimation  
        - Urban planning  
        - Humanitarian response  
        - Environmental and climate science  
        """,
        [("Official Dataset Documentation", "https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_Research_open-buildings_v3_polygons")],
        "https://ee-shubhdhadiwal.projects.earthengine.app/view/geoai",
        "https://code.earthengine.google.com/272ebbc2fd09e86a3b256c9c2f259b9f?hideCode=true"
    )

    # 2. Local Climate Zones Dashboard
    add_dashboard_expander(
        "Local Climate Zones (LCZ) Dashboard",
        """
        This global LCZ map (100m resolution, nominal year 2018) is derived from multiple EO datasets and expert labels.  
        LCZ classification supports **urban heat island** studies, urban climate modeling, and planning.  

        **Classes:**  
        - 10 'built' environment types  
        - 7 'natural' land-cover types for reference areas  
        """,
        [("Official Dataset Documentation", "https://developers.google.com/earth-engine/datasets/catalog/RUB_RUBCLIM_LCZ_global_lcz_map_latest#description")],
        "https://ee-shubhdhadiwal.projects.earthengine.app/view/lcz-dashboard",
        "https://code.earthengine.google.com/db65e6b4ece8341249a978d4a1509f0e"
    )

    # 3. NASA Sea Level Evaluation Tool
    add_dashboard_expander(
        "NASA Sea Level Evaluation Tool",
        """
        Interactive visualization of global sea level trends using satellite altimetry missions (TOPEX/Poseidon, Jason, Sentinel-6).  

        **Features:**  
        - Explore regional/global sea level anomalies  
        - Compare across missions  
        - Overlay climate indices (ENSO, PDO, NAO, etc.)  
        """,
        [("NASA Sea Level Evaluation Tool Website", "https://sealevel.nasa.gov/sea-level-evaluation-tool")],
        "https://sealevel.nasa.gov/sea-level-evaluation-tool"
    )

    # 4. BBBike OSM Extract Service
    add_dashboard_expander(
        "BBBike OSM Extract Service",
        """
        Extract **OpenStreetMap (OSM)** data for any area in formats like Shapefile, GeoJSON, KML, CSV.  
        Ideal for GIS analysis, navigation, and research.
        """,
        [],
        "https://extract.bbbike.org/"
    )

    # 5. DIVA-GIS Global Data Access
    add_dashboard_expander(
        "DIVA-GIS Global Data Access",
        """
        Download free spatial data for any country:  
        - Administrative boundaries  
        - Population density  
        - Climate & elevation  
        - Land cover maps  
        """,
        [("Official DIVA-GIS Website", "https://diva-gis.org/data.html")],
        "https://diva-gis.org/data.html"
    )

    # 6. Gridded Population of World 2020
    add_dashboard_expander(
        "Gridded Population of World 2020",
        """
        Estimates persons per ~1 km² grid cell, adjusted to **UN WPP 2015 Revision** totals.  
        Years: 2000, 2005, 2010, 2015, 2020.  
        """,
        [("Dataset Documentation - GPWv4, CIESIN, Columbia University", "https://doi.org/10.7927/H4F47M65")],
        "https://ee-shubhdhadiwal.projects.earthengine.app/view/gridded-population-of-world-2020",
        "https://code.earthengine.google.com/dca1dbdd9db97db7276ffab3cf5b2fe6",
        citation_md="""
        Center for International Earth Science Information Network - CIESIN - Columbia University. 2018.  
        *Gridded Population of the World, Version 4 (GPWv4.11): Population Density Adjusted to Match 2015 Revision of UN WPP Country Totals, Revision 11.*  
        Palisades, NY: NASA SEDAC. [https://doi.org/10.7927/H4F47M65](https://doi.org/10.7927/H4F47M65)  
        Accessed 12 August 2025.
        """
    )

    # 7. Global Landsat LST Explorer
    add_dashboard_expander(
        "Global Landsat LST Explorer",
        """
        Analyze **Land Surface Temperature (LST)** from Landsat 8 & 9 C2 L2 thermal bands (`ST_B10`).  
        - Period: March–June (2015–2024) median composites  
        - Resolution: 30 m  
        """,
        [
            ("Landsat 8 C2 L2 Documentation", "https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2"),
            ("Landsat 9 C2 L2 Documentation", "https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2")
        ],
        "https://ee-shubhdhadiwal.projects.earthengine.app/view/global-landsat-lst-explorer",
        "https://code.earthengine.google.com/e4830267a6dae171f1bf1057f52e19bc"
    )

    # 8. NASA POWER Data Access Viewer
    add_dashboard_expander(
        "NASA POWER Data Access Viewer",
        """
        Access global meteorological & solar energy data for renewable energy, agriculture, and climate research.  
        Sources: MERRA-2, GEOS models.
        """,
        [("NASA POWER Data Access Viewer Website", "https://power.larc.nasa.gov/data-access-viewer/")],
        "https://power.larc.nasa.gov/data-access-viewer/"
    )

    # 9. ESA WorldCover LULC Change Analysis 2020–2021
    add_dashboard_expander(
        "ESA WorldCover LULC Change Analysis 2020–2021",
        """
        ESA WorldCover 10 m global land cover maps for 2020 & 2021 from Sentinel-1 & 2.  
        """,
        [
            ("ESA WorldCover Website", "https://esa-worldcover.org/en"),
            ("User Manual & Validation Report", "https://esa-worldcover.org/en/data-access")
        ],
        "https://ee-shubhdhadiwal.projects.earthengine.app/view/esa-lulc-2020-21",
        note_md="""
        1. This dashboard displays results only; advanced analysis should be done in GIS.  
        2. Contact the developer for code access and customization.
        """
    )

    # 10. MODIS LULC Change 2010–2024
    add_dashboard_expander(
        "MODIS Land Use Land Cover (LULC) Change Analysis 2010–2024",
        """
        Annual MODIS global land cover types (MCD12Q1 V6.1) from 2010–2024.  
        Classification schemes: IGBP, UMD, LAI, BGC, PFT, LCCS.  
        """,
        [
            ("MODIS Land Cover Overview", "https://lpdaac.usgs.gov/products/mcd12q1v061/"),
            ("User Guide", "https://lpdaac.usgs.gov/documents/101/MCD12_User_Guide_V6.pdf")
        ],
        "https://ee-shubhdhadiwal.projects.earthengine.app/view/modis-lulc-2010-2024",
        note_md="""
        1. Visualizes MODIS LULC maps; detailed analysis should be done in GIS or Earth Engine.  
        2. Contact the developer for scripts and tailored change detection services.
        """
    )

    st.stop()

# ===== NON-SHEET TABS: About, Submit New Resource, FAQ ===== #
if selected_tab == "About":
    st.title("📘 About GeoAI Repository")
    
    st.markdown("""
    The **GeoAI Repository** is an interactive and open-access platform designed for 
    **students, researchers, and professionals** in geospatial analytics, urban planning, 
    and climate action. It integrates **Google Earth Engine (GEE)**, Python, and other 
    open-source tools to provide powerful, cloud-based geospatial analysis.
    """)
    
    st.info("""
    - 🌐 **Public Geospatial Datasets**: Access global and regional datasets on land use, climate, 
      urban infrastructure, and environmental change.  
    - 🛠️ **Open-Source Tools & Platforms**: Built on GEE, Python, and other open-source frameworks 
      for reproducible geospatial analysis.  
    - 📘 **Tutorials & Workflows**: Step-by-step guides and examples for implementing geospatial AI projects.  
    - 💻 **Python & GEE Scripts**: Ready-to-use scripts for satellite data processing, land cover analysis, 
      and urban/climate modeling.  
    - 📊 **Interactive Visualizations**: Explore dynamic maps, charts, and dashboards for real-time insights.
    """)
    
    st.subheader("🌟 Vision")
    st.markdown("""
    To empower **researchers, students, policymakers, and urban/climate planners** with 
    **accessible, AI-driven geospatial intelligence**, enabling informed decisions for a 
    **sustainable, resilient, and smarter planet**.
    """)
    
    st.subheader("🎯 Mission")
    st.markdown("""
    1. **Democratize Geospatial Data:** Provide open access to high-resolution satellite imagery, environmental, and urban datasets.  
    2. **Leverage AI & Machine Learning:** Integrate advanced AI models for land cover classification, predictive analytics, and anomaly detection.  
    3. **Promote Open-Source Tools:** Encourage reproducibility and innovation by offering Python/GEE scripts, tutorials, and workflows.  
    4. **Enable Real-Time Insights:** Create interactive dashboards that visualize trends, patterns, and changes in the environment, climate, and urban landscapes.  
    5. **Support Decision-Making:** Facilitate sustainable planning, climate action, and risk mitigation through data-driven insights.
    """)
    
    st.markdown("""
    This dashboard aims to **democratize geospatial intelligence**, enabling users to analyze, visualize, 
    and interpret complex spatial data efficiently without heavy local computing resources.
    """)

    categories_to_check = ["Data Sources", "Tools", "Courses", "Free Tutorials", "Python Codes (GEE)"]
    counts = {}
    for cat in categories_to_check:
        df_cat = load_data(sheet_options[cat])
        counts[cat] = len(df_cat)

    st.subheader("📊 Repository Content Overview")

    # Show counts as metrics in columns without any selection
    cols = st.columns(len(categories_to_check))
    for i, cat in enumerate(categories_to_check):
        cols[i].metric(label=cat, value=counts.get(cat, 0))

    st.markdown("---")

    # ADD CREATIVE COMMONS LICENSE INFO HERE
    st.markdown("""
    <p style='text-align:center; font-size:12px; color:gray;'>
    Licensed under the <a href='https://creativecommons.org/licenses/by-nc/4.0/' target='_blank'>Creative Commons BY-NC 4.0 License</a>.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align:center; font-size:12px; color:gray;'>
    Developed by Shubh | 
    <a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a>
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("""
<p style='text-align:center; font-size:12px; color:gray;'>
© 2025 GeoAI Repository
""", unsafe_allow_html=True)

    st.stop()

if selected_tab == "Submit New Resource":
    st.title("📤 Submit a New Resource")
    st.markdown("Help us grow this repository by contributing useful links and resources.")
    google_form_url = "https://forms.gle/FZZpvr4xQyon5nDs6"
    st.markdown(f"You can submit your resource using [this Google Form]({google_form_url}).")
    st.stop()

if selected_tab == "FAQ":
    st.title("❓ Frequently Asked Questions")
    faqs = {
        "What is GeoAI Repository?": "It is a free and open resource hub for geospatial analytics, ML, and planning.",
        "How can I contribute resources?": "Use the 'Submit New Resource' tab to add new links and resources.",
        "Are the datasets free to use?": "Yes, all datasets listed here are publicly accessible and free.",
        "Can I save favorite resources?": "Yes, use the 'Favorites' tab to view and manage your favorite items.",
        "What are the Dashboards?": "The Dashboards section provides interactive visualization of geospatial data. Check them out for detailed geospatial insights!",
        "Who developed this repository?": "This repository is developed and maintained by Shubh Dhadiwal."
    }
    for question, answer in faqs.items():
        with st.expander(question):
            st.write(answer)
    st.stop()

# ===== INITIALIZE FAVORITES ===== #
if "favorites" not in st.session_state:
    st.session_state.favorites = {}

# ===== LOAD DATA FOR OTHER TABS INCLUDING FAVORITES ===== #
if selected_tab != "Favorites":
    df = load_data(sheet_options[selected_tab])
else:
    all_fav_items = []
    for key, items in st.session_state.favorites.items():
        df_cat = load_data(sheet_options.get(key, key))
        if df_cat.empty:
            continue
        fav_rows = df_cat.loc[df_cat.index.isin(items)].copy()
        fav_rows["Category"] = key
        all_fav_items.append(fav_rows)
    if all_fav_items:
        df = pd.concat(all_fav_items)
    else:
        df = pd.DataFrame()

# ===== SEARCH & FILTER ===== #
search_term = st.sidebar.text_input("🔍 Search")
if selected_tab not in ["Favorites", "About", "Submit New Resource", "Dashboards", "FAQ"] and search_term:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]

if selected_tab == "Data Sources" and "Type" in df.columns:
    type_filter = st.sidebar.multiselect("📂 Filter by Type", sorted(df["Type"].dropna().unique()))
    if type_filter:
        df = df[df["Type"].isin(type_filter)]

# ===== TITLE MAP ===== #
title_map = {
    "Data Sources": "Data Source",
    "Tools": "Tools",
    "Courses": "Tutorials",
    "Python Codes (GEE)": "Title",
    "Free Tutorials": "Tutorials",
    "Favorites": "Title"
}

title_col = title_map.get(selected_tab, df.columns[0] if not df.empty else None)

if selected_tab == "Favorites":
    title_col = "Title" if "Title" in df.columns else (df.columns[0] if not df.empty else None)

# ===== DISPLAY TITLE ===== #
st.title(f"🌍 GeoAI Repository – {selected_tab}")

if df.empty:
    st.info("No resources to display.")
    st.stop()

# ===== DISPLAY DATA ===== #
exclude_cols = [title_col, "Description", "Purpose", "S.No", "Category"]

link_columns_map = {
    "Data Sources": ["Links", "Link"],
    "Tools": ["Tool Link", "Link", "Links"],
    "Courses": ["Course Link", "Link", "Links"],
    "Free Tutorials": ["Link", "Links", "Tutorial Link"],
    "Python Codes (GEE)": ["Link", "Links", "Link to the codes"],
    "Favorites": ["Link", "Links", "Link to the codes", "Tool Link", "Course Link", "Tutorial Link"]
}

possible_links = link_columns_map.get(selected_tab, ["Links", "Link", "Link to the codes", "Tool Link", "Course Link", "Tutorial Link"])

def highlight_search(text, term):
    if not term:
        return text
    regex = re.compile(re.escape(term), re.IGNORECASE)
    return regex.sub(lambda match: f"**:yellow[{match.group(0)}]**", str(text))

view_mode = st.sidebar.radio("View Mode", ["Detailed", "Compact"])

for idx, row in df.iterrows():
    if selected_tab.strip().lower() == "favorites":
        category_key = row.get("Category", None)
        title_for_fav = title_map.get(category_key, title_col)  # fallback to default title_col
        resource_title = row.get(title_for_fav)
        if not resource_title or str(resource_title).strip() == "":
            resource_title = f"Resource-{idx+1}"
    else:
        category_key = selected_tab
        resource_title = row.get(title_col)
        if not resource_title or str(resource_title).strip() == "":
            resource_title = f"Resource-{idx+1}"

    displayed_title = highlight_search(resource_title, search_term)

    # Collect links for this row
    links = []
    for col in possible_links:
        if col in df.columns and pd.notna(row.get(col)):
            val = str(row[col]).strip()
            if val.lower().startswith(("http://", "https://", "www.")):
                links.append((col, val))

    if view_mode == "Detailed" or selected_tab.strip().lower() == "favorites":
        # Show detailed view for Favorites always
        with st.expander(f"🔹 {displayed_title}", expanded=False):
            col1, col2 = st.columns([0.9, 0.1])
            with col2:
                fav_checkbox = st.checkbox(
                    "⭐",
                    value=idx in st.session_state.favorites.get(category_key, []),
                    key=f"{category_key}_{idx}"
                )
            with col1:
                if "Description" in df.columns and pd.notna(row.get("Description")):
                    st.write(highlight_search(row["Description"], search_term))
                for link_name, link_url in links:
                    st.markdown(f"[🔗 {link_name}]({link_url})", unsafe_allow_html=True)
                if "Purpose" in df.columns and pd.notna(row.get("Purpose")):
                    st.markdown(f"**🎯 Purpose:** {highlight_search(row['Purpose'], search_term)}")
                exclude_cols = [title_col, "Description", "Purpose", "S.No", "Category"] + possible_links
                for col in df.columns:
                    if col not in exclude_cols and pd.notna(row.get(col)):
                        st.markdown(f"**{col}:** {highlight_search(row[col], search_term)}")

            # Update favorites list
            if fav_checkbox and idx not in st.session_state.favorites.get(category_key, []):
                st.session_state.favorites.setdefault(category_key, []).append(idx)
            elif not fav_checkbox and idx in st.session_state.favorites.get(category_key, []):
                st.session_state.favorites[category_key].remove(idx)

    else:
        # Compact mode for non-favorites tabs only
        compact_col1, compact_col2, compact_col3 = st.columns([6, 3, 1])
        with compact_col1:
            st.markdown(f"🔹 {displayed_title}")
        with compact_col2:
            for link_name, link_url in links:
                st.markdown(f"[🔗 {link_name}]({link_url})", unsafe_allow_html=True)
        with compact_col3:
            fav_checkbox = st.checkbox(
                "⭐",
                value=idx in st.session_state.favorites.get(category_key, []),
                key=f"compact_{category_key}_{idx}"
            )
            if fav_checkbox and idx not in st.session_state.favorites.get(category_key, []):
                st.session_state.favorites.setdefault(category_key, []).append(idx)
            elif not fav_checkbox and idx in st.session_state.favorites.get(category_key, []):
                st.session_state.favorites[category_key].remove(idx)

st.markdown("""
<p style='text-align:center; font-size:12px; color:gray;'>
Developed by Shubh | 
<a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a> | 
© Copyright GeoAI Repository
</p>
""", unsafe_allow_html=True)

