import streamlit as st
import pandas as pd
import hashlib
import re
import os
import streamlit.components.v1 as components
import json
import os
from datetime import date

import streamlit as st
import pandas as pd
import os
import json
import hashlib
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

# Increment visitor count once per session
if 'visitor_counted' not in st.session_state:
    st.session_state.today_visitor_count = increment_visitor_count_today()
    st.session_state.total_visitor_count = get_total_visitor_count()
    st.session_state.visitor_counted = True

# ===== WELCOME MESSAGE =====
st.markdown("### Welcome to GeoAI Repository!")
st.markdown(
    f"""
    <p style='font-size:14px; color:gray;'>
    📅 Today's Visitors: <b>{st.session_state.today_visitor_count}</b><br>
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
    "Shubh1301": hash_password("Shubh130100")
}

# ===== SESSION AUTH SETUP =====
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['username'] = None

def login():
    # Add GeoAI login image
    st.image(
        "https://raw.githubusercontent.com/Shubhdhadiwal/GeoAIRepository/main/geoai_login.png",
        use_column_width=True
    )

    st.title("🔐 Login to GeoAI Repository")

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

# ===== LOGIN CHECK =====
if not st.session_state['authenticated']:
    login()
    st.stop()

# ===== SIDEBAR =====
if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.experimental_rerun()

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

    with st.expander("▶️ Google Open Building Dashboard"):
        st.markdown("""
        This large-scale open dataset consists of outlines of buildings derived from high-resolution 50 cm satellite imagery. It contains 1.8B building detections in Africa, Latin America, Caribbean, South Asia and Southeast Asia. The inference spanned an area of 58M km².

For each building in this dataset we include the polygon describing its footprint on the ground, a confidence score indicating how sure we are that this is a building, and a Plus Code corresponding to the center of the building. There is no information about the type of building, its street address, or any details other than its geometry.

Building footprints are useful for a range of important applications: from population estimation, urban planning and humanitarian response to environmental and climate science. The project is based in Ghana, with an initial focus on the continent of Africa and new updates on South Asia, South-East Asia, Latin America and the Caribbean.

Inference was carried out during May 2023.
        """)
        st.markdown("🔗 [Official Dataset Documentation](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_Research_open-buildings_v3_polygons)")
        st.markdown("---")
        st.markdown(
            """
            <iframe 
                src="https://ee-shubhdhadiwal.projects.earthengine.app/view/geoai" 
                width="100%" height="600" frameborder="0" allowfullscreen>
            </iframe>
            """,
            unsafe_allow_html=True
        )
        st.markdown("""
        Dashboard created by Shubh Dhadiwal using Google Earth Engine.  
        [🚀 Open Earth Engine Code Editor here](https://code.earthengine.google.com/272ebbc2fd09e86a3b256c9c2f259b9f?hideCode=true)
        """, unsafe_allow_html=True)

    with st.expander("▶️ Local Climate Zones (LCZ) Dashboard"):
        st.markdown("""
        This global map of Local Climate Zones, at 100m pixel size and representative for the nominal year 2018, is derived from multiple earth observation datasets and expert LCZ class labels. LCZ_Filter is the recommended band for most users. The other classification band, LCZ, is only provided as it is used to calculate the LCZ_Probability band.

The LCZ scheme complements other land use / land cover schemes by its focus on urban and rural landscape types, which can be described by any of the 17 classes in the LCZ scheme. Out of the 17 LCZ classes, 10 reflect the 'built' environment, and each LCZ type is associated with generic numerical descriptions of key urban canopy parameters critical to model atmospheric responses to urbanisation. In addition, since LCZs were originally designed as a new framework for urban heat island studies, they also contain a limited set (7) of 'natural' land-cover classes that can be used as 'control' or 'natural reference' areas.
        """)
        st.markdown("🔗 [Official Dataset Documentation](https://developers.google.com/earth-engine/datasets/catalog/RUB_RUBCLIM_LCZ_global_lcz_map_latest#description)")
        st.markdown("---")
        st.markdown(
            """
            <iframe 
                src="https://ee-shubhdhadiwal.projects.earthengine.app/view/lcz-dashboard" 
                width="100%" height="600" frameborder="0" allowfullscreen>
            </iframe>
            """,
            unsafe_allow_html=True
        )
        st.markdown("""
        Dashboard created by Shubh Dhadiwal using Google Earth Engine.  
        [🚀 Open Earth Engine Code Editor here](https://code.earthengine.google.com/db65e6b4ece8341249a978d4a1509f0e)
        """, unsafe_allow_html=True)

    with st.expander("▶️ NASA Sea Level Evaluation Tool"):
        st.markdown("""
        The **NASA Sea Level Evaluation Tool** provides interactive visualization and analysis of global sea level data from multiple satellite altimetry missions.  
        Users can:
        - Explore sea level trends and anomalies
        - Compare data from different missions (e.g., TOPEX/Poseidon, Jason-1/2/3, Sentinel-6)
        - Analyze time series for specific regions or globally
        - Overlay climate indices for correlation studies
    
        **Data Sources:**  
        - Satellite altimetry measurements from NASA, NOAA, CNES, and ESA missions  
        - Climate indices (ENSO, PDO, NAO, etc.)
    
        **Key Features:**  
        - Interactive maps and charts
        - Regional or global data selection
        - Downloadable CSV datasets for custom analysis
        """)
        st.markdown("🔗 [NASA Sea Level Evaluation Tool Website](https://sealevel.nasa.gov/sea-level-evaluation-tool)")
        components.iframe(
            "https://sealevel.nasa.gov/sea-level-evaluation-tool",
            height=1200,
            width=1400,
        )
        st.markdown("""
        <p style='font-size:15px; color:gray;'>
        Source: NASA, <a href="https://sealevel.nasa.gov/sea-level-evaluation-tool" target="_blank">https://sealevel.nasa.gov/sea-level-evaluation-tool</a>
        </p>
        """, unsafe_allow_html=True)


    with st.expander("▶️ BBBike OSM Extract Service"):
        st.markdown("""
        The **BBBike OSM Extract Service** is a free web-based tool for extracting **OpenStreetMap (OSM)** data for custom-defined areas anywhere in the world.  
        Users can:
        - Select a region by drawing a polygon or choosing from predefined cities
        - Download OSM data in multiple formats (Shapefile, GeoJSON, Garmin IMG, KML, PBF, CSV, etc.)
        - Filter datasets to include only desired layers (roads, buildings, land use, points of interest, etc.)
    
        **Key Features:**  
        - Global coverage
        - Multiple coordinate reference systems supported
        - Regularly updated extracts (usually weekly)
        - Free to use with generous area limits
    
        **Typical Uses:**  
        - GIS analysis
        - Urban planning
        - Navigation system development
        - Research projects
        """)
        components.iframe(
            "https://extract.bbbike.org/",
            height=700,
            width=1300,
            scrolling=True
        )

    with st.expander("▶️ DIVA-GIS Global Data Access"):
        st.markdown("""
        **DIVA-GIS** provides free spatial data for any country in the world, including:
        - Administrative boundaries
        - Roads, railways, and population density
        - Elevation and climate data
        - Land cover maps

        This is especially useful for GIS analysis, ecological studies, and spatial planning.

        🔗 [Official DIVA-GIS Website](https://diva-gis.org/data.html)
        """)
        st.components.v1.iframe(
            "https://diva-gis.org/data.html",
            height=900,
            width=1400,
            scrolling=True
        )  
    
    with st.expander("▶️ Gridded Population of World 2020"):
        st.markdown("""
        This dataset contains estimates of the number of persons per 30 arc-second (~1 km) grid cell, consistent with national censuses and population registers with respect to relative spatial distribution but adjusted to match the 2015 Revision of UN World Population Prospects country totals.  
        There is one image for each modeled year (2000, 2005, 2010, 2015, and 2020). Population is distributed to cells using proportional allocation of population from census and administrative units.
        """)
        st.markdown("🔗 [General Dataset Documentation - GPWv4, CIESIN, Columbia University](https://doi.org/10.7927/H4F47M65)")
        st.markdown("---")
        st.markdown(
            """
            <iframe 
                src="https://ee-shubhdhadiwal.projects.earthengine.app/view/gridded-population-of-world-2020" 
                width="100%" height="600" frameborder="0" allowfullscreen>
            </iframe>
            """,
            unsafe_allow_html=True
        )
        st.markdown("""
        Dashboard created by Shubh Dhadiwal using Google Earth Engine.  
        [🚀 Open Earth Engine Code Editor here](https://code.earthengine.google.com/dca1dbdd9db97db7276ffab3cf5b2fe6)
        """, unsafe_allow_html=True)
    
        st.markdown("""
        ---
        **Citation:**  
        Center for International Earth Science Information Network - CIESIN - Columbia University. 2018.  
        Gridded Population of the World, Version 4 (GPWv4.11): Population Density Adjusted to Match 2015 Revision of UN WPP Country Totals, Revision 11.  
        Palisades, NY: NASA Socioeconomic Data and Applications Center (SEDAC).  
        https://doi.org/10.7927/H4F47M65. Accessed 12 August 2025.
        """)
    
    with st.expander("▶️ Global Landsat LST Explorer"):
        st.markdown("""
        The **Global Landsat LST Explorer** is an interactive Google Earth Engine (GEE) application for analyzing Land Surface Temperature (LST) using Landsat 8 and Landsat 9 Collection 2 Level-2 data.  
        Features include:
        - Selecting **country**, **state/province**, and **year (March–June period)**
        - Visualizing **median LST**
        - Displaying **discrete temperature classes** (e.g., 0–10 °C, 10–20 °C, …, 60–70 °C)
        - Viewing **yearly min/max trend charts** (2015–2024)
        - Exporting processed LST as **GeoTIFF**
        
        **Data Sources & Processing Highlights:**  
        - Landsat 8 (`LANDSAT/LC08/C02/T1_L2`) & Landsat 9 (`LANDSAT/LC09/C02/T1_L2`) thermal band `ST_B10` (Kelvin → °C)  
        - Cloud masking via `QA_PIXEL` band  
        - Median compositing (March 1 – June 30)  
        - FAO GAUL 2015 boundaries for administrative regions  
        - Spatial resolution: 30 m  
        """)
        st.markdown("🔗 [Landsat 8 Collection 2 L2 Documentation](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2)")
        st.markdown("🔗 [Landsat 9 Collection 2 L2 Documentation](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2)")
        st.markdown("---")
        st.markdown(
            """
            <iframe
                src="https://ee-shubhdhadiwal.projects.earthengine.app/view/global-landsat-lst-explorer"
                width="100%" height="600" frameborder="0" allowfullscreen>
            </iframe>
            """,
            unsafe_allow_html=True
        )
        st.markdown("""
        Dashboard created by Shubh Dhadiwal using Google Earth Engine.  
        [🚀 Open Earth Engine Code Editor here](https://code.earthengine.google.com/e4830267a6dae171f1bf1057f52e19bc)
        """, unsafe_allow_html=True)


    st.stop()


# ===== NON-SHEET TABS: About, Submit New Resource, FAQ ===== #
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

