import streamlit as st
import pandas as pd
import json
import os

# ===== PAGE CONFIG ===== #
st.set_page_config(page_title="GeoAI Repository", layout="wide")

# Add new tabs
sheet_options = {
    "About": "About",
    "Data Sources": "Data Sources",
    "Tools": "Tools",
    "Free Tutorials": "Free Tutorials",
    "Python Codes (GEE)": "Google Earth EnginePython Codes",
    "Courses": "Courses",
    "User Embeds": None,   # Custom tab (no sheet)
    "Discussion": None,    # Chat tab
    "FAQ & Help": None,    # FAQ tab
    "Submit New Resource": "Submit New Resource"
}

# ===== PERSISTENT VOTES FILE ===== #
VOTES_FILE = "votes.json"

def load_votes():
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_votes(votes):
    with open(VOTES_FILE, "w") as f:
        json.dump(votes, f)

votes = load_votes()

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
    if st.button("Open Google Submission Form"):
        st.markdown(f"[Click here to submit your resource]({google_form_url})", unsafe_allow_html=True)
    else:
        st.markdown(f"Or you can submit your resource using [this Google Form]({google_form_url})")
    st.stop()

# ===== USER EMBEDS PAGE (placeholder) ===== #
if selected_tab == "User Embeds":
    st.title("🌐 User Submitted Embeds")
    st.info("This section will showcase user-submitted interactive embeds like maps, dashboards, etc.")
    # You can add actual embeds loading & display here later
    st.stop()

# ===== DISCUSSION CHAT ===== #
if selected_tab == "Discussion":
    st.title("💬 Discussion Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    def submit_message():
        if st.session_state.user_input.strip():
            st.session_state.messages.append(st.session_state.user_input.strip())
            st.session_state.user_input = ""

    st.text_input("Type your message and press Enter:", key="user_input", on_change=submit_message)

    if st.session_state.messages:
        for msg in st.session_state.messages:
            st.chat_message("user").write(msg)
    else:
        st.info("Start the conversation by typing a message above.")
    st.stop()

# ===== FAQ & HELP PAGE ===== #
if selected_tab == "FAQ & Help":
    st.title("❓ FAQ & Help")

    # Example FAQ list - replace with persistent data source if needed
    faq_list = [
        {"q": "How to use the GeoAI Repository?", "a": "Simply select a category and browse resources."},
        {"q": "How to submit new data?", "a": "Go to Submit New Resource tab and fill the form."},
    ]

    for faq in faq_list:
        with st.expander(faq["q"]):
            st.write(faq["a"])

    st.subheader("Ask a Question")
    user_question = st.text_area("Your question here:")

    if st.button("Submit Question"):
        if user_question.strip():
            # Save user questions to a file for admin review (optional)
            questions_file = "user_questions.txt"
            with open(questions_file, "a") as f:
                f.write(user_question.strip() + "\n")
            st.success("Thanks for your question! We'll review and answer soon.")
        else:
            st.error("Please enter a question.")
    st.stop()

# ===== LOAD DATA FOR OTHER TABS ===== #
if selected_tab in sheet_options and sheet_options[selected_tab]:
    df = load_data(sheet_options[selected_tab])
else:
    df = pd.DataFrame()  # empty df for custom tabs

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

# ===== MAIN TITLE ===== #
st.title(f"🌍 GeoAI Repository – {selected_tab}")

if not df.empty:
    # ===== SHOW CARD VIEW WITH UPVOTES ===== #
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

            # Show other columns
            for col in df.columns:
                if col not in exclude_cols + ([link_col] if link_col else []) and pd.notna(row.get(col)):
                    st.markdown(f"**{col}:** {row[col]}")

            # Upvote button & count
            res_id = f"{selected_tab}_{idx}"
            current_votes = votes.get(res_id, 0)
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("👍 Upvote", key=res_id):
                    if f"voted_{res_id}" not in st.session_state:
                        votes[res_id] = current_votes + 1
                        save_votes(votes)
                        st.session_state[f"voted_{res_id}"] = True
                        st.experimental_rerun()
                    else:
                        st.warning("You already voted!")
            with col2:
                st.write(f"Votes: {current_votes}")

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
