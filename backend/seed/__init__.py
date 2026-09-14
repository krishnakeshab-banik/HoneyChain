"""One-time synthetic demo seed. Separate from live writes after first boot."""

from backend.seed.story import reset_demo_story, seed_demo_story

__all__ = ["seed_demo_story", "reset_demo_story"]
