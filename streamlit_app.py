import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth

# ===== PAGE CONFIG ===== #
st.set_page_config(page_title="GeoAI Repository", layout="wide")

# ===== USER AUTH SETUP ===== #
users = {
    "usernames": {
        "shubh": {
            "name": "Shubh Dhadiwal",
            "password": "$2b$12$N0exmplEHashedPasswordHere1234567890abcdEfghIjkl"  # Replace with your hash
        },
        "admin": {
            "name": "Admin User",
            "password": "$2b$12$An0therExampleHashedPasswordForAdmin1234567890"  # Replace with your hash
        }
    }
}

usernames = list(users["usernames"].keys())
names = [users["usernames"][u]["name"] for u in usernames]
passwords = [users["usernames"][u]["password"] for u in usernames]

authenticator = stauth.Authenticate(
    names,
    usernames,
    passwords,
    "geoai_dashboard_cookie",  # Cookie name
    "random_signature_key_123",  # Change to a strong random string
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", "main")

if not authentication_status:
    if authentication_status is False:
        st.error("Username/password is incorrect")
    elif authentication_status is None:
        st.warning("Please enter your username and password")
    st.stop()

# User is authenticated here
authenticator.logout("Logout", "sidebar")
st.sidebar.write(f"Welcome *{name}*")

# ===== Your existing app code =====

sheet_options = {
    "About": "About",
    "Data Sources": "Data Sources",
    "Tools": "Tools",
    "Free Tutorials": "Free Tutorials",
    "Python Codes (GEE)": "Google Earth EnginePython Codes",
    "Courses": "Courses",
    "Submit New Resource": "Submit New Resource"
}

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
        return pd.DataFrame()

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
    
    selected_metric = st.radio(
        "Select category:",
        categories_to_check,
        index=0,
        horizontal=True
    )

    cols = st.columns(len(categories_to_check))
    for i, cat in enumerate(categories_to_check):
        label = f"➡️ {cat}" if cat == selected_metric else cat
        cols[i].metric(label=label, value=counts.get(cat, 0))

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
    if st.button("Open Google Submission Form"):
        st.markdown(f"[Click here to submit your resource]({google_form_url})", unsafe_allow_html=True)
    else:
        st.markdown(f"Or you can submit your resource using [this Google Form]({google_form_url})")
    st.stop()

df = load_data(sheet_options[selected_tab])

search_term = st.sidebar.text_input("🔍 Search")
if search_term:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]

if selected_tab == "Data Sources" and "Type" in df.columns:
    type_filter = st.sidebar.multiselect("📂 Filter by Type", sorted(df["Type"].dropna().unique()))
    if type_filter:
        df = df[df["Type"].isin(type_filter)]

title_map = {
    "Data Sources": "Data Source",
    "Tools": "Tools",
    "Courses": "Tutorials",
    "Python Codes (GEE)": "Title",
    "Free Tutorials": "Tutorials"
}
title_col = title_map.get(selected_tab, df.columns[0])

st.title(f"🌍 GeoAI Repository – {selected_tab}")

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

st.markdown("<hr style='border:1px solid #ddd'/>", unsafe_allow_html=True)
st.caption("📘 Powered by Streamlit | © 2025 GeoAI Repository")
st.markdown("""
<p style='text-align:center; font-size:12px; color:gray;'>
Developed by Shubh | 
<a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a>
</p>
""", unsafe_allow_html=True)
