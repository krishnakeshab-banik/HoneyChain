"""
HoneyChain Prototype Dashboard
==============================

FILE:
    frontend/app.py


WHAT IS THIS FILE?
------------------

This is the USER-FACING web application for the HoneyChain
hackathon prototype.

The backend already exists separately:

    FastAPI
        ↓
    http://127.0.0.1:8000


This Streamlit application does NOT store hive data itself.

Instead, it asks the FastAPI backend for information.

Architecture:

    Hive Simulator
         ↓
      FastAPI
         ↓
    HoneyChain API
         ↓
     Streamlit
         ↓
      Browser


WHY STREAMLIT FOR THE PROTOTYPE?
--------------------------------

For the hackathon prototype we need:

    - a working interface TODAY
    - live telemetry
    - charts
    - verification pages
    - buttons and workflows
    - minimal frontend complexity

Streamlit lets us build all of those directly in Python.

A future production implementation could replace Streamlit
with React/Next.js without changing the FastAPI backend.
"""


# ============================================================
# 1. IMPORTS
# ============================================================

# Streamlit builds the web interface.
import streamlit as st


# requests allows this frontend to communicate with FastAPI.
import requests


# pandas helps us organise time-series telemetry.
import pandas as pd


# Plotly creates interactive charts.
import plotly.express as px


# datetime is used later for timestamp formatting.
from datetime import datetime


# ============================================================
# 2. APPLICATION CONFIGURATION
# ============================================================

# This controls the browser-tab title and page layout.
#
# layout="wide"
#
# gives us more horizontal space for dashboard cards.
#
st.set_page_config(
    page_title="HoneyChain",
    page_icon="🍯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 3. BACKEND CONFIGURATION
# ============================================================

# This is the FastAPI server we already created.
#
API_BASE_URL = "http://127.0.0.1:8000"


# For today's prototype, this is our software-simulated hive.
#
DEMO_HIVE_ID = "IN-WB-001"


# ============================================================
# 4. VISUAL DESIGN
# ============================================================

# Streamlit provides default styling.
#
# We add a small amount of CSS so HoneyChain looks like a
# deliberate product rather than a default Python dashboard.
#
# IMPORTANT:
# This CSS changes presentation only.
# It does not affect any data or business logic.
#
st.markdown(
    """
    <style>

    /* ------------------------------------------------------
       MAIN PAGE
       ------------------------------------------------------ */

    .stApp {
        background:
            linear-gradient(
                180deg,
                #FBFAF7 0%,
                #F7F3EA 100%
            );
    }


    /* ------------------------------------------------------
       REMOVE EXCESS TOP SPACE
       ------------------------------------------------------ */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* ------------------------------------------------------
       BRAND LABEL
       ------------------------------------------------------ */

    .brand {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.18rem;
        color: #9A6A16;
        margin-bottom: 0.4rem;
    }


    /* ------------------------------------------------------
       MAIN TITLE
       ------------------------------------------------------ */

    .hero-title {
        font-size: 2.7rem;
        line-height: 1.05;
        font-weight: 750;
        color: #202020;
        margin-bottom: 0.7rem;
    }


    /* ------------------------------------------------------
       SUPPORTING TEXT
       ------------------------------------------------------ */

    .hero-subtitle {
        font-size: 1.05rem;
        color: #66615B;
        max-width: 750px;
        margin-bottom: 2rem;
    }


    /* ------------------------------------------------------
       SMALL LIVE INDICATOR
       ------------------------------------------------------ */

    .live-badge {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: #E8F3EB;
        color: #357047;
        font-size: 0.78rem;
        font-weight: 700;
    }


    /* ------------------------------------------------------
       SECTION HEADINGS
       ------------------------------------------------------ */

    .section-label {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.08rem;
        color: #807970;
        margin-top: 1.5rem;
        margin-bottom: 0.7rem;
    }


    /* ------------------------------------------------------
       STATUS CARD
       ------------------------------------------------------ */

    .status-card {
        padding: 1.2rem 1.4rem;
        border-radius: 16px;
        background: white;
        border: 1px solid #E7E1D7;
        box-shadow:
            0 6px 20px
            rgba(30, 25, 20, 0.04);
        margin-bottom: 1rem;
    }


    /* ==========================================================
       STREAMLIT TEXT + METRIC FIX
       ========================================================== */

    /*
    Streamlit may inherit dark-mode text colors from the browser
    or operating system.

    Because HoneyChain deliberately uses a light cream background,
    we explicitly set readable text colors.
    */


    /* ----------------------------------------------------------
       GENERAL PAGE TEXT
       ---------------------------------------------------------- */

    [data-testid="stAppViewContainer"] {
        color: #26231F;
    }


    /* ----------------------------------------------------------
       METRIC CARDS
       ---------------------------------------------------------- */

    /*
    These are the cards showing:

        Inside temperature
        Humidity
        Hive weight
        Readings received
    */

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E7E1D7;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        box-shadow: 0 6px 18px rgba(30, 25, 20, 0.04);
    }


    /* Metric label:
       e.g. "Inside temperature"
    */

    [data-testid="stMetricLabel"] {
        color: #716A61 !important;
    }

    [data-testid="stMetricLabel"] p {
        color: #716A61 !important;
        font-weight: 600 !important;
    }


    /* Metric value:
       e.g. "34.4 °C"
    */

    [data-testid="stMetricValue"] {
        color: #24211E !important;
    }

    [data-testid="stMetricValue"] div {
        color: #24211E !important;
    }


    /* ----------------------------------------------------------
       CAPTIONS
       ---------------------------------------------------------- */

    [data-testid="stCaptionContainer"] {
        color: #777068 !important;
    }


    /* ----------------------------------------------------------
       ACTIVE-HIVE CARD TEXT
       ---------------------------------------------------------- */

    .status-card {
        color: #2A2723;
    }

    .status-card b {
        color: #24211E;
        font-size: 1.05rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 5. API HELPER FUNCTIONS
# ============================================================

def get_hive_summary():
    """
    Request the compact hive summary from FastAPI.

    Backend endpoint:

        GET /api/hives/IN-WB-001/summary

    The summary endpoint is intentionally small because the
    dashboard does not need every historical sensor record just
    to show the latest state.

    It returns information such as:

        - latest temperature
        - latest humidity
        - latest hive weight
        - number of readings received
        - timestamp of the newest reading
    """

    url = (
        f"{API_BASE_URL}"
        f"/api/hives/{DEMO_HIVE_ID}/summary"
    )

    try:
        response = requests.get(
            url,
            timeout=5
        )

        # Any 4xx/5xx response becomes a Python exception.
        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        st.error(
            "HoneyChain cannot reach the backend API. "
            "Make sure FastAPI is running."
        )

        st.caption(
            f"Technical detail: {error}"
        )

        return None


def get_sensor_readings():
    """
    Retrieve the raw telemetry history for the demo hive.

    Backend endpoint:

        GET /api/hives/IN-WB-001/sensor-readings

    The Hive Monitor uses these readings to draw live charts.
    """

    url = (
        f"{API_BASE_URL}"
        f"/api/hives/{DEMO_HIVE_ID}/sensor-readings"
    )

    try:
        response = requests.get(
            url,
            timeout=5
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        st.error(
            "Could not retrieve hive telemetry."
        )

        st.caption(
            f"Technical detail: {error}"
        )

        return []


# ============================================================
# 6. LIVE OVERVIEW COMPONENT
# ============================================================

@st.fragment(run_every="5s")
def render_live_overview():
    """
    Render ONLY the changing telemetry area of the Overview page.

    WHY A STREAMLIT FRAGMENT?
    -------------------------

    The hive simulator currently sends a new reading every
    five seconds.

    Without this fragment, the browser would keep showing the
    old values until somebody manually refreshed the page.

    run_every="5s" tells Streamlit:

        every five seconds
            ↓
        rerun this function
            ↓
        ask FastAPI for the newest hive summary
            ↓
        redraw only this live section

    The rest of the page does not need a full browser refresh.
    """

    summary = get_hive_summary()

    if summary is None:
        return

    latest = summary.get("latest")

    if latest is None:
        st.warning(
            "The hive is registered, but no telemetry has "
            "arrived yet. Start the simulator."
        )
        return

    # --------------------------------------------------------
    # LIVE STATUS
    # --------------------------------------------------------

    st.markdown(
        '<span class="live-badge">'
        '● LIVE SIMULATION'
        '</span>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-label">'
        'CURRENT HIVE STATE'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # TELEMETRY CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Inside temperature",
            value=f"{latest['inside_temperature_c']:.1f} °C"
        )

    with col2:
        st.metric(
            label="Humidity",
            value=f"{latest['humidity_pct']:.1f} %"
        )

    with col3:
        st.metric(
            label="Hive weight",
            value=f"{latest['weight_kg']:.2f} kg"
        )

    with col4:
        st.metric(
            label="Readings received",
            value=summary["reading_count"]
        )

    # --------------------------------------------------------
    # HIVE INFORMATION
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-label">'
        'ACTIVE HIVE'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="status-card">

        <b>West Bengal Demo Hive</b><br>

        <span style="color:#777;">
        {DEMO_HIVE_ID}
        · Apis cerana
        · Humid subtropical profile
        </span>

        <br><br>

        <span style="color:#9A6A16;">
        ● Simulated demonstration telemetry
        </span>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Latest telemetry received: "
        f"{latest['timestamp']}"
    )


# ============================================================
# 7. LIVE HIVE MONITOR COMPONENT
# ============================================================

@st.fragment(run_every="5s")
def render_live_monitor():
    """
    Draw the telemetry charts and refresh them automatically.

    Every five seconds this fragment:

        1. Requests the current sensor-reading history.
        2. Converts the JSON records into a pandas DataFrame.
        3. Rebuilds the three charts.
        4. Replaces only this section of the page.

    This means the plotted lines grow as the simulator sends
    new readings, without requiring Ctrl + R.
    """

    readings = get_sensor_readings()

    if len(readings) == 0:
        st.warning(
            "No telemetry available yet. "
            "Start the hive simulator."
        )
        return

    # --------------------------------------------------------
    # CONVERT API JSON INTO A TABLE
    # --------------------------------------------------------

    df = pd.DataFrame(readings)

    # Turn ISO timestamp strings into proper datetime values.
    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    # Sort explicitly so the x-axis always moves forward
    # chronologically, even if data later arrive out of order.
    df = df.sort_values("timestamp")

    # --------------------------------------------------------
    # SMALL LIVE SUMMARY ABOVE THE GRAPHS
    # --------------------------------------------------------

    latest = df.iloc[-1]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Latest inside temperature",
            f"{latest['inside_temperature_c']:.1f} °C"
        )

    with col2:
        st.metric(
            "Latest humidity",
            f"{latest['humidity_pct']:.1f} %"
        )

    with col3:
        st.metric(
            "Telemetry points",
            len(df)
        )

    # --------------------------------------------------------
    # TEMPERATURE CHART
    # --------------------------------------------------------

    temperature_figure = px.line(
        df,
        x="timestamp",
        y=[
            "inside_temperature_c",
            "outside_temperature_c"
        ],
        title="Temperature telemetry"
    )

    temperature_figure.update_layout(
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        legend_title="Signal",
        margin=dict(l=20, r=20, t=55, b=20)
    )

    st.plotly_chart(
        temperature_figure,
        use_container_width=True
    )

    # --------------------------------------------------------
    # HUMIDITY CHART
    # --------------------------------------------------------

    humidity_figure = px.line(
        df,
        x="timestamp",
        y="humidity_pct",
        title="Hive humidity"
    )

    humidity_figure.update_layout(
        xaxis_title="Time",
        yaxis_title="Relative humidity (%)",
        margin=dict(l=20, r=20, t=55, b=20)
    )

    st.plotly_chart(
        humidity_figure,
        use_container_width=True
    )

    # --------------------------------------------------------
    # WEIGHT CHART
    # --------------------------------------------------------

    weight_figure = px.line(
        df,
        x="timestamp",
        y="weight_kg",
        title="Hive weight"
    )

    weight_figure.update_layout(
        xaxis_title="Time",
        yaxis_title="Weight (kg)",
        margin=dict(l=20, r=20, t=55, b=20)
    )

    st.plotly_chart(
        weight_figure,
        use_container_width=True
    )

    # --------------------------------------------------------
    # RAW DATA TABLE
    # --------------------------------------------------------

    with st.expander(
        "View raw telemetry"
    ):
        st.dataframe(
            df,
            use_container_width=True
        )


# ============================================================
# 8. SIDEBAR
# ============================================================

st.sidebar.markdown("## 🍯 HoneyChain")

st.sidebar.caption(
    "Evidence-backed honey intelligence"
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    "<small style='color:#9A938A;'>OPERATOR PROTOTYPE</small>",
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigate",
    [
        "Overview",
        "Hive Monitor",
        "Traceability",
        "Consumer Verify",
        "CloneWatch"
    ]
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Prototype build · Hackathon 2026"
)


# ============================================================
# 9. OVERVIEW PAGE
# ============================================================

if page == "Overview":

    # --------------------------------------------------------
    # STATIC HERO SECTION
    # --------------------------------------------------------
    #
    # This part does not need to refresh every five seconds.
    #
    st.markdown(
        '<div class="brand">HONEYCHAIN</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-title">'
        'From hive signals to trusted honey.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-subtitle">
        A software prototype connecting smart-hive telemetry,
        evidence-backed traceability and package-level
        authenticity verification.
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # DYNAMIC SECTION
    # --------------------------------------------------------
    #
    # This section refreshes itself every five seconds.
    #
    render_live_overview()


# ============================================================
# 10. HIVE MONITOR PAGE
# ============================================================

elif page == "Hive Monitor":

    st.title("Hive Monitor")

    st.caption(
        "Live software-simulated telemetry for IN-WB-001. "
        "Charts refresh automatically every five seconds."
    )

    render_live_monitor()


# ============================================================
# 11. PLACEHOLDER PAGES
# ============================================================

elif page == "Traceability":

    st.title("Traceability")

    st.info(
        "Next module: "
        "Hive → Harvest → Test → Process → Package."
    )


elif page == "Consumer Verify":

    st.title("Consumer Honey Passport")

    st.caption(
        "This will become the public-facing experience opened "
        "when a consumer scans a jar QR code."
    )

    st.info(
        "Next module: package ID lookup, provenance timeline "
        "and authenticity verification."
    )


elif page == "CloneWatch":

    st.title("CloneWatch")

    st.info(
        "Next module: suspicious duplicate-package detection."
    )
