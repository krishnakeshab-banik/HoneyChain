"""
HoneyChain Hive Simulator
=========================

FILE:
    simulator/hive_simulator.py

Extended, not replaced. IN-WB-001 still emits drifted readings every
5 seconds. DE-001 is now a second independently drifting hive so it is
no longer a dead registered entity.

Offline/online cycles: when a hive is "offline", readings go into a
local queue and flush as a batch when the link returns. That is still
simulated connectivity, not a real ESP32 buffer.
"""

from __future__ import annotations

import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

API_URL = "http://127.0.0.1:8000/api/sensor-readings"
HIVE_ID = "IN-WB-001"
SEND_INTERVAL_SECONDS = 5
QUEUE_PATH = Path(__file__).resolve().parent.parent / "data" / "simulator_queue.json"
CONTROL_PATH = Path(__file__).resolve().parent.parent / "data" / "simulator_control.json"
OFFLINE_FLIP_CHANCE = 0.10

HiveState = dict[str, float]

HIVE_PROFILES: dict[str, dict[str, Any]] = {
    "IN-WB-001": {
        "state": {
            "inside_temperature_c": 34.2,
            "outside_temperature_c": 31.0,
            "humidity_pct": 68.0,
            "weight_kg": 42.8,
        },
        "ranges": {
            "inside_temperature_c": (30.0, 38.0),
            "outside_temperature_c": (20.0, 40.0),
            "humidity_pct": (40.0, 90.0),
            "weight_kg": (35.0, 55.0),
        },
        "online": True,
    },
    "DE-001": {
        "state": {
            "inside_temperature_c": 33.4,
            "outside_temperature_c": 16.5,
            "humidity_pct": 58.0,
            "weight_kg": 44.1,
        },
        "ranges": {
            "inside_temperature_c": (30.0, 37.0),
            "outside_temperature_c": (8.0, 28.0),
            "humidity_pct": (40.0, 85.0),
            "weight_kg": (36.0, 54.0),
        },
        "online": True,
    },
    "IN-WB-002": {
        "state": {
            "inside_temperature_c": 34.6,
            "outside_temperature_c": 30.4,
            "humidity_pct": 71.0,
            "weight_kg": 41.2,
        },
        "ranges": {
            "inside_temperature_c": (30.0, 38.0),
            "outside_temperature_c": (20.0, 40.0),
            "humidity_pct": (40.0, 90.0),
            "weight_kg": (35.0, 55.0),
        },
        "online": True,
    },
    "IN-WB-003": {
        "state": {
            "inside_temperature_c": 33.8,
            "outside_temperature_c": 29.8,
            "humidity_pct": 74.0,
            "weight_kg": 43.5,
        },
        "ranges": {
            "inside_temperature_c": (30.0, 38.0),
            "outside_temperature_c": (20.0, 40.0),
            "humidity_pct": (40.0, 90.0),
            "weight_kg": (35.0, 55.0),
        },
        "online": True,
    },
    "IN-KA-001": {
        "state": {
            "inside_temperature_c": 34.0,
            "outside_temperature_c": 26.0,
            "humidity_pct": 64.0,
            "weight_kg": 40.6,
        },
        "ranges": {
            "inside_temperature_c": (30.0, 38.0),
            "outside_temperature_c": (16.0, 34.0),
            "humidity_pct": (40.0, 88.0),
            "weight_kg": (35.0, 52.0),
        },
        "online": True,
    },
}

# Backwards-compatible alias used by the original single-hive loop.
state: HiveState = HIVE_PROFILES[HIVE_ID]["state"]


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def generate_reading(hive_id: str | None = None) -> dict[str, Any]:
    """Generate one drifted reading. Default hive remains IN-WB-001."""

    target_id = hive_id or HIVE_ID
    profile = HIVE_PROFILES[target_id]
    hive_state: HiveState = profile["state"]
    ranges: dict[str, tuple[float, float]] = profile["ranges"]

    hive_state["inside_temperature_c"] += random.gauss(0, 0.12)
    hive_state["outside_temperature_c"] += random.gauss(0, 0.18)
    hive_state["humidity_pct"] += random.gauss(0, 0.4)
    hive_state["weight_kg"] += random.gauss(0.002, 0.015)

    for key, (low, high) in ranges.items():
        hive_state[key] = clamp(hive_state[key], low, high)

    return {
        "hive_id": target_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inside_temperature_c": round(hive_state["inside_temperature_c"], 2),
        "outside_temperature_c": round(hive_state["outside_temperature_c"], 2),
        "humidity_pct": round(hive_state["humidity_pct"], 2),
        "weight_kg": round(hive_state["weight_kg"], 3),
        "source": "simulated",
    }


def _load_queue() -> list[dict[str, Any]]:
    if not QUEUE_PATH.is_file():
        return []
    try:
        loaded = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return loaded if isinstance(loaded, list) else []


def _save_queue(queue: list[dict[str, Any]]) -> None:
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_PATH.write_text(json.dumps(queue, indent=2), encoding="utf-8")


def send_reading(reading: dict[str, Any]) -> bool:
    try:
        response = requests.post(API_URL, json=reading, timeout=5)
        if response.status_code == 201:
            print(
                f"[SENT] {reading['hive_id']} | "
                f"{reading['timestamp']} | "
                f"Inside: {reading['inside_temperature_c']} °C | "
                f"Humidity: {reading['humidity_pct']} % | "
                f"Weight: {reading['weight_kg']} kg"
            )
            return True
        print(f"[API ERROR] Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    except requests.RequestException as error:
        print("[CONNECTION ERROR] Could not send reading to HoneyChain.")
        print(f"Technical detail: {error}")
        return False


def read_control() -> dict[str, Any]:
    if not CONTROL_PATH.is_file():
        return {"mode": "auto"}
    try:
        loaded = json.loads(CONTROL_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"mode": "auto"}
    return loaded if isinstance(loaded, dict) else {"mode": "auto"}


def write_control(mode: str) -> None:
    CONTROL_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTROL_PATH.write_text(json.dumps({"mode": mode}, indent=2), encoding="utf-8")


def _forced_online() -> bool | None:
    mode = str(read_control().get("mode") or "auto").lower()
    if mode == "offline":
        return False
    if mode == "online":
        return True
    return None


def _maybe_flip_link(hive_id: str) -> None:
    forced = _forced_online()
    if forced is not None:
        previous = bool(HIVE_PROFILES[hive_id]["online"])
        HIVE_PROFILES[hive_id]["online"] = forced
        if previous != forced:
            print(f"[LINK] {hive_id} forced {'ONLINE' if forced else 'OFFLINE'} by simulator_control.json")
        return
    if random.random() < OFFLINE_FLIP_CHANCE:
        HIVE_PROFILES[hive_id]["online"] = not HIVE_PROFILES[hive_id]["online"]
        state_label = "ONLINE" if HIVE_PROFILES[hive_id]["online"] else "OFFLINE"
        print(f"[LINK] {hive_id} is now {state_label}")


def _flush_queue() -> None:
    queue = _load_queue()
    if not queue:
        return
    remaining: list[dict[str, Any]] = []
    print(f"[SYNC] Flushing {len(queue)} queued reading(s).")
    for item in queue:
        if not send_reading(item):
            remaining.append(item)
    _save_queue(remaining)


def dispatch_reading(reading: dict[str, Any]) -> None:
    hive_id = reading["hive_id"]
    _maybe_flip_link(hive_id)
    online = bool(HIVE_PROFILES[hive_id]["online"])
    if not online:
        queue = _load_queue()
        queue.append(reading)
        _save_queue(queue)
        print(f"[OFFLINE] Queued reading for {hive_id}. Queue size: {len(queue)}")
        return
    _flush_queue()
    if not send_reading(reading):
        queue = _load_queue()
        queue.append(reading)
        _save_queue(queue)


def run_simulator() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Stream synthetic hive telemetry.")
    parser.add_argument("--mode", choices=["auto", "online", "offline"], default=None)
    args = parser.parse_args()
    if args.mode:
        write_control(args.mode)

    print()
    print("============================================")
    print("       HoneyChain Hive Simulator")
    print("============================================")
    print()
    print(f"Hives: {', '.join(HIVE_PROFILES)}")
    print(f"API:  {API_URL}")
    print(f"Link mode: {read_control().get('mode', 'auto')}")
    print(f"Sending one reading per hive every {SEND_INTERVAL_SECONDS} seconds.")
    print("Offline readings are queued locally and flushed on reconnect.")
    print("Force the link with --mode online|offline or data/simulator_control.json")
    print()
    print("Press Ctrl + C to stop the simulator.")
    print()

    try:
        while True:
            for hive_id in HIVE_PROFILES:
                dispatch_reading(generate_reading(hive_id))
            time.sleep(SEND_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print()
        print("HoneyChain simulator stopped safely.")


if __name__ == "__main__":
    run_simulator()
