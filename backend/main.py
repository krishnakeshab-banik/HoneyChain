"""
HoneyChain Backend
==================

FILE:
    backend/main.py


WHAT IS THIS FILE?
------------------

This file is the ENTRY POINT of the HoneyChain backend.

When we start HoneyChain's Python server, FastAPI will load
the variable named:

    app

from this file.


RIGHT NOW OUR BACKEND IS TINY.

It can only answer two questions:

    1. "Is HoneyChain running?"
    2. "Is the backend healthy?"


LATER THIS SAME BACKEND WILL HANDLE:

    - hive information
    - sensor readings
    - machine-learning predictions
    - harvest creation
    - honey batches
    - laboratory certificates
    - package identities
    - QR scans
    - counterfeit detection
    - blockchain verification


IMPORTANT:
We deliberately start with a tiny working system rather than
trying to build everything at once.
"""


# ============================================================
# 1. IMPORT FASTAPI
# ============================================================

# FastAPI is a Python framework for building web APIs.
#
# An API allows different parts of our system to communicate.
#
# Eventually:
#
#     Website
#         ↓
#     FastAPI
#         ↓
#     Database / AI / Blockchain
#
from fastapi import FastAPI,  HTTPException
from backend.models import Hive, SensorReading


# ============================================================
# 2. CREATE THE HONEYCHAIN APPLICATION
# ============================================================

# `app` represents our backend web application.
#
# Later we will attach many API routes to this object.
#
# Examples:
#
#     GET  /api/hives
#     POST /api/harvests
#     GET  /api/batches/HC-001
#
app = FastAPI(
    title="HoneyChain API",

    description=(
        "Backend API for HoneyChain, "
        "a smart beekeeping and honey traceability platform."
    ),

    version="0.1.0",
)
# ============================================================
# TEMPORARY DEVELOPMENT DATABASE
# ============================================================

# For the moment, we are NOT using PostgreSQL.
#
# Instead, we store our hives inside a normal Python dictionary.
#
# This lets us learn and test the API first.
#
# Example structure:
#
# {
#     "DE-001": Hive(...),
#     "IN-WB-001": Hive(...)
# }
#
#
# IMPORTANT:
#
# This data exists only while the server is running.
#
# If the server completely restarts, newly created hives
# disappear.
#
# That is intentional for this development stage.
#
# Later:
#
#     hive_store
#
# will be replaced by:
#
#     PostgreSQL
#
hive_store: dict[str, Hive] = {}

# ============================================================
# TEMPORARY SENSOR DATA STORE
# ============================================================

# This dictionary stores time-series measurements for each hive.
#
# Structure:
#
# {
#     "DE-001": [
#         SensorReading(...),
#         SensorReading(...),
#         SensorReading(...)
#     ],
#
#     "IN-WB-001": [
#         SensorReading(...),
#         SensorReading(...)
#     ]
# }
#
#
# Each hive ID points to a LIST because one hive can produce
# many measurements over time.
#
# This is temporary in-memory storage.
#
# Later PostgreSQL will replace this dictionary.

sensor_store: dict[str, list[SensorReading]] = {}

# ============================================================
# INITIAL DEMONSTRATION HIVES
# ============================================================

# These records allow us to test the API immediately.
#
# Later, real hive metadata will be imported from datasets
# or created through the application.

hive_store["DE-001"] = Hive(
    hive_id="DE-001",
    name="Bremen Demonstration Hive",
    country="Germany",
    region="Bremen",
    bee_species="Apis mellifera",
    climate_zone="temperate",
    data_source="real_dataset",
    source_reference="German Smart Beehive Dataset",
    active=True
)


hive_store["IN-WB-001"] = Hive(
    hive_id="IN-WB-001",
    name="West Bengal Demo Hive",
    country="India",
    region="West Bengal",
    bee_species="Apis cerana",
    climate_zone="humid_subtropical",
    data_source="simulated",
    source_reference="HoneyChain Simulator",
    active=True
)

# ============================================================
# 3. ROOT ENDPOINT
# ============================================================

# The line:
#
#     @app.get("/")
#
# means:
#
# "When somebody sends an HTTP GET request to `/`,
# run the Python function immediately below it."
#
#
# Example URL:
#
#     http://127.0.0.1:8000/
#

@app.get("/")
def root():
    """
    Basic HoneyChain status endpoint.

    This function returns a Python dictionary.

    FastAPI automatically converts that dictionary into JSON
    before sending it to the browser.
    """

    return {
        "project": "HoneyChain",
        "version": "0.1.0",
        "status": "running",
        "message": "HoneyChain backend is alive."
    }


# ============================================================
# 4. HEALTH-CHECK ENDPOINT
# ============================================================

# Real software systems commonly expose something called a
# "health endpoint".
#
# It allows developers or cloud services to ask:
#
#     "Is this server functioning?"
#
#
# Right now we only return:
#
#     healthy
#
#
# Later this endpoint could check:
#
#     - database connection
#     - machine-learning model availability
#     - blockchain connection
#
@app.get("/health")
def health_check():
    """
    Check whether the HoneyChain backend is running.
    """

    return {
        "status": "healthy"
    }

# ============================================================
# GET ALL HIVES
# ============================================================

@app.get("/api/hives")
def get_all_hives():
    """
    Return every hive currently registered in HoneyChain.

    HTTP method:
        GET

    Endpoint:
        /api/hives

    Purpose:
        The frontend dashboard will eventually call this
        endpoint to display all available hives.
    """

    # hive_store.values() gives us all Hive objects stored
    # inside the dictionary.
    #
    # list(...) converts those values into a normal Python list
    # that FastAPI can return as JSON.
    return list(hive_store.values())

# ============================================================
# ADD A SENSOR READING
# ============================================================

@app.post("/api/sensor-readings", status_code=201)
def create_sensor_reading(reading: SensorReading):
    """
    Store one sensor reading.

    HTTP method:
        POST

    Endpoint:
        /api/sensor-readings


    Expected workflow:

        sensor / simulator
                ↓
        sends JSON reading
                ↓
        FastAPI
                ↓
        Pydantic validation
                ↓
        HoneyChain stores reading


    Example request:

        {
            "hive_id": "DE-001",
            "timestamp": "2026-09-13T10:30:00",
            "inside_temperature_c": 34.2,
            "outside_temperature_c": 22.5,
            "humidity_pct": 61.4,
            "weight_kg": 46.8,
            "source": "simulated"
        }
    """


    # --------------------------------------------------------
    # CHECK THAT THE HIVE ACTUALLY EXISTS
    # --------------------------------------------------------

    # We do not want sensor measurements belonging to a hive
    # that HoneyChain has never heard of.
    #
    # Example of BAD data:
    #
    #     hive_id = "MAGIC-HIVE-999"
    #
    # if that hive was never registered.

    if reading.hive_id not in hive_store:
        raise HTTPException(
            status_code=404,
            detail=f"Hive '{reading.hive_id}' does not exist."
        )


    # --------------------------------------------------------
    # CREATE A LIST FOR THIS HIVE IF NECESSARY
    # --------------------------------------------------------

    # The first time DE-001 sends a reading,
    #
    # sensor_store may not yet contain:
    #
    #     "DE-001"
    #
    # So we create an empty list.

    if reading.hive_id not in sensor_store:
        sensor_store[reading.hive_id] = []


    # --------------------------------------------------------
    # SAVE THE READING
    # --------------------------------------------------------

    sensor_store[reading.hive_id].append(reading)


    # --------------------------------------------------------
    # RETURN CONFIRMATION
    # --------------------------------------------------------

    return {
        "message": "Sensor reading stored successfully.",
        "reading": reading
    }

# ============================================================
# GET SENSOR READINGS FOR ONE HIVE
# ============================================================

@app.get("/api/hives/{hive_id}/sensor-readings")
def get_sensor_readings(hive_id: str):
    """
    Return all sensor readings currently stored for one hive.

    Example:

        GET /api/hives/DE-001/sensor-readings


    Later the frontend will use this endpoint to create:

        temperature charts
        humidity charts
        hive-weight charts
        anomaly visualisations
    """


    # First verify that the hive exists.

    if hive_id not in hive_store:
        raise HTTPException(
            status_code=404,
            detail=f"Hive '{hive_id}' does not exist."
        )


    # If this hive has not produced any sensor readings yet,
    # simply return an empty list instead of throwing an error.

    return sensor_store.get(hive_id, [])

# ============================================================
# HIVE TELEMETRY SUMMARY
# ============================================================

@app.get("/api/hives/{hive_id}/summary")
def get_hive_summary(hive_id: str):
    """
    Return a compact telemetry summary for one hive.

    WHY DOES THIS ENDPOINT EXIST?
    -----------------------------

    The raw sensor endpoint may eventually contain thousands
    or millions of measurements.

    A dashboard usually does NOT need all of them.

    It mainly needs information such as:

        - current temperature
        - current humidity
        - current hive weight
        - how many readings exist
        - when the most recent reading arrived

    Therefore this endpoint creates a lightweight summary.

    Example:

        GET /api/hives/IN-WB-001/summary
    """


    # --------------------------------------------------------
    # STEP 1: VERIFY THE HIVE EXISTS
    # --------------------------------------------------------

    if hive_id not in hive_store:
        raise HTTPException(
            status_code=404,
            detail=f"Hive '{hive_id}' does not exist."
        )


    # --------------------------------------------------------
    # STEP 2: GET ALL READINGS FOR THIS HIVE
    # --------------------------------------------------------

    # If no readings exist, return an empty list.
    #
    readings = sensor_store.get(hive_id, [])


    # --------------------------------------------------------
    # STEP 3: HANDLE THE "NO DATA YET" CASE
    # --------------------------------------------------------

    if len(readings) == 0:

        return {
            "hive_id": hive_id,
            "reading_count": 0,
            "latest": None,
            "message": "No sensor readings available yet."
        }


    # --------------------------------------------------------
    # STEP 4: FIND THE MOST RECENT READING
    # --------------------------------------------------------

    # Because readings are appended in chronological order
    # during the prototype, the final object in the list is
    # the latest one.
    #
    latest = readings[-1]


    # --------------------------------------------------------
    # STEP 5: RETURN A FRONTEND-FRIENDLY SUMMARY
    # --------------------------------------------------------

    return {

        "hive_id": hive_id,

        "reading_count": len(readings),

        "latest": {

            "timestamp": latest.timestamp,

            "inside_temperature_c":
                latest.inside_temperature_c,

            "outside_temperature_c":
                latest.outside_temperature_c,

            "humidity_pct":
                latest.humidity_pct,

            "weight_kg":
                latest.weight_kg,

            "source":
                latest.source
        }
    }