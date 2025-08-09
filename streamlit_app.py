# ===== Force install packages from requirement_1.txt ===== #
import sys, subprocess
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirement_1.txt"])
except Exception as e:
    print(f"Warning: Could not install from requirement_1.txt: {e}")

# ===== Imports after installing dependencies ===== #
import streamlit as st
import pandas as pd
import altair as alt
import re
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# ===== PAGE CONFIG ===== #
st.set_page_config(page_title="GeoAI Repository", layout="wide")

# ===== LOAD LOGIN CONFIG ===== #
def load_auth_config(config_path: str = "config.yaml"):
    """Load and validate authentication configuration from YAML."""
    try:
        with open(config_path) as file:
            config = yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")

    credentials = config.get("credentials")
    cookie = config.get("cookie", {})
    cookie_name = cookie.get("name")
    cookie_key = cookie.get("key")
    expiry_days = cookie.get("expiry_days")

    if not all([credentials, cookie_name, cookie_key, expiry_days]):
        raise ValueError(
            "Authentication config missing required fields. "
            "Check 'credentials', 'cookie.name', 'cookie.key', and 'cookie.expiry_days' in config.yaml."
        )

    return credentials, cookie_name, cookie_key, expiry_days

# Initialize authenticator
try:
    credentials, cookie_name, cookie_key, expiry_days = load_auth_config()
    authenticator = stauth.Authenticate(
        credentials,
        cookie_name,
        cookie_key,
        expiry_days
    )
except Exception as e:
    st.error(f"Authentication configuration error: {e}")
    st.stop()

# ===== LOGIN ===== #
name, authentication_status, username = authenticator.login('Login', 'sidebar')

if authentication_status:
    st.sidebar.success(f"Welcome {name} 👋")
    authenticator.logout('Logout', 'sidebar')

    # ==== PUT YOUR MAIN GEOAI APP CODE BELOW ==== #
    # (Paste your working repository display code here unchanged)

elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
