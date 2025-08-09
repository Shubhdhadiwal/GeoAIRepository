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
def load_data(sheet_name):
    try:
        df = pd.read_excel("Geospatial Data Repository (2).xlsx", sheet_name=sheet_name)
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

# Search term input
search_term = st.sidebar.text_input("🔍 Search")

# Add sorting option
sort_order = st.sidebar.selectbox("Sort by Title", ["Ascending", "Descending"])

# Dynamic filters for categorical columns
def get_categorical_columns(df):
    cat_cols = []
    for col in df.columns:
        if df[col].dtype == 'object' and df[col].nunique() < 30:
            cat_cols.append(col)
    return cat_cols

if selected_tab not in ["Favorites", "About", "Submit New Resource", "FAQ"]:
    # Apply search filter
    if search_term:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]
    
    # Dynamic filters
    cat_cols = get_categorical_columns(df)
    for col in cat_cols:
        options = sorted(df[col].dropna().unique())
        selected_options = st.sidebar.multiselect(f"Filter by {col}", options, default=options)
        if selected_options:
            df = df[df[col].isin(selected_options)]
    
    # Sort dataframe
    if title_col in df.columns:
        df = df.sort_values(by=title_col, ascending=(sort_order == "Ascending"))

if selected_tab == "Favorites":
    # Clear all favorites button
    if st.sidebar.button("Clear All Favorites"):
        st.session_state.favorites = {}
        st.experimental_rerun()

st.title(f"🌍 GeoAI Repository – {selected_tab}")

if df.empty:
    st.info("No resources to display.")
    st.stop()

# Toggle between compact and detailed view
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
    
    # Highlight search term in title
    displayed_title = highlight_search(resource_title, search_term)

    # Collect all valid links
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
            # Update favorites
            if fav_checkbox and idx not in st.session_state.favorites.get(category_key, []):
                st.session_state.favorites.setdefault(category_key, []).append(idx)
            elif not fav_checkbox and idx in st.session_state.favorites.get(category_key, []):
                st.session_state.favorites[category_key].remove(idx)
    else:
        # Compact view: single line with title + first link + favorite star
        compact_col1, compact_col2, compact_col3 = st.columns([6, 3, 1])
        with compact_col1:
            st.markdown(f"🔹 {displayed_title}")
        with compact_col2:
            if links:
                # Show all links as clickable badges/buttons
                for link_name, link_url in links:
                    st.markdown(f"[🔗 {link_name}]({link_url})", unsafe_allow_html=True)
        with compact_col3:
            fav_checkbox = st.checkbox("⭐", value=checked, key=f"compact_{category_key}_{idx}")
            if fav_checkbox and idx not in st.session_state.favorites.get(category_key, []):
                st.session_state.favorites.setdefault(category_key, []).append(idx)
            elif not fav_checkbox and idx in st.session_state.favorites.get(category_key, []):
                st.session_state.favorites[category_key].remove(idx)

st.markdown("<hr style='border:1px solid #ddd'/>", unsafe_allow_html=True)
st.caption("📘 Powered by Streamlit | © 2025 GeoAI Repository")
st.markdown("""
<p style='text-align:center; font-size:12px; color:gray;'>
Developed by Shubh | 
<a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a>
</p>
""", unsafe_allow_html=True)
