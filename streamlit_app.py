import streamlit as st
import pandas as pd
import hashlib
import re
import os
import json
from datetime import date
import streamlit.components.v1 as components

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="GeoAI Repository",
    page_icon="https://raw.githubusercontent.com/Shubhdhadiwal/GeoAIRepository/main/geoai_logo.png",
    layout="wide",
)

# =========================
# CONSTANTS
# =========================
LOGO_URL = "https://raw.githubusercontent.com/Shubhdhadiwal/GeoAIRepository/main/geoai_logo.png"
GITHUB_RAW_URL = "https://github.com/Shubhdhadiwal/GeoAIRepository/raw/main/Geospatial%20Data%20Repository%20(2).xlsx"
VISITOR_COUNT_FILE = "visitor_count_by_date.json"

# =========================
# TOP LOGO
# =========================
st.image(LOGO_URL, width=200)

# =========================
# AUTHENTICATION
# =========================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

USER_CREDENTIALS = {
    "Shubh1301": hash_password("Shubh130128")
}

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['username'] = None

def login():
    st.title("🔐 Login to GeoAI Repository")
    st.markdown("""
    <hr>
    <p style="font-size:12px; color:gray;">
    🛠️ <b>Need login access or help?</b><br>
    Please contact the developer for login credentials:<br>
    👉 <a href="https://www.linkedin.com/in/shubh-dhadiwal/" target="_blank">Shubh Dhadiwal on LinkedIn</a>
    </p>
    <hr>
    """, unsafe_allow_html=True)

    username = st.text_input("Username", key="username_input")
    password = st.text_input("Password", type="password", key="password_input")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == hash_password(password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
        else:
            st.error("❌ Invalid username or password")

if not st.session_state['authenticated']:
    login()
    st.stop()

# =========================
# SIDEBAR
# =========================
if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.rerun()

st.sidebar.title(f"Welcome, {st.session_state['username']}!")

sheet_options = {
    "About": "About",
    "Data Sources": "Data Sources",
    "Tools": "Tools",
    "Free Tutorials": "Free Tutorials",
    "Python Codes (GEE)": "Google Earth EnginePython Codes",
    "Courses": "Courses",
    "Dashboards": "Dashboards",
    "Submit New Resource": "Submit New Resource",
    "Favorites": "Favorites",
    "FAQ": "FAQ",
}

st.sidebar.header("🧭 GeoAI Repository")
selected_tab = st.sidebar.radio("Select Section", list(sheet_options.keys()))

# =========================
# VISITOR COUNTER FUNCTIONS
# =========================
def get_visitor_count_today():
    today_str = str(date.today())
    if not os.path.exists(VISITOR_COUNT_FILE):
        with open(VISITOR_COUNT_FILE, "w") as f:
            json.dump({}, f)
        return 0
    with open(VISITOR_COUNT_FILE, "r") as f:
        try:
            counts = json.load(f)
        except json.JSONDecodeError:
            counts = {}
    return counts.get(today_str, 0)

def get_total_visitor_count():
    if not os.path.exists(VISITOR_COUNT_FILE):
        return 0
    with open(VISITOR_COUNT_FILE, "r") as f:
        try:
            counts = json.load(f)
        except json.JSONDecodeError:
            counts = {}
    return sum(counts.values())

def increment_visitor_count_today():
    today_str = str(date.today())
    if not os.path.exists(VISITOR_COUNT_FILE):
        counts = {}
    else:
        with open(VISITOR_COUNT_FILE, "r") as f:
            try:
                counts = json.load(f)
            except json.JSONDecodeError:
                counts = {}
    counts[today_str] = counts.get(today_str, 0) + 1
    with open(VISITOR_COUNT_FILE, "w") as f:
        json.dump(counts, f)
    return counts[today_str]

    # Only increment visitor counter on About page
    if 'visitor_counted' not in st.session_state:
        st.session_state.today_visitor_count = increment_visitor_count_today()
        st.session_state.total_visitor_count = get_total_visitor_count()
        st.session_state.visitor_counted = True

    st.markdown(
        f"""
        <p style='font-size:14px; color:gray;'>
        📅 Today's Visitors: <b>{st.session_state.today_visitor_count}</b><br>
        📈 Total Visitors: <b>{st.session_state.total_visitor_count}</b>
        </p>
        """,
        unsafe_allow_html=True
    )

# =========================
# DATA LOADER
# =========================
@st.cache_data(show_spinner=False)
def load_data(sheet_name):
    try:
        df = pd.read_excel(GITHUB_RAW_URL, sheet_name=sheet_name)
        df.columns = df.iloc[0]
        df = df[1:]
        df = df.dropna(subset=[df.columns[0]])
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        if sheet_name == "Tools":
            new_cols = {col: "Link" for col in df.columns if isinstance(col, str) and col.startswith("Column")}
            if new_cols:
                df = df.rename(columns=new_cols)

        return df
    except Exception as e:
        st.error(f"Error loading sheet '{sheet_name}': {e}")
        return pd.DataFrame()

# =========================
# HELPERS
# =========================
def highlight_search(text, term):
    if not term:
        return text
    regex = re.compile(re.escape(term), re.IGNORECASE)
    return regex.sub(lambda match: f"**:yellow[{match.group(0)}]**", str(text))

if "favorites" not in st.session_state:
    st.session_state.favorites = {}

# =========================
# TAB RENDERERS
# =========================
def show_dashboards():
    st.title("🌍 Dashboards")

    # CSS only for this page (fullscreen map support)
    st.markdown("""
    <style>
    .block-container { max-width: 98% !important; padding-left: 1rem; padding-right: 1rem; }
    iframe.fullscreen-map { height: 90vh; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

    with st.expander("🏢 Google Open Building Dashboard"):
        st.markdown("""
        This large-scale open dataset consists of outlines of buildings derived from high-resolution 50 cm satellite imagery. It contains 1.8B building detections in Africa, Latin America, Caribbean, South Asia and Southeast Asia. The inference spanned an area of 58M km².
    
        For each building in this dataset we include the polygon describing its footprint on the ground, a confidence score indicating how sure we are that this is a building, and a Plus Code corresponding to the center of the building. There is no information about the type of building, its street address, or any details other than its geometry.
    
        Building footprints are useful for a range of important applications: from population estimation, urban planning and humanitarian response to environmental and climate science.
    
        The project is based in Ghana, with an initial focus on the continent of Africa and new updates on South Asia, South-East Asia, Latin America and the Caribbean. Inference was carried out during May 2023.
        """)
        
        st.markdown("🔗 [Official Dataset Documentation](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_Research_open-buildings_v3_polygons)")
        
        st.markdown("---")
        
        st.markdown(
            """<iframe src="https://ee-shubhdhadiwal.projects.earthengine.app/view/geoai" width="100%" height="600" frameborder="0" allowfullscreen></iframe>""",
            unsafe_allow_html=True
        )
        
        st.markdown("""
    **Note:**  
    1. Some state boundaries may not be available in the FAO GAUL dataset.  
    2. Detailed statistical analysis can be performed in GIS or Google Earth Engine using the raw dataset.  
    3. To get access to the processing scripts and download the data, please contact the developer. Custom analysis and tailored building footprint studies are available upon request (may be subject to service fees).
    
    Dashboard created by Shubh Dhadiwal using Google Earth Engine (GEE).
    """)

    with st.expander("🌍 Local Climate Zones (LCZ) Dashboard"):
        st.markdown("""
        This global map of Local Climate Zones, at 100m pixel size and representative for the nominal year 2018, is derived from multiple earth observation datasets and expert LCZ class labels. LCZ_Filter is the recommended band for most users. The other classification band, LCZ, is only provided as it is used to calculate the LCZ_Probability band.
    
        The LCZ scheme complements other land use / land cover schemes by its focus on urban and rural landscape types, which can be described by any of the 17 classes in the LCZ scheme. Out of the 17 LCZ classes, 10 reflect the 'built' environment, and each LCZ type is associated with generic numerical descriptions of key urban canopy parameters critical to model atmospheric responses to urbanisation.
    
        In addition, since LCZs were originally designed as a new framework for urban heat island studies, they also contain a limited set (7) of 'natural' land-cover classes that can be used as 'control' or 'natural reference' areas.
        """)
        st.markdown("🔗 [Official Dataset Documentation](https://developers.google.com/earth-engine/datasets/catalog/RUB_RUBCLIM_LCZ_global_lcz_map_latest#description)")
        st.markdown("---")
        st.markdown(
            """<iframe src="https://ee-shubhdhadiwal.projects.earthengine.app/view/lcz-dashboard" width="100%" height="600" frameborder="0" allowfullscreen></iframe>""",
            unsafe_allow_html=True
        )
        st.markdown("""
    **Note:**  
    1. Some state boundaries may not be available in the FAO GAUL dataset.  
    2. Detailed statistical analysis can be performed in GIS or Google Earth Engine using the raw dataset.  
    3. To get access to the processing scripts and download the data, please contact the developer. Custom analysis and tailored LCZ studies are available upon request (may be subject to service fees).
    
    Dashboard created by Shubh Dhadiwal using Google Earth Engine (GEE).
    """)

    with st.expander("🚴 BBBike OSM Extract Service"):
        st.markdown("""
        The **BBBike OSM Extract Service** is a free web-based tool for extracting **OpenStreetMap (OSM)** data for custom-defined areas anywhere in the world. Users can:
        - Select a region by drawing a polygon or choosing from predefined cities
        - Download OSM data in multiple formats (Shapefile, GeoJSON, Garmin IMG, KML, PBF, CSV, etc.)
        - Filter datasets to include only desired layers (roads, buildings, land use, points of interest, etc.)

**Key Features:**
- Global coverage
- Multiple coordinate reference systems supported
        """)
        components.iframe("https://extract.bbbike.org/", height=700, width=1300, scrolling=True)

    with st.expander("🌐 DIVA-GIS Global Data Access"):
        st.markdown("""
        **DIVA-GIS** provides free spatial data for any country in the world, including:
        - Administrative boundaries
        - Roads, railways, and population density
        - Elevation and climate data
        - Land cover maps

This is especially useful for GIS analysis, ecological studies, and spatial planning.

🔗 [Official DIVA-GIS Website](https://diva-gis.org/data.html)
        """)
        components.iframe("https://diva-gis.org/data.html", height=900, width=1400, scrolling=True)

    with st.expander("▶️ Gridded Population of World 2020"):
        st.markdown("""
        This dataset contains estimates of the number of persons per 30 arc-second (~1 km) grid cell, consistent with national censuses and population registers with respect to relative spatial distribution but adjusted to match the 2015 Revision of UN World Population Prospects country totals.
    
        There is one image for each modeled year (2000, 2005, 2010, 2015, and 2020). Population is distributed to cells using proportional allocation of population from census and administrative units.
        """)
        st.markdown("🔗 [General Dataset Documentation - GPWv4, CIESIN, Columbia University](https://doi.org/10.7927/H4F47M65)")
        
        st.markdown("---")
        
        st.markdown(
            """<iframe src="https://ee-shubhdhadiwal.projects.earthengine.app/view/gridded-population-of-world-2020" width="100%" height="600" frameborder="0" allowfullscreen></iframe>""",
            unsafe_allow_html=True
        )
        
        st.markdown("""
    **Note:**  
    1. Some state boundaries may not be available in the FAO GAUL dataset.  
    2. Detailed statistical analysis can be performed in GIS or Google Earth Engine using the raw dataset.  
    3. To get access to the processing scripts and download the data, please contact the developer. Custom analysis and tailored population studies are available upon request (may be subject to service fees).
    
    Dashboard created by Shubh Dhadiwal using Google Earth Engine (GEE).
    """)
        
        st.markdown("""--- **Citation:** Center for International Earth Science Information Network - CIESIN - Columbia University. 2018. Gridded Population of the World, Version 4 (GPWv4.11): Population Density Adjusted to Match 2015 Revision of UN WPP Country Totals, Revision 11. Palisades, NY: NASA Socioeconomic Data and Applications Center (SEDAC). https://doi.org/10.7927/H4F47M65. Accessed 12 August 2025.""")

    with st.expander("🌡️ Global Landsat LST Explorer"):
        st.markdown("""
        The **Global Landsat LST Explorer** is an interactive Google Earth Engine (GEE) application for analyzing Land Surface Temperature (LST) using Landsat 8 and Landsat 9 Collection 2 Level-2 data.
    
        **Features include:**
        - Selecting **country**, **state/province**, and **year (March–June period)**
        - Visualizing **median LST**
        - Displaying **discrete temperature classes** (e.g., 0–10 °C, 10–20 °C, …, 60–70 °C)
        - Viewing **yearly min/max trend charts** (2015–2024)
        - Exporting processed LST as **GeoTIFF**
    
        **Data Sources & Processing Highlights:**
        - Landsat 8 (LANDSAT/LC08/C02/T1_L2) & Landsat 9 (LANDSAT/LC09/C02/T1_L2) thermal band ST_B10 (Kelvin → °C)
        - Cloud masking via QA_PIXEL band
        - Median compositing (March 1 – June 30)
        - FAO GAUL 2015 boundaries for administrative regions
        - Spatial resolution: 30 m
        """)
        
        st.markdown("🔗 [Landsat 8 Collection 2 L2 Documentation](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2)")
        st.markdown("🔗 [Landsat 9 Collection 2 L2 Documentation](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2)")
        
        st.markdown("---")
        
        st.markdown(
            """
            <iframe src="https://ee-shubhdhadiwal.projects.earthengine.app/view/global-landsat-lst-explorer" width="100%" height="600" frameborder="0" allowfullscreen> </iframe>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("""
    **Note:**  
    1. Some state boundaries may not be available in the FAO GAUL dataset.  
    2. Detailed statistical analysis can be performed in GIS or Google Earth Engine using the raw dataset.  
    3. To get access to the processing scripts and download the data, please contact the developer. Custom analysis and tailored LST studies are available upon request (may be subject to service fees).
    
    Dashboard created by Shubh Dhadiwal using Google Earth Engine (GEE).
    """)

    with st.expander("☀️ NASA POWER Data Access Viewer"):
        st.markdown("""
        The **NASA POWER (Prediction Of Worldwide Energy Resources) Data Access Viewer** is a web-based tool that provides access to global meteorological and solar energy data. It is widely used for:
        - Renewable energy assessments
        - Agricultural planning
        - Climate research and environmental studies
        - Weather-related analytics

**Key Features:**
- Download daily, hourly, or climatological datasets
- Access variables like temperature, humidity, wind speed, precipitation, and solar radiation
- Select specific geographic coordinates or regions
- Multiple output formats (CSV, GeoJSON, NetCDF, etc.)
- Easy visualization of time series and maps

**Data Sources:**
- NASA's MERRA-2 (Modern-Era Retrospective Analysis for Research and Applications, Version 2)
- GEOS (Goddard Earth Observing System) models

**Applications:**
- Solar energy project design
- Crop modeling
- Hydrology and water resource management
- Climate variability analysis
        """)
        st.markdown("🔗 [NASA POWER Data Access Viewer Website](https://power.larc.nasa.gov/data-access-viewer/)")
        st.components.v1.iframe(
            "https://power.larc.nasa.gov/data-access-viewer/",
            height=900,
            width=1400,
            scrolling=True
        )
        st.markdown(
            """<p style='font-size:15px; color:gray;'> Source: NASA POWER Project, <a href="https://power.larc.nasa.gov/data-access-viewer/" target="_blank">https://power.larc.nasa.gov/data-access-viewer/</a><br> Credit: NASA Langley Research Center (LaRC) — Prediction Of Worldwide Energy Resources (POWER) Project </p>""",
            unsafe_allow_html=True
        )

    with st.expander("🛰️ ESA WorldCover LULC Change Analysis 2020-2021"):
        st.markdown("""
        The European Space Agency (ESA) WorldCover 10 m products provide global land cover maps at 10 m spatial resolution based on Sentinel-1 and Sentinel-2 data. Available years: **2020** and **2021**.

The WorldCover products have been generated as part of the ESA WorldCover project, under the 5th Earth Observation Envelope Programme (EOEP-5) of the European Space Agency.

**Citation:** Zanaga, D., Van De Kerchove, R., De Keersmaecker, W., Souverijns, N., Brockmann, C., Quast, R., Wevers, J., Grosu, A., Paccini, A., Vergnaud, S., Cartus, O., Santoro, M., Fritz, S., Georgieva, I., Lesiv, M., Carter, S., Herold, M., Li, Linlin, Tsendbazar, N.E., Ramoino, F., Arino, O., 2021. ESA WorldCover 10 m 2020 v100. (doi:10.5281/zenodo.5571936)

See also:
- [ESA WorldCover website](https://esa-worldcover.org/en)
- [User Manual and Validation Report](https://esa-worldcover.org/en/data-access)
        """)
        st.markdown("---")
        st.markdown(f"""
            <iframe src="https://ee-shubhdhadiwal.projects.earthengine.app/view/esa-lulc-2020-2021" width="100%" height="600" frameborder="0" allowfullscreen> </iframe>
        """, unsafe_allow_html=True)
        st.markdown("**Note:**")
        st.markdown("""
1. Some state boundaries may not be available in the FAO GAUL dataset.
2. This dashboard displays the results only; advanced analysis as per the needs to be performed in GIS after downloading the data.
3. To get access to the code and download the data, please contact the developer. Customization of the code tailored to your study can also be requested (it may be subject to service fees).
This dashboard is created by Shubh Dhadiwal using Google Earth Engine.
        """, unsafe_allow_html=True)
        
# ✅ MODIS moved INSIDE Dashboards tab (this fixes the leak)
    with st.expander("🗺️ MODIS Land Use Land Cover (LULC) Change Analysis 2010-2024"):
        st.markdown("""
        The **Terra and Aqua combined Moderate Resolution Imaging Spectroradiometer (MODIS)** Land Cover Type (MCD12Q1) Version 6.1 data product provides global land cover types at yearly intervals.
    
        The MCD12Q1 Version 6.1 product is derived using **supervised classifications** of MODIS Terra and Aqua reflectance data.  
        Land cover types are derived from the:
        - **International Geosphere-Biosphere Programme (IGBP)**
        - **University of Maryland (UMD)**
        - **Leaf Area Index (LAI)**
        - **BIOME-Biogeochemical Cycles (BGC)**
        - **Plant Functional Types (PFT)** classification schemes.
    
        The supervised classifications undergo **post-processing** that incorporates prior knowledge and ancillary information to refine specific classes.  
        Additional land cover property assessment layers are provided by the **FAO Land Cover Classification System (LCCS)** for land cover, land use, and surface hydrology.
    
        **Applications include:**
        - Monitoring long-term land cover change
        - Tracking transitions between cropland, forest, urban, grassland, and other categories
        - Supporting climate, hydrology, and biodiversity research
    
        **Citation:** Please visit the [LP DAAC 'Citing Our Data'](https://lpdaac.usgs.gov/citing-data/) page for information on citing LP DAAC datasets.  
        Dataset reference: *Friedl, M.A., Sulla-Menashe, D., 2021. MCD12Q1 MODIS/Terra+Aqua Land Cover Type Yearly L3 Global 500 m SIN Grid V061. NASA EOSDIS Land Processes DAAC.* (doi:[10.5067/MODIS/MCD12Q1.061](https://doi.org/10.5067/MODIS/MCD12Q1.061))
        """)
        
        st.markdown("---")
        
        st.markdown(
            """<iframe class="fullscreen-map" src="https://ee-shubhdhadiwal.projects.earthengine.app/view/modis-lulc-change-analysis-2010-2024" width="100%" height="600" frameborder="0" allowfullscreen></iframe>""",
            unsafe_allow_html=True
        )
    
        st.markdown("""
        **Note:**
        1. Some state boundaries may not be available in the FAO GAUL dataset.
        2. This dashboard visualizes annual MODIS LULC maps from 2010 to 2024; detailed statistical analysis can be performed in GIS or Earth Engine using the raw dataset.
        3. To get access to the processing scripts and download the data, please contact the developer. Custom analysis and tailored LULC change detection services are available upon request (may be subject to service fees).
    
        *This dashboard is created by Shubh Dhadiwal using Google Earth Engine.*
        """, unsafe_allow_html=True)
    
    with st.expander("💧 Global Surface Water (GSW) Explorer 1984-2021"):
        st.markdown("""
        The **Global Surface Water (GSW) dataset** provides a comprehensive view of the location and temporal distribution of surface water from **1984 to 2021**.  
        It includes statistics on the extent, occurrence, change, and seasonality of water surfaces, enabling detailed hydrological and environmental analysis.
    
        **Dataset Overview:**
        - Generated using **4,716,475 Landsat 5, 7, and 8 scenes** acquired between 16 March 1984 and 31 December 2021.
        - Each pixel is classified as water / non-water using an expert system.
        - Provides monthly histories and two epochs (1984–1999 and 2000–2021) for change detection.
        - The mapping layer product consists of **1 image with 7 bands**, mapping spatial and temporal water distribution over 38 years.
    
        **Key Metrics:**
        - **Occurrence:** The frequency with which water is present at a given location. Useful for identifying permanent versus intermittent water bodies.
        - **Seasonality:** The typical timing and duration of water presence within a year. Helps understand wet and dry periods and plan water management.
        - **Transition:** The change of a pixel from water to non-water or vice versa between two epochs. Indicates areas of water gain or loss.
        - **Extent:** The total area covered by water at a given time. Critical for assessing flood risk, reservoir storage, and wetland health.
        - **Change:** The difference in water presence between two time periods (e.g., 1984–1999 vs 2000–2021). Highlights trends due to climate, land use, or hydrological interventions.
        - **Recurrence:** The probability that a location that was once water will return to being water in future observations. Helps identify persistent vs. ephemeral water bodies.
    
        **Applications:**
        - Monitoring long-term water surface changes
        - Assessing impacts of climate change, urbanization, or irrigation
        - Supporting water resource management, flood risk assessment, and environmental policy
    
        **Citation:**  
        Pekel, J.-F., Cottam, A., Gorelick, N., & Belward, A. S. (2016). High-resolution mapping of global surface water and its long-term changes. *Nature*, 540(7633), 418–422. [doi:10.1038/nature20584](https://doi.org/10.1038/nature20584)
    
        **Data Users Guide:** [GSW Data User Guide](https://global-surface-water.appspot.com/)
    
        """, unsafe_allow_html=True)
    
        st.markdown("---")
    
        st.markdown(
            """<iframe src="https://ee-shubhdhadiwal.projects.earthengine.app/view/global-surface-water-explorer" width="100%" height="600" frameborder="0" allowfullscreen></iframe>""",
            unsafe_allow_html=True
        )
    
        st.markdown("""
        **Note:**
        1. Some state boundaries may not be available in the FAO GAUL dataset.
        2. This dashboard visualizes Global Surface Water (GSW) metrics; detailed statistical analysis can be performed in GIS or Earth Engine using the raw dataset.
        3. To get access to the processing scripts and download the data, please contact the developer. Custom analysis and tailored GSW studies are available upon request (may be subject to service fees).
    
        *This dashboard is created by Shubh Dhadiwal using Google Earth Engine.*
        """, unsafe_allow_html=True)

    with st.expander("⚠️💧 Flood Detection Dashboard, 2015-2025"):
        st.markdown("""
        The **Flood Detection Dashboard** uses **Sentinel-1 SAR imagery** to detect potential flood-affected areas from **2015 to 2025**.  
        It allows users to interactively explore flood extents for different states, months, and years, providing valuable insights for research, urban planning, and disaster management.
    
        **Dataset Overview:**
        - Uses **Sentinel-1 VV polarization SAR imagery** to detect low backscatter areas, indicative of potential flooding.
        - Flood detection threshold is set at **-13 dB VV**, capturing water-covered surfaces even under cloudy conditions.
        - State boundaries are from **FAO GAUL 2015 Level 1 dataset**. Some regions may not be available or incomplete.
    
        **Key Features:**
        - **State/Region Selection:** Choose a state or region to visualize floods.  
        - **Month Selection:** View flood extents for any month (01–12).  
        - **Year Slider:** Interactive slider allows browsing floods from **2015 to 2025**.  
        - **Detected Flood Areas:** Blue shaded areas show regions with potential flooding.  
        - **Export Functionality:** Download the flood layer as a GeoTIFF for further analysis.
    
        **Applications:**
        - Flood risk assessment and early warning
        - Urban planning and disaster management
        - Research on temporal flood patterns
    
        **Data Sources:**  
        - Sentinel-1 SAR Imagery (COPERNICUS/S1_GRD)  
        - State Boundaries (FAO GAUL 2015; some boundaries may be missing)
    
        **Explore the Dashboard:**  
        [Open Flood Detection Dashboard](https://ee-shubhdhadiwal.projects.earthengine.app/view/flood-detection-sentinel-1-2015-2025)
    
        **Note:**
        1. This dashboard identifies potential flooded areas but does not differentiate between riverine or urban floods.  
        2. Validation with local ground data is recommended before decision-making.  
        3. Some state boundaries may not be available in the FAO GAUL dataset.  
        4. Detailed statistical analysis can be performed in GIS or Earth Engine using the raw dataset.  
        5. To get access to the processing scripts and download the data, please contact the developer. Custom analysis and tailored flood studies are available upon request (may be subject to service fees).  
        6. The use of Sentinel data is governed by the [Copernicus Sentinel Data Terms and Conditions](https://sentinels.copernicus.eu/web/sentinel/terms-of-use).
    
        *This dashboard is created by Shubh Dhadiwal using Google Earth Engine.*
        """, unsafe_allow_html=True)
    
        st.markdown("---")
    
        st.markdown(
            """<iframe src="https://ee-shubhdhadiwal.projects.earthengine.app/view/flood-detection-sentinel-1-2015-2025" width="100%" height="600" frameborder="0" allowfullscreen></iframe>""",
            unsafe_allow_html=True
        )

def show_about():
    st.title("📘 About GeoAI Repository")
    
    st.markdown("""
    The **GeoAI Repository** is an interactive and open-access platform designed for students, researchers, and professionals in geospatial analytics, urban planning, and climate action. It integrates **Google Earth Engine (GEE)**, Python, and other open-source tools to provide powerful, cloud-based geospatial analysis.
    """)
    
    st.info("""
    - 🌐 **Public Geospatial Datasets**: Land use, climate, urban infrastructure, and environmental change.  
    - 🛠️ **Open-Source Tools & Platforms**: Built on GEE, Python, and open frameworks.  
    - 📘 **Tutorials & Workflows**: Step-by-step guides for geospatial AI projects.  
    - 💻 **Python & GEE Scripts**: Satellite processing, LULC, and modeling.  
    - 📊 **Interactive Visualizations**: Dynamic maps, charts, and dashboards.
    """)
    
    st.subheader("🌟 Vision")
    st.markdown("Empower analysts and planners with accessible, AI-driven geospatial intelligence for a sustainable, resilient planet.")
    
    st.subheader("🎯 Mission")
    st.markdown("""
    1. Democratize geospatial data  
    2. Leverage AI/ML for classification and prediction  
    3. Promote open-source tools  
    4. Enable real-time insights via dashboards  
    5. Support data-driven decision-making
    """)

    # Content overview (counts)
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
    Licensed under the <a href='https://creativecommons.org/licenses/by-nc/4.0/' target='_blank'>Creative Commons BY-NC 4.0 License</a>.
    </p>
    """, unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align:center; font-size:12px; color:gray;'>
    Developed by Shubh | <a href='https://www.linkedin.com/in/shubh-dhadiwal/' target='_blank'>LinkedIn</a>
    </p>
    """, unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align:center; font-size:12px; color:gray;'>
    © 2025 GeoAI Repository
    </p>
    """, unsafe_allow_html=True)

def show_submit_new_resource():
    st.title("📤 Submit a New Resource")
    st.markdown("Help us grow this repository by contributing useful links and resources.")
    st.markdown("You can submit your resource using [this Google Form](https://forms.gle/FZZpvr4xQyon5nDs6).")

def show_faq():
    st.title("❓ Frequently Asked Questions")
    faqs = {
        "What is GeoAI Repository?": "It is a free and open resource hub for geospatial analytics, ML, and planning.",
        "How can I contribute resources?": "Use the 'Submit New Resource' tab to add new links and resources.",
        "Are the datasets free to use?": "Yes, all datasets listed here are publicly accessible and free.",
        "Can I save favorite resources?": "Yes, use the 'Favorites' tab to view and manage your favorite items.",
        "What are the Dashboards?": "The Dashboards section provides interactive visualization of geospatial data.",
        "Who developed this repository?": "This repository is developed and maintained by Shubh Dhadiwal.",
    }
    for question, answer in faqs.items():
        with st.expander(question):
            st.write(answer)

def show_list_tab(selected_tab):
    # Load data for normal tabs + Favorites aggregation if needed
    if selected_tab != "Favorites":
        df = load_data(sheet_options[selected_tab])
    else:
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

    # Title
    st.title(f"🌍 GeoAI Repository – {selected_tab}")

    if df.empty:
        st.info("No resources to display.")
        return

    # Search/filter
    search_term = st.sidebar.text_input("🔍 Search")
    if selected_tab not in ["Favorites", "About", "Submit New Resource", "Dashboards", "FAQ"] and search_term:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)]

    if selected_tab == "Data Sources" and "Type" in df.columns:
        type_filter = st.sidebar.multiselect("📂 Filter by Type", sorted(df["Type"].dropna().unique()))
        if type_filter:
            df = df[df["Type"].isin(type_filter)]

    # Title column per tab
    title_map = {
        "Data Sources": "Data Source",
        "Tools": "Tools",
        "Courses": "Tutorials",
        "Python Codes (GEE)": "Title",
        "Free Tutorials": "Tutorials",
        "Favorites": "Title",
    }
    title_col = title_map.get(selected_tab, df.columns[0] if not df.empty else None)
    if selected_tab == "Favorites":
        title_col = "Title" if "Title" in df.columns else (df.columns[0] if not df.empty else None)

    # Link columns per tab
    link_columns_map = {
        "Data Sources": ["Links", "Link"],
        "Tools": ["Tool Link", "Link", "Links"],
        "Courses": ["Course Link", "Link", "Links"],
        "Free Tutorials": ["Link", "Links", "Tutorial Link"],
        "Python Codes (GEE)": ["Link", "Links", "Link to the codes"],
        "Favorites": ["Link", "Links", "Link to the codes", "Tool Link", "Course Link", "Tutorial Link"],
    }
    possible_links = link_columns_map.get(
        selected_tab, ["Links", "Link", "Link to the codes", "Tool Link", "Course Link", "Tutorial Link"]
    )

    view_mode = st.sidebar.radio("View Mode", ["Detailed", "Compact"])

    for idx, row in df.iterrows():
        # Determine category and title in case of Favorites
        if selected_tab.strip().lower() == "favorites":
            category_key = row.get("Category", None)
            title_for_fav = title_map.get(category_key, title_col)
            resource_title = row.get(title_for_fav)
            if not resource_title or str(resource_title).strip() == "":
                resource_title = f"Resource-{idx+1}"
        else:
            category_key = selected_tab
            resource_title = row.get(title_col)
            if not resource_title or str(resource_title).strip() == "":
                resource_title = f"Resource-{idx+1}"

        displayed_title = highlight_search(resource_title, search_term)

        # Collect links for this row
        links = []
        for col in possible_links:
            if col in df.columns and pd.notna(row.get(col)):
                val = str(row[col]).strip()
                if val.lower().startswith(("http://", "https://", "www.")):
                    links.append((col, val))

        if view_mode == "Detailed" or selected_tab.strip().lower() == "favorites":
            with st.expander(f"🔹 {displayed_title}", expanded=False):
                col1, col2 = st.columns([0.9, 0.1])
                with col2:
                    fav_checkbox = st.checkbox(
                        "⭐",
                        value=idx in st.session_state.favorites.get(category_key, []),
                        key=f"{category_key}_{idx}",
                    )
                with col1:
                    if "Description" in df.columns and pd.notna(row.get("Description")):
                        st.write(highlight_search(row["Description"], search_term))
                    for link_name, link_url in links:
                        st.markdown(f"[🔗 {link_name}]({link_url})", unsafe_allow_html=True)
                    if "Purpose" in df.columns and pd.notna(row.get("Purpose")):
                        st.markdown(f"**🎯 Purpose:** {highlight_search(row['Purpose'], search_term)}")
                    exclude_cols = [title_col, "Description", "Purpose", "S.No", "Category"] + possible_links
                    for col in df.columns:
                        if col not in exclude_cols and pd.notna(row.get(col)):
                            st.markdown(f"**{col}:** {highlight_search(row[col], search_term)}")

                # Update favorites
                if fav_checkbox and idx not in st.session_state.favorites.get(category_key, []):
                    st.session_state.favorites.setdefault(category_key, []).append(idx)
                elif not fav_checkbox and idx in st.session_state.favorites.get(category_key, []):
                    st.session_state.favorites[category_key].remove(idx)
        else:
            compact_col1, compact_col2, compact_col3 = st.columns([6, 3, 1])
            with compact_col1:
                st.markdown(f"🔹 {displayed_title}")
            with compact_col2:
                for link_name, link_url in links:
                    st.markdown(f"[🔗 {link_name}]({link_url})", unsafe_allow_html=True)
            with compact_col3:
                fav_checkbox = st.checkbox(
                    "⭐",
                    value=idx in st.session_state.favorites.get(category_key, []),
                    key=f"compact_{category_key}_{idx}",
                )
                if fav_checkbox and idx not in st.session_state.favorites.get(category_key, []):
                    st.session_state.favorites.setdefault(category_key, []).append(idx)
                elif not fav_checkbox and idx in st.session_state.favorites.get(category_key, []):
                    st.session_state.favorites[category_key].remove(idx)

# =========================
# ROUTER
# =========================
if selected_tab == "Dashboards":
    show_dashboards()
elif selected_tab == "About":
    show_about()
elif selected_tab == "Submit New Resource":
    show_submit_new_resource()
elif selected_tab == "FAQ":
    show_faq()
else:
    # All other tabs render the list interface (incl. Favorites)
    show_list_tab(selected_tab)

