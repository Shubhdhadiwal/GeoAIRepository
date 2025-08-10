import streamlit as st
import pandas as pd
import altair as alt
import re
import hashlib
import os
import json
from datetime import datetime
import altair as alt

# ===== PAGE CONFIG ===== #
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

st.sidebar.title(f"Welcome, {st.session_state['username']}!")

sheet_options = {
    "About": "About",
    "Data Sources": "Data Sources",
    "Tools": "Tools",
    "Free Tutorials": "Free Tutorials",
    "Python Codes (GEE)": "Google Earth EnginePython Codes",  # fixed spacing here
    "Courses": "Courses",
    "Submit New Resource": "Submit New Resource",
    "Favorites": "Favorites",
    "FAQ": "FAQ",
    "Dashboards": "Dashboards"
}

@st.cache_data(show_spinner=False)
def load_data(sheet_name):
    try:
        df = pd.read_excel(GITHUB_RAW_URL, sheet_name=sheet_name)
        df.columns = df.iloc[0]  # Use first row as header
        df = df[1:]
        df = df.dropna(subset=[df.columns[0]])
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        if sheet_name == "Tools":
            new_columns = {}
            for col in df.columns:
                if isinstance(col, str) and col.startswith("Column"):
                    new_columns[col] = "Link"
            if new_columns:
                df = df.rename(columns=new_columns)
        return df
    except Exception as e:
        st.error(f"Error loading sheet '{sheet_name}': {e}")
        return pd.DataFrame()

if "favorites" not in st.session_state:
    st.session_state.favorites = {}

st.sidebar.header("🧭 GeoAI Repository")
selected_tab = st.sidebar.radio("Select Section", list(sheet_options.keys()))

st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 GeoAI Repository")

# Simple CC license text with link
st.sidebar.markdown(
    """
    Licensed under the  
    [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
    """,
    unsafe_allow_html=True
)

# ---- Visitor counter functions ----
COUNTER_FILE = "visitor_count.json"

def load_counter():
    if not os.path.exists(COUNTER_FILE):
        return {"total": 0, "daily": {}}
    with open(COUNTER_FILE, "r") as f:
        return json.load(f)

def save_counter(counter_data):
    with open(COUNTER_FILE, "w") as f:
        json.dump(counter_data, f)

def increment_visitor_count():
    today = datetime.now().strftime("%Y-%m-%d")
    counter = load_counter()

    counter["total"] = counter.get("total", 0) + 1
    counter["daily"][today] = counter["daily"].get(today, 0) + 1

    save_counter(counter)
    return counter["total"], counter["daily"][today]

def get_visitor_counts():
    today = datetime.now().strftime("%Y-%m-%d")
    counter = load_counter()
    total = counter.get("total", 0)
    today_count = counter["daily"].get(today, 0)
    return total, today_count

# ---- After user login ----
if st.session_state.get('authenticated', False):
    if 'visitor_incremented' not in st.session_state:
        total_visitors, today_visitors = increment_visitor_count()
        st.session_state.visitor_incremented = True
    else:
        total_visitors, today_visitors = get_visitor_counts()

    st.sidebar.markdown(f"👥 **Total Visitors:** {total_visitors}")
    st.sidebar.markdown(f"📅 **Today's Visitors:** {today_visitors}")

# ---- Static tabs handling ----

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
    cols = st.columns(len(categories_to_check))
    for i, cat in enumerate(categories_to_check):
        cols[i].metric(label=cat, value=counts.get(cat, 0))
    st.markdown("---")
    st.markdown("""
    <p style='text-align:center; font-size:12px; color:gray;'>
    Developed by Shubh | 
    <a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a>
    </p>
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
        "Who developed this repository?": "This repository is developed and maintained by Shubh Dhadiwal."
    }
    for question, answer in faqs.items():
        with st.expander(question):
            st.write(answer)
    st.stop()

if selected_tab == "Dashboards":
    st.title("🏙️Dashboards")

    # Clickable expander for the dashboard info and links
    with st.expander("▶️ Google Open Building Dashboard"):
        st.markdown("""
        Google Open Buildings is a global dataset developed by Google that provides high-resolution building footprints extracted from satellite imagery using advanced machine learning techniques. It covers millions of buildings across many countries, especially focusing on regions where accurate building data was previously unavailable or incomplete.

        This dataset is an invaluable resource for urban planners, researchers, governments, and humanitarian organizations. It supports applications such as disaster response, infrastructure planning, population estimation, and sustainable development by providing detailed and up-to-date information on building locations and shapes.

        Google Open Buildings is openly available and continues to grow, helping bridge data gaps and enabling data-driven decision-making at scale.
        """)

        st.markdown("🔗 [Official Dataset Documentation](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_Research_open-buildings_v3_polygons)")

        st.markdown("---")

        # Embedded GEE app iframe
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
    st.stop()

import streamlit as st
import requests
import pandas as pd
import altair as alt

import streamlit as st
import requests
import pandas as pd
import altair as alt

if selected_tab == "Dashboards":
    st.title("🌊 Sea Level Global Dashboard")

    with st.expander("▶️ Sea Level Global Dataset Overview"):
        st.markdown("""
        The Sea Level Global dataset provides global-scale sea level rise projections and observations, crucial for understanding climate change impacts on coastal regions. 
        This dataset supports research, policymaking, and urban planning to build resilient coastal infrastructure and adapt to rising seas.

        The dataset is accessible via an API and can be visualized through interactive dashboards.
        """)

        st.markdown("🔗 [Dataset API Source](https://d3qt3aobtsas2h.cloudfront.net/edge/ws/search/sealevelgovglobal?type=global)")

        try:
            response = requests.get("https://d3qt3aobtsas2h.cloudfront.net/edge/ws/search/sealevelgovglobal?type=global")
            response.raise_for_status()
            data_json = response.json()

            records = data_json.get("data", [])

            if records:
                df = pd.DataFrame(records)
                # Ensure columns for plotting exist:
                if "year" in df.columns and "sea_level_mm" in df.columns:
                    chart = alt.Chart(df).mark_line(point=True).encode(
                        x='year:O',
                        y='sea_level_mm:Q',
                        tooltip=['year', 'sea_level_mm']
                    ).properties(
                        width=700,
                        height=400,
                        title="Global Sea Level Rise Over Years (mm)"
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.write("Expected columns 'year' and 'sea_level_mm' not found in the dataset. Here's the raw data:")
                    st.write(df)
            else:
                st.write("No data found in the API response.")
        except Exception as e:
            st.error(f"Failed to load data: {e}")

        st.markdown("---")

        st.markdown(
            """
            Dashboard created by Shubh Dhadiwal using the Sea Level Global API data.

            To explore or download raw data, visit the API link above.
            """
        )
    st.stop()

   # For other tabs with data

title_map = {
    "Data Sources": "Data Source",
    "Tools": "Tools",
    "Courses": "Tutorials",
    "Python Codes (GEE)": "Title",
    "Free Tutorials": "Tutorials",
    "Favorites": "Title"
}

if selected_tab != "Favorites":
    with st.spinner(f"Loading {selected_tab} data..."):
        df = load_data(sheet_options[selected_tab])
else:
    all_fav_items = []
    for key, items in st.session_state.favorites.items():
        df_cat = load_data(sheet_options.get(key, key))
        if df_cat.empty:
            continue
        fav_rows = df_cat.loc[df_cat.index.isin(items)].copy()
        fav_rows["Category"] = key
        title_col_fav = title_map.get(key, df_cat.columns[0])
        fav_rows["Fav_Title"] = fav_rows[title_col_fav]
        all_fav_items.append(fav_rows)
    if all_fav_items:
        df = pd.concat(all_fav_items)
    else:
        df = pd.DataFrame()

if selected_tab == "Favorites":
    title_col = "Fav_Title"
else:
    title_col = title_map.get(selected_tab, df.columns[0] if not df.empty else None)

# Search and sorting controls

search_term = st.sidebar.text_input("🔍 Search")
sort_order = st.sidebar.selectbox("Sort by Title", ["Ascending", "Descending"])

if selected_tab not in ["Favorites", "About", "Submit New Resource", "FAQ"]:
    if search_term:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]
    if title_col in df.columns:
        df = df.sort_values(by=title_col, ascending=(sort_order == "Ascending"))

if selected_tab == "Favorites":
    if st.sidebar.button("Clear All Favorites"):
        st.session_state.favorites = {}
        st.experimental_rerun()

st.title(f"🌍 GeoAI Repository – {selected_tab}")

if df.empty:
    st.info("No resources to display.")
    st.stop()

view_mode = st.sidebar.radio("View Mode", ["Detailed", "Compact"])

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

st.markdown("""
<p style='text-align:center; font-size:12px; color:gray;'>
Developed by Shubh | 
<a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a> | 
<a href='https://creativecommons.org/licenses/by-nc/4.0/' target='_blank'>
  <img src='https://mirrors.creativecommons.org/presskit/icons/by-nc/88x31.png' alt='Creative Commons License' style='vertical-align:middle;'/>
  Creative Commons BY-NC 4.0 License
</a>
</p>
""", unsafe_allow_html=True)

