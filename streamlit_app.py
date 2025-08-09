import streamlit as st
import pandas as pd
import altair as alt
import re

# ===== PAGE CONFIG ===== #
st.set_page_config(page_title="GeoAI Repository", layout="wide")

sheet_options = {
    "About": "About",
    "Data Sources": "Data Sources",
    "Tools": "Tools",
    "Free Tutorials": "Free Tutorials",
    "Python Codes (GEE)": "Google Earth EnginePython Codes",
    "Courses": "Courses",
    "Submit New Resource": "Submit New Resource",
    "Favorites": "Favorites",
    "FAQ": "FAQ"
}

@st.cache_data(show_spinner=False)
def load_data(sheet_name: str) -> pd.DataFrame:
    """Load Excel sheet into a cleaned pandas DataFrame."""
    try:
        df = pd.read_excel("Geospatial Data Repository (2).xlsx", sheet_name=sheet_name)
        df.columns = df.iloc[0]
        df = df[1:].dropna(subset=[df.columns[0]])
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        
        # Rename ambiguous tool columns to "Link"
        if sheet_name == "Tools":
            df.rename(columns={col: "Link" for col in df.columns if isinstance(col, str) and col.startswith("Column")}, inplace=True)
        
        return df
    except FileNotFoundError:
        st.error("❌ Data file not found. Please make sure the Excel file exists in the working directory.")
    except Exception as e:
        st.error(f"Error loading sheet '{sheet_name}': {e}")
    return pd.DataFrame()

if "favorites" not in st.session_state:
    st.session_state.favorites = {}

st.sidebar.header("🧭 GeoAI Repository")
selected_tab = st.sidebar.radio("Select Section", list(sheet_options.keys()))
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 GeoAI Repository")

# ===== STATIC PAGES ===== #
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
    counts = {cat: len(load_data(sheet_options[cat])) for cat in categories_to_check}
    
    st.subheader("📊 Repository Content Overview")
    cols = st.columns(len(categories_to_check))
    for i, cat in enumerate(categories_to_check):
        cols[i].metric(label=cat, value=counts.get(cat, 0))
    
    st.markdown("<hr>", unsafe_allow_html=True)
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
    st.markdown("[Submit via Google Form](https://forms.gle/FZZpvr4xQyon5nDs6)")
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
    for q, a in faqs.items():
        with st.expander(q):
            st.write(a)
    st.stop()

# ===== TITLE COLUMN MAP ===== #
title_map = {
    "Data Sources": "Data Source",
    "Tools": "Tools",
    "Courses": "Tutorials",
    "Python Codes (GEE)": "Title",
    "Free Tutorials": "Tutorials",
    "Favorites": "Title"
}

# ===== LOAD DATA ===== #
if selected_tab != "Favorites":
    with st.spinner(f"Loading {selected_tab} data..."):
        df = load_data(sheet_options[selected_tab])
else:
    fav_items = []
    for key, items in st.session_state.favorites.items():
        df_cat = load_data(sheet_options.get(key, key))
        if not df_cat.empty:
            fav_rows = df_cat.loc[df_cat.index.isin(items)].copy()
            fav_rows["Category"] = key
            fav_rows["Fav_Title"] = fav_rows[title_map.get(key, df_cat.columns[0])]
            fav_items.append(fav_rows)
    df = pd.concat(fav_items) if fav_items else pd.DataFrame()

title_col = "Fav_Title" if selected_tab == "Favorites" else title_map.get(selected_tab, df.columns[0] if not df.empty else None)

# ===== SEARCH, SORT, FILTER ===== #
search_term = st.sidebar.text_input("🔍 Search")
sort_order = st.sidebar.selectbox("Sort by Title", ["Ascending", "Descending"])

@st.cache_data
def get_categorical_columns(df: pd.DataFrame):
    return [col for col in df.columns if df[col].dtype == "object" and df[col].nunique() < 30]

if selected_tab not in ["Favorites", "About", "Submit New Resource", "FAQ"]:
    if search_term:
        terms = search_term.split()
        df = df[df.apply(lambda r: all(any(re.search(t, str(v), re.IGNORECASE) for v in r) for t in terms), axis=1)]
    
    for col in get_categorical_columns(df):
        opts = sorted(df[col].dropna().unique())
        sel_opts = st.sidebar.multiselect(f"Filter by {col}", opts, default=opts)
        df = df[df[col].isin(sel_opts)]
    
    if title_col in df.columns:
        df = df.sort_values(by=title_col, ascending=(sort_order == "Ascending"))

if selected_tab == "Favorites" and st.sidebar.button("Clear All Favorites"):
    st.session_state.favorites = {}
    st.experimental_rerun()

st.title(f"🌍 GeoAI Repository – {selected_tab}")

if df.empty:
    st.info("No resources to display.")
    st.stop()

# ===== DISPLAY VIEW ===== #
view_mode = st.sidebar.radio("View Mode", ["Detailed", "Compact"])
exclude_cols = [title_col, "Description", "Purpose", "S.No", "Category"]

link_columns = ["Links", "Link", "Link to the codes", "Tool Link", "Course Link", "Tutorial Link"]

def highlight_search(text, term):
    if not term:
        return str(text)
    pattern = "|".join(re.escape(t) for t in term.split())
    return re.sub(pattern, lambda m: f"**:yellow[{m.group(0)}]**", str(text), flags=re.IGNORECASE)

for idx, row in df.iterrows():
    resource_title = row.get(title_col) or f"Resource-{idx+1}"
    displayed_title = highlight_search(resource_title, search_term)
    links = [(col, row[col]) for col in link_columns if col in df.columns and pd.notna(row[col]) and str(row[col]).startswith(("http", "www"))]
    
    category_key = row.get("Category", selected_tab)
    is_fav_list = st.session_state.favorites.get(category_key, [])
    fav_state = idx in is_fav_list
    
    if view_mode == "Detailed":
        with st.expander(f"🔹 {displayed_title}", expanded=False):
            fav_checkbox = st.checkbox("⭐", value=fav_state, key=f"{category_key}_{idx}")
            if "Description" in df.columns and pd.notna(row["Description"]):
                st.write(highlight_search(row["Description"], search_term))
            for name, url in links:
                st.markdown(f"[🔗 {name}]({url})")
            if "Purpose" in df.columns and pd.notna(row["Purpose"]):
                st.markdown(f"**🎯 Purpose:** {highlight_search(row['Purpose'], search_term)}")
            for col in df.columns:
                if col not in exclude_cols + link_columns and pd.notna(row[col]):
                    st.markdown(f"**{col}:** {highlight_search(row[col], search_term)}")
    else:
        col1, col2, col3 = st.columns([6, 3, 1])
        col1.markdown(f"🔹 {displayed_title}")
        for name, url in links:
            col2.markdown(f"[🔗 {name}]({url})")
        fav_checkbox = col3.checkbox("⭐", value=fav_state, key=f"compact_{category_key}_{idx}")
    
    # Update favorites
    if fav_checkbox and idx not in is_fav_list:
        st.session_state.favorites.setdefault(category_key, []).append(idx)
    elif not fav_checkbox and idx in is_fav_list:
        st.session_state.favorites[category_key].remove(idx)

st.markdown("<hr>", unsafe_allow_html=True)
st.caption("📘 Powered by Streamlit | © 2025 GeoAI Repository")
