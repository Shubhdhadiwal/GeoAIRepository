import streamlit as st
import pandas as pd
import hashlib
import re
import os
import streamlit.components.v1 as components
import json
from datetime import date
import os


# ===== PAGE CONFIG =====
st.set_page_config(page_title="GeoAI Repository", layout="wide")

# GitHub raw Excel file URL
GITHUB_RAW_URL = "https://github.com/Shubhdhadiwal/GeoAIRepository/raw/main/Geospatial%20Data%20Repository%20(2).xlsx"

import os
import json
from datetime import date
import streamlit as st

# ===== VISITOR COUNTER SETUP =====
VISITOR_COUNT_FILE = "visitor_count_by_date.json"

def get_visitor_counts():
    if not os.path.exists(VISITOR_COUNT_FILE):
        with open(VISITOR_COUNT_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(VISITOR_COUNT_FILE, "r") as f:
        try:
            counts = json.load(f)
        except json.JSONDecodeError:
            counts = {}
    return counts

def save_visitor_counts(counts):
    with open(VISITOR_COUNT_FILE, "w") as f:
        json.dump(counts, f)

def increment_visitor_count_today():
    today_str = str(date.today())
    counts = get_visitor_counts()
    counts[today_str] = counts.get(today_str, 0) + 1
    save_visitor_counts(counts)
    return counts[today_str], sum(counts.values())

# Increment visitor count only once per browser session per day
if 'visitor_counted_date' not in st.session_state or st.session_state.visitor_counted_date != str(date.today()):
    today_count, total_count = increment_visitor_count_today()
    st.session_state.visitor_counted_date = str(date.today())
    st.session_state.today_visitor_count = today_count
    st.session_state.total_visitor_count = total_count
else:
    counts = get_visitor_counts()
    st.session_state.today_visitor_count = counts.get(str(date.today()), 0)
    st.session_state.total_visitor_count = sum(counts.values())

# Display below welcome text (replace st.write below with your welcome text)
st.write("### Welcome to GeoAI Repository!")

# Display visitor counts below welcome
st.markdown(f"""
<p style='font-size:14px; color:gray; margin-top: 0;'>
📅 Today's Visitors: <b>{st.session_state.today_visitor_count}</b> &nbsp;&nbsp;|&nbsp;&nbsp; 
📈 Total Visitors: <b>{st.session_state.total_visitor_count}</b>
</p>
""", unsafe_allow_html=True)

# Utility to hash password string
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Store username and hashed password
USER_CREDENTIALS = {
    "Shubh1301": hash_password("Shubh130100")
}

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['username'] = None

def login():
    st.title("🔐 Login to GeoAI Repository")

 # Support/contact info on login page with smaller font
    st.markdown("""
    <hr>
    <p style="font-size:12px; color:gray;">
    🛠️ <b>Need login access or help?</b><br>
    Please contact the developer for login credentials:<br><br>
    👉 <a href="https://www.linkedin.com/in/shubh-dhadiwal/" target="_blank">Shubh Dhadiwal on LinkedIn</a><br>
    Send a message mentioning your request for login details.
    </p>
    <hr>
    """, unsafe_allow_html=True)
    
    username = st.text_input("Username", key="username_input")
    password = st.text_input("Password", type="password", key="password_input")
    login_pressed = st.button("Login")

    if login_pressed:
        hashed_input = hash_password(password)
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == hashed_input:
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
        else:
            st.error("Invalid username or password")

if not st.session_state['authenticated']:
    login()
    st.stop()

if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.session_state['username'] = None

st.sidebar.title(f"Welcome, {st.session_state['username']}!")

# Sheet options mapping tab name → Excel sheet name (except Dashboards etc. which don't have sheets)
sheet_options = {
    "About": "About",
    "Data Sources": "Data Sources",
    "Tools": "Tools",
    "Free Tutorials": "Free Tutorials",
    "Python Codes (GEE)": "Google Earth EnginePython Codes",
    "Courses": "Courses",
    "Dashboards": "Dashboards",  # note: no sheet actually called "Dashboards"
    "Submit New Resource": "Submit New Resource",
    "Favorites": "Favorites",
    "FAQ": "FAQ"
}

# Display real-time visitor count
st.sidebar.markdown(f"📅 Total Visitors: **{st.session_state.visitor_count}**")

@st.cache_data(show_spinner=False)
def load_data(sheet_name):
    try:
        # You may want to change here to load directly from URL if needed
        # For now assumes local file:
        df = pd.read_excel("Geospatial Data Repository (2).xlsx", sheet_name=sheet_name)
        df.columns = df.iloc[0]  # Use first row as header
        df = df[1:]  # Skip header row from data
        df = df.dropna(subset=[df.columns[0]])  # Drop rows with empty first col
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Drop unnamed columns

        if sheet_name == "Tools":
            # Rename any "Column X" columns to "Link"
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
        Google Open Buildings is a global dataset developed by Google that provides high-resolution building footprints extracted from satellite imagery using advanced machine learning techniques. It covers millions of buildings across many countries, especially focusing on regions where accurate building data was previously unavailable or incomplete.
    
        This dataset is an invaluable resource for urban planners, researchers, governments, and humanitarian organizations. It supports applications such as disaster response, infrastructure planning, population estimation, and sustainable development by providing detailed and up-to-date information on building locations and shapes.
    
        Google Open Buildings is openly available and continues to grow, helping bridge data gaps and enabling data-driven decision-making at scale.
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
    
        st.markdown(
            """
            Dashboard created by Shubh Dhadiwal using Google Earth Engine.
            
            To download the data, click on the Code Editor link below:  
            [🚀 Open Earth Engine Code Editor here](https://code.earthengine.google.com/272ebbc2fd09e86a3b256c9c2f259b9f?hideCode=true)
            """,
            unsafe_allow_html=True,
        )
    
    with st.expander("▶️ Local Climate Zones (LCZ) Dashboard"):
        st.markdown("""
        Local Climate Zones (LCZs), introduced in 2012, provide a standardized classification for urban and rural landscapes at a micro-scale. This classification captures detailed land-cover and physical properties critical for understanding urban climate phenomena such as urban heat islands.

        The global LCZ map shown here has a spatial resolution of 100 meters, representing the nominal year 2018. It is derived from multiple Earth observation datasets combined with expert LCZ class labels. The recommended band for most users is **LCZ_Filter**, which provides the primary classification. Another band, **LCZ**, is available but mainly used internally for calculating the probability layer.

        The LCZ scheme classifies landscapes into 17 classes: 10 representing built environments (urban forms) and 7 representing natural land-cover types. Each LCZ type includes generic numerical descriptions of urban canopy parameters, making this dataset valuable for urban climate modeling and impact assessment.
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

        st.markdown(
            """
            Dashboard created by Shubh Dhadiwal using Google Earth Engine.
            
            To download the LCZ data, open the Earth Engine Code Editor link below:  
            [🚀 Open Earth Engine Code Editor here](https://code.earthengine.google.com/db65e6b4ece8341249a978d4a1509f0e)
            """,
            unsafe_allow_html=True,
        )

    with st.expander("▶️ NASA Sea Level Evaluation Tool"):
        st.markdown("""
        The NASA Sea Level Evaluation Tool provides interactive visualization and analysis of global sea level data, enabling researchers and policymakers to understand rising sea levels and their impacts.
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

    with st.expander("▶️ Global Surface Water Explorer"):
        st.markdown("""
        The **Global Surface Water Explorer** (GSWE), developed by the European Commission's Joint Research Centre, provides high-resolution mapping of global surface water distribution and long-term changes from 1984 to 2021. 

        It utilizes Landsat satellite imagery to analyze water occurrence, seasonality, recurrence, transitions, and maximum extent worldwide. This dataset supports water resource management, climate change studies, biodiversity conservation, and food security.

        **Citation:**  
        Pekel, J.-F., Cottam, A., Gorelick, N., & Belward, A. S. (2016). High-resolution mapping of global surface water and its long-term changes. *Nature*, 540(7633), 418–422. [https://doi.org/10.1038/nature20584](https://doi.org/10.1038/nature20584)

        **Data Access:**  
        Download the data at the [Global Surface Water Explorer Download Page](https://global-surface-water.appspot.com/download)
        """)

        leaflet_html = """
        <div id="map" style="width: 1400px; height: 700px;"></div>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script>
        var map = L.map('map').setView([20, 0], 2);

        var transitions = L.tileLayer('https://storage.googleapis.com/global-surface-water/tiles2021/transitions/{z}/{x}/{y}.png', {
            format: 'image/png',
            maxZoom: 13,
            errorTileUrl: 'https://storage.googleapis.com/global-surface-water/downloads_ancillary/blank.png',
            attribution: '© 2016 EC JRC/Google'
        }).addTo(map);
        </script>
        """

        st.components.v1.html(leaflet_html, height=550)

    with st.expander("▶️ BBBike Extract Service"):
        st.markdown("""
        BBBike Extract is a service to extract OpenStreetMap data for custom-defined areas worldwide. It allows users to select any region and download geospatial data extracts.

        ---

        **Welcome to the BBBike Extract Service!**

        BBBike extracts allows you to extract areas from Planet.osm in OSM, PBF, o5m, Garmin, Organic Maps, Osmand, mapsforge CSV, SVG, libosmium OPL, GeoJSON, SQLite, text, or Esri shapefile format. The maximum area size is 24,000,000 square km, or up to 512MB file size. It takes between 2-7 minutes to extract an area. The email field is required, you will be notified by email if your extract is ready for download. Please use a meaningful name for the extract. For more information, please read the extract help page.

        **How to use the BBBike extract service (YouTube tutorials):**

        1. Now move the map to your desired location.  
        2. Then click the **here** button to create the bounding box.  
        3. Move or resize the bounding box, or add new points to the polygon.  
        4. Select a Format, enter Your email address and Name of area to extract.  
        5. Click the extract button. Wait for email notification and download the map. Done!

        Supported formats include:  
        - Shapefile (Esri)  
        - Garmin OSM  
        - Garmin Leisure  
        - Organic Maps  
        - mapsforge  
        - OsmAnd  
        - SVG

        For a full guide, visit [BBBike Extract Website](https://extract.bbbike.org/).

        ---
        """)

        components.iframe(
            "https://extract.bbbike.org/",
            height=700,
            width=1300,
            scrolling=True
        )

    st.stop()  # Stop execution here for dashboards so no other code runs below

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

# ===== LOAD DATA FOR OTHER TABS INCLUDING FAVORITES ===== #
if selected_tab != "Favorites":
    df = load_data(sheet_options[selected_tab])
else:
    # For favorites, combine favorites from all categories
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

# ===== FAVORITES STORAGE ===== #
if "favorites" not in st.session_state:
    st.session_state.favorites = {}

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

# Initialize favorites in session_state if not present
if "favorites" not in st.session_state:
    st.session_state.favorites = {}

def highlight_search(text, term):
    if not term:
        return text
    regex = re.compile(re.escape(term), re.IGNORECASE)
    return regex.sub(lambda match: f"**:yellow[{match.group(0)}]**", str(text))

view_mode = st.sidebar.radio("View Mode", ["Detailed", "Compact"])

# Debug print to check selected tab value
st.write(f"Selected tab: '{selected_tab}'")

for idx, row in df.iterrows():
    # Handle title and category keys
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

    if view_mode == "Detailed":
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
        # Compact mode ONLY if NOT Favorites tab
        if selected_tab.strip().lower() != "favorites":
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
        else:
            # Favorites tab: no compact view - do nothing or add message if you want
            pass

# Footer
st.markdown("""
<p style='text-align:center; font-size:12px; color:gray;'>
Developed by Shubh | 
<a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a> | 
© Copyright GeoAI Repository
</p>
""", unsafe_allow_html=True)

