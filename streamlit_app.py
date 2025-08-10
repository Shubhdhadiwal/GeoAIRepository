import streamlit as st
import pandas as pd
import hashlib
import re

# ===== PAGE CONFIG =====
st.set_page_config(page_title="GeoAI Repository", layout="wide")

# GitHub raw Excel file URL
GITHUB_RAW_URL = "https://github.com/Shubhdhadiwal/GeoAIRepository/raw/main/Geospatial%20Data%20Repository%20(2).xlsx"

# Utility to hash password string
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Store username and hashed password
USER_CREDENTIALS = {
    "Shubh4016": hash_password("Shubh9834421314")
}

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['username'] = None

def login():
    st.title("🔐 Login to GeoAI Repository")
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
    st.experimental_rerun()

st.sidebar.title(f"Welcome, {st.session_state['username']}!")

# Sheet options mapping tab name → Excel sheet name (except Dashboards etc. which don't have sheets)
sheet_options = {
    "About": "About",
    "Data Sources": "Data Sources",
    "Tools": "Tools",
    "Free Tutorials": "Free Tutorials",
    "Python Codes (GEE)": "Google Earth EnginePython Codes",
    "Courses": "Courses",
    "Submit New Resource": "Submit New Resource",
    "Favorites": "Favorites",
    "Dashboards": "Dashboards",  # note: no sheet actually called "Dashboards"
    "FAQ": "FAQ"
}

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
    st.stop()  # Important: stop here so no Excel loading attempted

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

def highlight_search(text, term):
    if not term:
        return text
    regex = re.compile(re.escape(term), re.IGNORECASE)
    return regex.sub(lambda match: f"**:yellow[{match.group(0)}]**", str(text))

view_mode = st.sidebar.radio("View Mode", ["Detailed", "Compact"])

for idx, row in df.iterrows():
    resource_title = row.get(title_col)
    if not resource_title or str(resource_title).strip() == "":
        resource_title = f"Resource-{idx+1}"
    displayed_title = highlight_search(resource_title, search_term)

    links = []
    for col in possible_links:
        if col in df.columns and pd.notna(row.get(col)):
            val = str(row[col]).strip()
            if val.lower().startswith(("http://", "https://", "www.")):
                links.append((col, val))

    category_key = selected_tab
    if selected_tab == "Favorites" and "Category" in row:
        category_key = row["Category"]
    is_fav = st.session_state.favorites.get(category_key, [])
    checked = idx in is_fav

    if view_mode == "Detailed":
        with st.expander(f"🔹 {displayed_title}", expanded=False):
            col1, col2 = st.columns([0.9, 0.1])
            with col2:
                fav_checkbox = st.checkbox("⭐", value=checked, key=f"{category_key}_{idx}")
            with col1:
                if "Description" in df.columns and pd.notna(row.get("Description")):
                    st.write(highlight_search(row["Description"], search_term))
                for link_name, link_url in links:
                    st.markdown(f"[🔗 {link_name}]({link_url})", unsafe_allow_html=True)
                if "Purpose" in df.columns and pd.notna(row.get("Purpose")):
                    st.markdown(f"**🎯 Purpose:** {highlight_search(row['Purpose'], search_term)}")
                for col in df.columns:
                    if col not in exclude_cols and col not in possible_links and pd.notna(row.get(col)):
                        st.markdown(f"**{col}:** {highlight_search(row[col], search_term)}")
            if fav_checkbox and idx not in st.session_state.favorites.get(category_key, []):
                st.session_state.favorites.setdefault(category_key, []).append(idx)
            elif not fav_checkbox and idx in st.session_state.favorites.get(category_key, []):
                st.session_state.favorites[category_key].remove(idx)
    else:
        compact_col1, compact_col2, compact_col3 = st.columns([6, 3, 1])
        with compact_col1:
            st.markdown(f"🔹 {displayed_title}")
        with compact_col2:
            if links:
                for link_name, link_url in links:
                    st.markdown(f"[🔗 {link_name}]({link_url})", unsafe_allow_html=True)
        with compact_col3:
            fav_checkbox = st.checkbox("⭐", value=checked, key=f"compact_{category_key}_{idx}")
            if fav_checkbox and idx not in st.session_state.favorites.get(category_key, []):
                st.session_state.favorites.setdefault(category_key, []).append(idx)
            elif not fav_checkbox and idx in st.session_state.favorites.get(category_key, []):
                st.session_state.favorites[category_key].remove(idx)

if selected_tab == "Favorites":
    if st.sidebar.button("Clear All Favorites"):
        st.session_state.favorites = {}
        st.experimental_rerun()

st.markdown("""
<p style='text-align:center; font-size:12px; color:gray;'>
Developed by Shubh | 
<a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a> | 
© Copyright GeoAI Repository
</p>
""", unsafe_allow_html=True)
