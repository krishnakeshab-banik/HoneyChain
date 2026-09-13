"""
HoneyChain Hive Simulator
=========================

FILE:
    simulator/hive_simulator.py


PURPOSE
-------

This program acts like a SOFTWARE VERSION of a physical smart hive.

In a real deployment, something like this might happen:

    temperature sensor
    humidity sensor
    weighing scale
            ↓
          ESP32
            ↓
        HoneyChain API


We do not have physical hardware.

So, for the hackathon, this Python program replaces the
sensor + ESP32 layer.

It generates simulated hive measurements and sends them to:

    POST /api/sensor-readings


VERY IMPORTANT
--------------

The generated values are DEMONSTRATION DATA.

They are NOT claimed to be real biological measurements
from an Indian honeybee colony.

That is why every generated record is explicitly labelled:

    source = "simulated"


LATER
-----

We can replace this simulator with:

    1. Real German hive telemetry
    2. Another scientific dataset
    3. Real hardware

without changing the main HoneyChain API architecture.
"""


# ============================================================
# 1. IMPORTS
# ============================================================

# random
# ------
# Used to introduce small natural-looking variations between
# consecutive measurements.
#
# We deliberately do NOT generate completely unrelated random
# values each time.
#
# Real sensor measurements usually change gradually.
#
import random


# time
# ----
# Used to pause between measurements.
#
# Example:
#
#     time.sleep(5)
#
# means:
#
#     wait five seconds.
#
import time


# datetime
# --------
# Used to create the timestamp attached to every reading.
#
# timezone.utc makes the timestamp explicit and unambiguous.
#
from datetime import datetime, timezone


# requests
# --------
# Allows this Python program to send an HTTP request to our
# FastAPI backend.
#
# In other words:
#
#     simulator.py
#          ↓
#       requests
#          ↓
#     FastAPI server
#
import requests


# ============================================================
# 2. SIMULATOR CONFIGURATION
# ============================================================

# This is the HoneyChain API endpoint that accepts new
# sensor readings.
#
API_URL = "http://127.0.0.1:8000/api/sensor-readings"


# We deliberately use our simulated Indian hive.
#
# Remember:
#
#     DE-001
#         reserved for real German dataset measurements
#
#     IN-WB-001
#         software simulation / demo hive
#
HIVE_ID = "IN-WB-001"


# How often should the simulator send a reading?
#
# For a real deployment, telemetry might arrive every few
# minutes.
#
# For a live hackathon demo, waiting several minutes would be
# painfully boring.
#
# Therefore we use 5 seconds.
#
SEND_INTERVAL_SECONDS = 5


# ============================================================
# 3. INITIAL SIMULATED HIVE STATE
# ============================================================

# Instead of generating a completely new random measurement
# every five seconds, we keep track of the previous state.
#
# This creates TEMPORAL CONTINUITY.
#
# Example:
#
# Good:
#
#     34.2
#     34.3
#     34.1
#     34.4
#
# Bad:
#
#     34.2
#     12.5
#     57.9
#     3.1
#
#
# These starting values are simply illustrative demo values.
#
state = {
    "inside_temperature_c": 34.2,
    "outside_temperature_c": 31.0,
    "humidity_pct": 68.0,
    "weight_kg": 42.8,
}


# ============================================================
# 4. HELPER FUNCTION: KEEP VALUES INSIDE A RANGE
# ============================================================

def clamp(value, minimum, maximum):
    """
    Prevent a simulated value from leaving an allowed range.

    Example:

        clamp(120, 0, 100)

    returns:

        100


    This protects our simulator from accidentally producing
    impossible values because of accumulated random drift.
    """

    return max(minimum, min(value, maximum))


# ============================================================
# 5. GENERATE ONE NEW SENSOR READING
# ============================================================

def generate_reading():
    """
    Generate ONE new simulated sensor measurement.

    The new value is based on the PREVIOUS value plus a small
    random change.

    This makes the signal behave more like a time series rather
    than a collection of unrelated random numbers.


    IMPORTANT:

    This is not a biological prediction model.

    Its purpose is only to create believable-looking telemetry
    for testing the HoneyChain software pipeline.
    """

    # --------------------------------------------------------
    # INTERNAL TEMPERATURE
    # --------------------------------------------------------
    #
    # random.gauss(mean, standard_deviation)
    #
    # Here:
    #
    #     mean = 0
    #
    # means there is no systematic upward/downward movement.
    #
    #     standard deviation = 0.12
    #
    # means most changes are small.
    #
    state["inside_temperature_c"] += random.gauss(0, 0.12)


    # --------------------------------------------------------
    # OUTSIDE TEMPERATURE
    # --------------------------------------------------------

    state["outside_temperature_c"] += random.gauss(0, 0.18)


    # --------------------------------------------------------
    # HUMIDITY
    # --------------------------------------------------------

    state["humidity_pct"] += random.gauss(0, 0.4)


    # --------------------------------------------------------
    # HIVE WEIGHT
    # --------------------------------------------------------
    #
    # We use tiny short-term changes.
    #
    # Again:
    #
    # THIS IS NOT BEING INTERPRETED AS HONEY PRODUCTION.
    #
    # Hive weight includes:
    #
    #     structure
    #     bees
    #     food stores
    #     brood
    #     water
    #     other material
    #
    state["weight_kg"] += random.gauss(0.002, 0.015)


    # --------------------------------------------------------
    # KEEP VALUES INSIDE SAFE DEMO RANGES
    # --------------------------------------------------------

    state["inside_temperature_c"] = clamp(
        state["inside_temperature_c"],
        30.0,
        38.0
    )

    state["outside_temperature_c"] = clamp(
        state["outside_temperature_c"],
        20.0,
        40.0
    )

    state["humidity_pct"] = clamp(
        state["humidity_pct"],
        40.0,
        90.0
    )

    state["weight_kg"] = clamp(
        state["weight_kg"],
        35.0,
        55.0
    )


    # --------------------------------------------------------
    # CREATE THE JSON OBJECT
    # --------------------------------------------------------
    #
    # requests will later convert this Python dictionary into
    # JSON and send it to FastAPI.
    #
    reading = {

        "hive_id": HIVE_ID,

        # ISO 8601 timestamp.
        #
        # Example:
        #
        # 2026-09-13T08:32:14.123456+00:00
        #
        "timestamp": datetime.now(timezone.utc).isoformat(),

        # round(..., 2)
        #
        # keeps the demo values readable.
        #
        "inside_temperature_c": round(
            state["inside_temperature_c"],
            2
        ),

        "outside_temperature_c": round(
            state["outside_temperature_c"],
            2
        ),

        "humidity_pct": round(
            state["humidity_pct"],
            2
        ),

        "weight_kg": round(
            state["weight_kg"],
            3
        ),

        # Provenance remains explicit.
        "source": "simulated",
    }

    return reading


# ============================================================
# 6. SEND ONE READING TO HONEYCHAIN
# ============================================================

def send_reading(reading):
    """
    Send one sensor reading to the HoneyChain FastAPI backend.

    The request looks conceptually like:

        simulator
            ↓
        HTTP POST
            ↓
        /api/sensor-readings
            ↓
        FastAPI
            ↓
        Pydantic validation
            ↓
        sensor_store
    """

    try:

        # requests.post(...)
        #
        # sends an HTTP POST request.
        #
        # json=reading
        #
        # automatically converts our Python dictionary into
        # JSON.
        #
        # timeout=5
        #
        # means:
        #
        # do not wait forever if the backend is unavailable.
        #
        response = requests.post(
            API_URL,
            json=reading,
            timeout=5
        )


        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        if response.status_code == 201:

            print(
                f"[SENT] "
                f"{reading['timestamp']} | "
                f"Inside: {reading['inside_temperature_c']} °C | "
                f"Outside: {reading['outside_temperature_c']} °C | "
                f"Humidity: {reading['humidity_pct']} % | "
                f"Weight: {reading['weight_kg']} kg"
            )


        # ----------------------------------------------------
        # API REJECTED THE DATA
        # ----------------------------------------------------

        else:

            print(
                f"[API ERROR] "
                f"Status code: {response.status_code}"
            )

            print(
                f"Response: {response.text}"
            )


    # --------------------------------------------------------
    # NETWORK / SERVER ERROR
    # --------------------------------------------------------
    #
    # Example:
    #
    # FastAPI server is not running.
    #
    except requests.RequestException as error:

        print(
            "[CONNECTION ERROR] "
            "Could not send reading to HoneyChain."
        )

        print(
            f"Technical detail: {error}"
        )


# ============================================================
# 7. MAIN SIMULATOR LOOP
# ============================================================

def run_simulator():
    """
    Continuously generate and transmit sensor readings.

    The loop continues until the user presses:

        Ctrl + C
    """

    print()
    print("============================================")
    print("       HoneyChain Hive Simulator")
    print("============================================")
    print()
    print(f"Hive: {HIVE_ID}")
    print(f"API:  {API_URL}")
    print(
        f"Sending one reading every "
        f"{SEND_INTERVAL_SECONDS} seconds."
    )
    print()
    print("Press Ctrl + C to stop the simulator.")
    print()


    try:

        # `while True` means:
        #
        # keep repeating forever.
        #
        # This is appropriate here because a real sensor would
        # also keep producing measurements continuously.
        #
        while True:

            # Step 1:
            # Generate one new simulated measurement.
            #
            reading = generate_reading()


            # Step 2:
            # Send it to FastAPI.
            #
            send_reading(reading)


            # Step 3:
            # Wait before generating the next measurement.
            #
            time.sleep(SEND_INTERVAL_SECONDS)


    except KeyboardInterrupt:

        # KeyboardInterrupt happens when the user presses:
        #
        #     Ctrl + C
        #
        print()
        print("HoneyChain simulator stopped safely.")


# ============================================================
# 8. PROGRAM ENTRY POINT
# ============================================================

# This line means:
#
# "Only start the simulator automatically when this file is
# executed directly."
#
#
# Example:
#
#     python simulator/hive_simulator.py
#
#
# If some other Python file IMPORTS this file later,
# the simulator will not unexpectedly start running.
#
if __name__ == "__main__":
    run_simulator()