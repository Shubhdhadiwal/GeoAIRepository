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
    "Submit New Resource": "Submit New Resource"
}

# ===== LOAD DATA ===== #
def load_data(sheet_name):
    try:
        df = pd.read_excel("Geospatial Data Repository (2).xlsx", sheet_name=sheet_name)
        df.columns = df.iloc[0]  # Use first row as header
        df = df[1:]  # Skip header row from data
        df = df.dropna(subset=[df.columns[0]])  # Ensure first column is not empty
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Drop unnamed columns
        return df
    except Exception as e:
        st.error(f"Error loading sheet '{sheet_name}': {e}")
        return pd.DataFrame()  # return empty dataframe on error

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

    # Convert counts dict to DataFrame for plotting
    counts_df = pd.DataFrame(list(counts.items()), columns=["Category", "Count"])

    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Data Sources", counts.get("Data Sources", 0))
    col2.metric("Tools", counts.get("Tools", 0))
    col3.metric("Courses", counts.get("Courses", 0))
    col4.metric("Free Tutorials", counts.get("Free Tutorials", 0))
    col5.metric("Python Codes", counts.get("Python Codes (GEE)", 0))

    st.markdown("---")
    st.subheader("📊 Repository Content Overview")

    # Bar chart
    st.bar_chart(data=counts_df.set_index("Category"))

    # Pie chart with Altair
    pie_chart = alt.Chart(counts_df).mark_arc().encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Category", type="nominal"),
        tooltip=["Category", "Count"]
    ).properties(width=400, height=400)
    st.altair_chart(pie_chart)

    st.markdown("""
    ---
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
    if st.button("Open Google Submission Form"):
        st.markdown(f"[Click here to submit your resource]({google_form_url})", unsafe_allow_html=True)
    else:
        st.markdown(f"Or you can submit your resource using [this Google Form]({google_form_url})")
    st.stop()

# ===== LOAD DATA FOR OTHER TABS ===== #
df = load_data(sheet_options[selected_tab])

# ===== INTERACTIVE SEARCH & FILTER ===== #
search_term = st.sidebar.text_input("🔍 Search")
if search_term:
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
    "Free Tutorials": "Tutorials"
}
title_col = title_map.get(selected_tab, df.columns[0])

# ===== MAIN TITLE ===== #
st.title(f"🌍 GeoAI Repository – {selected_tab}")

# ===== SHOW CARD VIEW ONLY ===== #
exclude_cols = [title_col, "Description", "Purpose", "S.No"]  # Add more if needed

link_columns_map = {
    "Data Sources": ["Links", "Link"],
    "Tools": ["Tool Link", "Link", "Links"],
    "Courses": ["Course Link", "Link", "Links"],
    "Free Tutorials": ["Link", "Links", "Tutorial Link"],
    "Python Codes (GEE)": ["Link", "Links", "Link to the codes"]
}

possible_links = link_columns_map.get(selected_tab, ["Links", "Link", "Link to the codes"])
link_col = next((c for c in possible_links if c in df.columns), None)

for idx, row in df.iterrows():
    resource_title = row.get(title_col)
    if not resource_title or str(resource_title).strip() == "":
        resource_title = f"Resource-{idx+1}"

    with st.expander(f"🔹 {resource_title}"):
        if "Description" in df.columns and pd.notna(row.get("Description")):
            st.write(row["Description"])

        if link_col and pd.notna(row.get(link_col)):
            st.markdown(f"[🔗 Access Resource]({row[link_col]})", unsafe_allow_html=True)

        if "Purpose" in df.columns and pd.notna(row.get("Purpose")):
            st.markdown(f"**🎯 Purpose:** {row['Purpose']}")

        for col in df.columns:
            if col not in exclude_cols + ([link_col] if link_col else []) and pd.notna(row.get(col)):
                st.markdown(f"**{col}:** {row[col]}")

# ===== FOOTER ===== #
st.markdown("<hr style='border:1px solid #ddd'/>", unsafe_allow_html=True)
st.caption("📘 Powered by Streamlit | © 2025 GeoAI Repository")
st.markdown("""
<p style='text-align:center; font-size:12px; color:gray;'>
Developed by Shubh | 
<a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a>
</p>
""", unsafe_allow_html=True)
