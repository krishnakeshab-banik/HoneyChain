"""python -m backend.seed [--reset]"""

from __future__ import annotations

import argparse

from backend.database import SessionLocal, init_db
from backend.seed.story import reset_demo_story, seed_demo_story


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply or reset the one-time HoneyChain demo seed.")
    parser.add_argument("--reset", action="store_true", help="Remove demo-tagged rows, then reseed.")
    args = parser.parse_args()
    init_db()
    session = SessionLocal()
    try:
        if args.reset:
            reset_demo_story(session)
        seed_demo_story(session)
        session.commit()
        print("Demo seed applied. Later harvests, scans, and readings are live.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
