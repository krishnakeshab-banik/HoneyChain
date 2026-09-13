"""
HoneyChain Data Models
======================

FILE:
    backend/models.py


WHY DOES THIS FILE EXIST?
-------------------------

The HoneyChain backend will receive lots of structured data:

    - hives
    - sensor readings
    - harvests
    - honey batches
    - laboratory tests
    - packages
    - QR scans

We need strict rules describing what each type of data
is supposed to look like.

For example:

A hive should have:

    - a unique hive ID
    - a country
    - a bee species
    - a climate zone

We should NOT allow arbitrary or malformed data into the system.

Pydantic gives us this validation layer.


IMPORTANT ARCHITECTURAL RULE
----------------------------

Hive metadata and sensor measurements are DIFFERENT things.

A hive might exist for years.

Its sensor measurements may arrive every few minutes.

Therefore we deliberately DO NOT store temperature, humidity,
or weight directly inside the Hive model.

Those will get their own SensorReading model later.
"""


# ============================================================
# 1. IMPORTS
# ============================================================

# BaseModel is the core Pydantic class used to describe
# structured data.
#
# Any class that inherits from BaseModel automatically gets:
#
#   - data validation
#   - type checking
#   - JSON conversion
#   - automatic API documentation
#
from pydantic import BaseModel, Field
from datetime import datetime


# Literal lets us restrict a field to a known set of values.
#
# Example:
#
# instead of allowing:
#
#     data_source = "whatever"
#
# we can allow only:
#
#     "real_dataset"
#     "simulated"
#     "manual"
#
from typing import Literal


# ============================================================
# 2. HIVE MODEL
# ============================================================

class Hive(BaseModel):
    """
    Represents one beehive registered in HoneyChain.

    This model contains relatively stable information about
    the hive itself.

    It does NOT contain time-series sensor measurements.
    """

    # --------------------------------------------------------
    # UNIQUE HIVE IDENTIFIER
    # --------------------------------------------------------
    #
    # Example:
    #
    #     DE-001
    #     IN-WB-001
    #
    # Every hive in HoneyChain must have an identifier.
    #
    # min_length prevents someone from using something
    # ridiculous like:
    #
    #     hive_id = "x"
    #
    hive_id: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique HoneyChain hive identifier"
    )


    # --------------------------------------------------------
    # DISPLAY NAME
    # --------------------------------------------------------
    #
    # This is a human-friendly label.
    #
    # Example:
    #
    #     "Bremen Hive 01"
    #
    # It does not need to be globally unique.
    #
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Human-readable hive name"
    )


    # --------------------------------------------------------
    # COUNTRY
    # --------------------------------------------------------
    #
    # Examples:
    #
    #     Germany
    #     India
    #
    country: str = Field(
        ...,
        min_length=2,
        max_length=100
    )


    # --------------------------------------------------------
    # REGION
    # --------------------------------------------------------
    #
    # More specific geographical information.
    #
    # Examples:
    #
    #     Bremen
    #     West Bengal
    #
    region: str = Field(
        ...,
        min_length=2,
        max_length=100
    )


    # --------------------------------------------------------
    # BEE SPECIES
    # --------------------------------------------------------
    #
    # We explicitly store species because environmental
    # expectations may differ between populations/species.
    #
    # Examples:
    #
    #     Apis mellifera
    #     Apis cerana
    #
    bee_species: str = Field(
        ...,
        min_length=3,
        max_length=100
    )


    # --------------------------------------------------------
    # CLIMATE ZONE
    # --------------------------------------------------------
    #
    # For the prototype we keep this flexible rather than
    # forcing a complicated scientific climate classification.
    #
    # Examples:
    #
    #     temperate
    #     humid_subtropical
    #     tropical
    #
    climate_zone: str = Field(
        ...,
        min_length=3,
        max_length=100
    )


    # --------------------------------------------------------
    # DATA SOURCE
    # --------------------------------------------------------
    #
    # This is VERY important scientifically.
    #
    # We must distinguish:
    #
    # REAL scientific dataset
    #
    # from
    #
    # simulated data created for demonstration.
    #
    # HoneyChain must never pretend simulated hive measurements
    # are genuine field measurements.
    #
    data_source: Literal[
        "real_dataset",
        "simulated",
        "manual"
    ]


    # --------------------------------------------------------
    # SOURCE REFERENCE
    # --------------------------------------------------------
    #
    # Records where this hive came from.
    #
    # Examples:
    #
    #     "German Smart Beehive Dataset"
    #
    #     "HoneyChain Simulator"
    #
    source_reference: str = Field(
        ...,
        min_length=2,
        max_length=200
    )


    # --------------------------------------------------------
    # ACTIVE STATUS
    # --------------------------------------------------------
    #
    # True:
    #     Hive is currently active.
    #
    # False:
    #     Hive is archived / no longer monitored.
    #
    active: bool = True

    # ============================================================
# 3. SENSOR READING MODEL
# ============================================================

class SensorReading(BaseModel):
    """
    Represents ONE sensor observation from ONE hive.

    Important:
    A hive can have thousands or millions of sensor readings.

    Example:

        Hive DE-001
        2026-09-13 10:00
        34.2 °C
        61.5 % humidity
        46.8 kg

    We deliberately keep this separate from the Hive model
    because hive identity and time-series measurements are
    fundamentally different types of information.
    """


    # --------------------------------------------------------
    # HIVE IDENTIFIER
    # --------------------------------------------------------
    #
    # This tells us which hive produced the reading.
    #
    # Example:
    #
    #     DE-001
    #
    hive_id: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="ID of the hive that produced this reading"
    )


    # --------------------------------------------------------
    # TIMESTAMP
    # --------------------------------------------------------
    #
    # datetime allows FastAPI/Pydantic to understand proper
    # date/time values.
    #
    # Example JSON:
    #
    #     "2026-09-13T10:30:00"
    #
    timestamp: datetime


    # --------------------------------------------------------
    # INTERNAL HIVE TEMPERATURE
    # --------------------------------------------------------
    #
    # We use Celsius.
    #
    # The bounds here are deliberately broad.
    #
    # These are data-validation limits, NOT biological
    # "healthy hive" thresholds.
    #
    # Biological interpretation will happen later in the
    # analytics / ML layer.
    #
    inside_temperature_c: float = Field(
        ...,
        ge=-40,
        le=85,
        description="Internal hive temperature in degrees Celsius"
    )


    # --------------------------------------------------------
    # OUTSIDE TEMPERATURE
    # --------------------------------------------------------
    #
    # This gives environmental context.
    #
    outside_temperature_c: float = Field(
        ...,
        ge=-50,
        le=60,
        description="Outside temperature in degrees Celsius"
    )


    # --------------------------------------------------------
    # RELATIVE HUMIDITY
    # --------------------------------------------------------
    #
    # Relative humidity must logically lie between:
    #
    #     0% and 100%
    #
    humidity_pct: float = Field(
        ...,
        ge=0,
        le=100,
        description="Relative humidity percentage"
    )


    # --------------------------------------------------------
    # HIVE WEIGHT
    # --------------------------------------------------------
    #
    # The total measured hive weight.
    #
    # This may include:
    #
    #     hive box
    #     bees
    #     brood
    #     stored honey
    #
    # It is NOT automatically equivalent to honey yield.
    #
    weight_kg: float = Field(
        ...,
        gt=0,
        le=500,
        description="Measured total hive weight in kilograms"
    )


    # --------------------------------------------------------
    # DATA SOURCE
    # --------------------------------------------------------
    #
    # Again we keep provenance explicit.
    #
    # Later this allows us to distinguish:
    #
    #     real dataset
    #     simulator
    #     live field hardware
    #
    source: Literal[
        "real_dataset",
        "simulated",
        "manual"
    ]