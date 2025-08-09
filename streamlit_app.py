import streamlit as st
import pandas as pd
import altair as alt

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
    "Favorites": "Favorites",  # Added Favorites tab
    "FAQ": "FAQ"               # Added FAQ tab
}

# ===== LOAD DATA ===== #
@st.cache_data(show_spinner=False)
def load_data(sheet_name):
    try:
        df = pd.read_excel("Geospatial Data Repository (2).xlsx", sheet_name=sheet_name)
        df.columns = df.iloc[0]  # Use first row as header
        df = df[1:]  # Skip header row from data
        df = df.dropna(subset=[df.columns[0]])  # Ensure first column is not empty
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Drop unnamed columns

        # Fix: Rename any "Column X" column to "Link" if sheet is Tools
        if sheet_name == "Tools":
            # Find columns named like "Column 10", "Column 9", etc. and rename to "Link"
            new_columns = {}
            for col in df.columns:
                if isinstance(col, str) and col.startswith("Column"):
                    new_columns[col] = "Link"
            if new_columns:
                df = df.rename(columns=new_columns)

        return df
    except Exception as e:
        st.error(f"Error loading sheet '{sheet_name}': {e}")
        return pd.DataFrame()  # return empty dataframe on error

# ===== INITIALIZE FAVORITES IN SESSION STATE ===== #
if "favorites" not in st.session_state:
    st.session_state.favorites = {}

# ===== SIDEBAR NAV ===== #
st.sidebar.header("🧭 GeoAI Repository")
selected_tab = st.sidebar.radio("Select Section", list(sheet_options.keys()))

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 GeoAI Repository")

# ===== ABOUT PAGE ===== #
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
    st.markdown("""
    <p style='text-align:center; font-size:12px; color:gray;'>
    Developed by Shubh | 
    <a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a>
    </p>
    """, unsafe_allow_html=True)
    st.stop()

# ===== SUBMIT NEW RESOURCE ===== #
if selected_tab == "Submit New Resource":
    st.title("📤 Submit a New Resource")
    st.markdown("Help us grow this repository by contributing useful links and resources.")
    google_form_url = "https://forms.gle/FZZpvr4xQyon5nDs6"
    st.markdown(f"You can submit your resource using [this Google Form]({google_form_url}).")
    st.stop()

# ===== FAQ SECTION ===== #
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

# ===== INTERACTIVE SEARCH & FILTER ===== #
search_term = st.sidebar.text_input("🔍 Search")
if selected_tab not in ["Favorites", "About", "Submit New Resource", "FAQ"] and search_term:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]

if selected_tab == "Data Sources" and "Type" in df.columns:
    type_filter = st.sidebar.multiselect("📂 Filter by Type", sorted(df["Type"].dropna().unique()))
    if type_filter:
        df = df[df["Type"].isin(type_filter)]

# ===== TITLE MAPPING ===== #
title_map = {
    "Data Sources": "Data Source",
    "Tools": "Tools",
    "Courses": "Tutorials",
    "Python Codes (GEE)": "Title",
    "Free Tutorials": "Tutorials",
    "Favorites": "Title"
}
title_col = title_map.get(selected_tab, df.columns[0] if not df.empty else None)

# ===== MAIN TITLE ===== #
st.title(f"🌍 GeoAI Repository – {selected_tab}")

if df.empty:
    st.info("No resources to display.")
    st.stop()

# ===== SHOW CARD VIEW WITH FAVORITE BUTTONS ===== #
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

for idx, row in df.iterrows():
    resource_title = row.get(title_col)
    if not resource_title or str(resource_title).strip() == "":
        resource_title = f"Resource-{idx+1}"

    # Find first valid link column for this row
    link_val = None
    for col in possible_links:
        if col in df.columns and pd.notna(row.get(col)):
            val = str(row[col]).strip()
            if val.lower().startswith(("http://", "https://", "www.")):
                link_val = val
                break

    # Determine category key for favorites
    category_key = selected_tab
    if selected_tab == "Favorites" and "Category" in row:
        category_key = row["Category"]
    is_fav = st.session_state.favorites.get(category_key, [])
    checked = idx in is_fav

    with st.expander(f"🔹 {resource_title}"):
        col1, col2 = st.columns([0.9, 0.1])
        with col2:
            fav_checkbox = st.checkbox("⭐", value=checked, key=f"{category_key}_{idx}")
        with col1:
            if "Description" in df.columns and pd.notna(row.get("Description")):
                st.write(row["Description"])

            if link_val:
                st.markdown(f"[🔗 Access Resource]({link_val})", unsafe_allow_html=True)

            if "Purpose" in df.columns and pd.notna(row.get("Purpose")):
                st.markdown(f"**🎯 Purpose:** {row['Purpose']}")

            for col in df.columns:
                if col not in exclude_cols + ([link_val] if link_val else []) and pd.notna(row.get(col)):
                    if col not in possible_links:
                        st.markdown(f"**{col}:** {row[col]}")

        # Update favorites based on checkbox toggle
        if fav_checkbox and idx not in st.session_state.favorites.get(category_key, []):
            st.session_state.favorites.setdefault(category_key, []).append(idx)
        elif not fav_checkbox and idx in st.session_state.favorites.get(category_key, []):
            st.session_state.favorites[category_key].remove(idx)

# ===== FOOTER ===== #
st.markdown("<hr style='border:1px solid #ddd'/>", unsafe_allow_html=True)
st.caption("📘 Powered by Streamlit | © 2025 GeoAI Repository")
st.markdown("""
<p style='text-align:center; font-size:12px; color:gray;'>
Developed by Shubh | 
<a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a>
</p>
""", unsafe_allow_html=True)
