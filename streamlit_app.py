import streamlit as st
import pandas as pd

# ===== PAGE CONFIG ===== #
st.set_page_config(page_title="GeoAI Repository", layout="wide")

# ===== SIDEBAR OPTIONS ===== #
sheet_options = {
    "About": "About",
    "Data Sources": "Data Sources",
    "Tools": "Tools",
    "Free Tutorials": "Free Tutorials",
    "Python Codes (GEE)": "Google Earth EnginePython Codes",
    "Courses": "Courses",
    "Submit New Resource": "Submit New Resource",
    "Favorites": None,
    "FAQ & Help": None
}

# ===== INIT SESSION STATE ===== #
if "favorites" not in st.session_state:
    st.session_state.favorites = {}
if "faq_questions" not in st.session_state:
    st.session_state.faq_questions = [
        {"q": "What is GeoAI Repository?", "a": "It is a free resource hub for geospatial analytics, machine learning, and urban/climate planning."},
        {"q": "How to submit a new resource?", "a": "Use the Submit New Resource tab or the Google Form linked there."},
        {"q": "Can I favorite resources?", "a": "Yes! Use the star buttons to favorite/unfavorite and view them in the Favorites tab."}
    ]

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
    if st.button("Open Google Submission Form"):
        st.markdown(f"[Click here to submit your resource]({google_form_url})", unsafe_allow_html=True)
    else:
        st.markdown(f"Or you can submit your resource using [this Google Form]({google_form_url})")
    st.stop()

# ===== FAVORITES PAGE ===== #
if selected_tab == "Favorites":
    st.title("⭐ Your Favorite Resources")
    if not st.session_state.favorites:
        st.info("You have not favorited any resources yet.")
    else:
        from collections import defaultdict
        fav_by_cat = defaultdict(list)
        for fav in st.session_state.favorites.values():
            fav_by_cat[fav["category"]].append(fav)

        for cat, items in fav_by_cat.items():
            st.subheader(cat)
            for item in items:
                if item["link"]:
                    st.markdown(f"- [{item['title']}]({item['link']})")
                else:
                    st.markdown(f"- {item['title']}")
    st.stop()

# ===== FAQ & HELP ===== #
if selected_tab == "FAQ & Help":
    st.title("❓ FAQ & Help")

    st.subheader("Frequently Asked Questions")
    for faq in st.session_state.faq_questions:
        with st.expander(faq["q"]):
            st.write(faq["a"])

    st.markdown("---")
    st.subheader("Submit a Question or Suggestion")
    new_question = st.text_area("Your Question or Suggestion", key="faq_input")
    if st.button("Submit Question"):
        if new_question.strip() != "":
            st.session_state.faq_questions.append({"q": new_question.strip(), "a": "Awaiting answer..."})
            st.success("Thanks! Your question has been added.")
            st.experimental_rerun()
    st.stop()

# ===== LOAD DATA FOR OTHER TABS ===== #
if selected_tab in sheet_options and sheet_options[selected_tab]:
    df = load_data(sheet_options[selected_tab])
else:
    df = pd.DataFrame()

# ===== INTERACTIVE SEARCH & FILTER ===== #
search_term = st.sidebar.text_input("🔍 Search")
if search_term and not df.empty:
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
title_col = title_map.get(selected_tab, df.columns[0] if not df.empty else None)

# ===== FUNCTION TO TOGGLE FAVORITE ===== #
def toggle_favorite(res_id, resource_title, selected_tab, link):
    if res_id in st.session_state.favorites:
        st.session_state.favorites.pop(res_id)
    else:
        st.session_state.favorites[res_id] = {
            "title": resource_title,
            "category": selected_tab,
            "link": link
        }
    st.experimental_rerun()

# ===== HELPER FUNCTION TO EMBED URL ===== #
def embed_resource(url):
    if not url or not isinstance(url, str):
        return
    # Support YouTube embeds
    if "youtube.com/watch" in url or "youtu.be/" in url:
        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
        else:
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            query = urllib.parse.parse_qs(parsed.query)
            video_id = query.get("v", [""])[0]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        st.video(embed_url)
    # Support generic iframe embed for other URLs (if allowed)
    else:
        # Basic iframe embed (width and height can be adjusted)
        iframe_code = f"""
        <iframe src="{url}" width="700" height="400" frameborder="0" allowfullscreen></iframe>
        """
        st.markdown(iframe_code, unsafe_allow_html=True)

# ===== MAIN TITLE & RESOURCE DISPLAY ===== #
if selected_tab not in ["Favorites", "Submit New Resource", "About", "FAQ & Help"]:
    st.title(f"🌍 GeoAI Repository – {selected_tab}")

    if not df.empty:
        exclude_cols = [title_col, "Description", "Purpose", "S.No"]

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

                # Embed the resource link (if possible)
                if link_col and pd.notna(row.get(link_col)):
                    embed_resource(row[link_col])

                # Favorite toggle button
                res_id = f"{selected_tab}_{idx}"
                is_fav = res_id in st.session_state.favorites
                col1, col2 = st.columns([1, 5])
                with col1:
                    if is_fav:
                        if st.button("⭐ Unfavorite", key=f"fav_{res_id}"):
                            toggle_favorite(res_id, resource_title, selected_tab, row[link_col] if link_col and pd.notna(row.get(link_col)) else None)
                    else:
                        if st.button("☆ Favorite", key=f"fav_{res_id}"):
                            toggle_favorite(res_id, resource_title, selected_tab, row[link_col] if link_col and pd.notna(row.get(link_col)) else None)
                with col2:
                    st.write("❤️ Favorited" if is_fav else "")

    else:
        st.info("No data available to display.")

# ===== FOOTER ===== #
st.markdown("<hr style='border:1px solid #ddd'/>", unsafe_allow_html=True)
st.caption("📘 Powered by Streamlit | © 2025 GeoAI Repository")
st.markdown("""
<p style='text-align:center; font-size:12px; color:gray;'>
Developed by Shubh | 
<a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a>
</p>
""", unsafe_allow_html=True)
