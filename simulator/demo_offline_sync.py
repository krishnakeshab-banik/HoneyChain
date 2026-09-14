"""Demonstrate the offline queue then a lossless, de-duplicated sync.

Usage (backend must be running):

    python simulator/demo_offline_sync.py
"""

from __future__ import annotations

import time

import requests

from simulator.hive_simulator import (
    API_URL,
    HIVE_ID,
    _flush_queue,
    _load_queue,
    _save_queue,
    generate_reading,
    write_control,
)

STATS = "http://127.0.0.1:8000/api/hives/IN-WB-001/sensor-readings"


def _count() -> int:
    response = requests.get(STATS, timeout=5)
    response.raise_for_status()
    return len(response.json())


def main() -> None:
    write_control("offline")
    _save_queue([])
    before = _count()
    print(f"Readings on {HIVE_ID} before demo: {before}")
    print("Forcing OFFLINE and generating 4 queued readings...")
    queued = [generate_reading(HIVE_ID) for _ in range(4)]
    _save_queue(queued)
    print(f"Queue size: {len(_load_queue())}")
    mid = _count()
    if mid != before:
        raise SystemExit("Queue leaked into the API while offline.")
    print("Forcing ONLINE and flushing the queue...")
    write_control("online")
    _flush_queue()
    # Replay the same timestamps — store_reading must not duplicate.
    _save_queue(queued)
    _flush_queue()
    time.sleep(0.3)
    after = _count()
    leftover = _load_queue()
    print(f"Readings after sync: {after} (expected {before + 4})")
    print(f"Queue leftover: {len(leftover)}")
    write_control("auto")
    if leftover:
        raise SystemExit("Queue did not drain.")
    if after != before + 4:
        raise SystemExit(f"Expected {before + 4} readings, got {after}.")
    print("Offline/sync cycle OK: no loss, no duplication.")


if __name__ == "__main__":
    main()
