import streamlit as st
import pandas as pd

# ===== PAGE CONFIG ===== #
st.set_page_config(page_title="GeoAI Repository", layout="wide")

# ===== SESSION STATE ===== #
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ===== LOAD DATA FUNCTION ===== #
@st.cache_data
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

# ===== SIDEBAR ===== #
st.sidebar.header("🧭 GeoAI Repository")
sheet_options = {
    "About": "About",
    "Data Sources": "Data Sources",
    "Tools": "Tools",
    "Free Tutorials": "Free Tutorials",
    "Python Codes (GEE)": "Python Codes (GEE)",
    "Courses": "Courses",
    "Submit New Resource": "Submit New Resource",
    "Favorites": None,
    "Discussion": None,
    "FAQ & Help": None
}
selected_tab = st.sidebar.radio("Select Section", list(sheet_options.keys()))
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 GeoAI Repository")

# ===== ABOUT ===== #
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

# ===== DISCUSSION CHAT ===== #
elif selected_tab == "Discussion":
    st.title("💬 Discussion Chat")
    st.markdown("Ask your questions and discuss — press **Enter** to send.")

    # Styled message bubble HTML
    def message_bubble(msg):
        return f"""
        <div style="
            background-color:#DCF8C6; 
            padding:10px 15px; 
            border-radius:15px; 
            margin:8px 0; 
            max-width:70%; 
            font-family:sans-serif;
            box-shadow: 1px 1px 3px #ccc;
            ">
            <b>User:</b> {msg}
        </div>
        """

    # Display all chat messages
    for message in st.session_state.chat_messages:
        st.markdown(message_bubble(message), unsafe_allow_html=True)

    # Append message on Enter press
    def add_message():
        msg = st.session_state.chat_input.strip()
        if msg:
            st.session_state.chat_messages.append(msg)
        st.session_state.chat_input = ""

    st.text_input("Type your message here...", key="chat_input", on_change=add_message)

# ===== Other tabs simplified example ===== #
else:
    sheet_name = sheet_options.get(selected_tab)
    if sheet_name:
        df = load_data(sheet_name)
        if not df.empty:
            st.title(f"📂 {selected_tab}")
            st.dataframe(df)
        else:
            st.info("No data available to display.")
    else:
        st.info("Select a valid section from the sidebar.")

# ===== FOOTER ===== #
st.markdown("<hr style='border:1px solid #ddd'/>", unsafe_allow_html=True)
st.caption("📘 Powered by Streamlit | © 2025 GeoAI Repository")
st.markdown("""
<p style='text-align:center; font-size:12px; color:gray;'>
Developed by Shubh | 
<a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a>
</p>
""", unsafe_allow_html=True)
