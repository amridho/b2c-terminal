"""
Hostility Controller
Phase 3 — Central control for feed failure mode simulation

Governance constraints:
- No randomness
- No retries
- No auto-recovery
- Manual selection only
- Active mode visible to UI
"""

import json
from pathlib import Path
from typing import Literal

from stubs import price_feed_stub, visibility_feed_stub, input_proxy_feed_stub

ObservationStatus = Literal["observed", "missing", "blocked", "stale"]
FeedName = Literal["price_feed", "visibility_feed", "input_proxy_feed"]

CONFIG_PATH = Path(__file__).parent / "hostility_config.json"


class HostilityController:
    """
    Central controller for hostility simulation.
    Manages failure modes across all feeds.
    No randomness. No retries. Manual selection only.
    """

    FEED_STUBS = {
        "price_feed": price_feed_stub,
        "visibility_feed": visibility_feed_stub,
        "input_proxy_feed": input_proxy_feed_stub,
    }

    def __init__(self, config_path: Path = CONFIG_PATH):
        self._config_path = config_path
        self._config = self._load_config()
        self._apply_config()

    def _load_config(self) -> dict:
        """Load configuration from JSON file."""
        if self._config_path.exists():
            with open(self._config_path, "r") as f:
                return json.load(f)
        return {"feeds": {}}

    def _save_config(self) -> None:
        """Persist configuration to JSON file."""
        with open(self._config_path, "w") as f:
            json.dump(self._config, f, indent=2)

    def _apply_config(self) -> None:
        """Apply configured failure modes to all feeds."""
        for feed_name, stub_module in self.FEED_STUBS.items():
            feed_config = self._config.get("feeds", {}).get(feed_name, {})
            mode = feed_config.get("failure_mode", "observed")
            stub_module.set_failure_mode(mode)

    def set_failure_mode(self, feed_name: FeedName, mode: ObservationStatus) -> None:
        """
        Set failure mode for a specific feed.
        Updates both runtime state and persistent config.
        """
        if feed_name not in self.FEED_STUBS:
            raise ValueError(f"Unknown feed: {feed_name}")
        if mode not in ("observed", "missing", "blocked", "stale"):
            raise ValueError(f"Invalid failure mode: {mode}")

        # Update runtime
        self.FEED_STUBS[feed_name].set_failure_mode(mode)

        # Update config
        if "feeds" not in self._config:
            self._config["feeds"] = {}
        if feed_name not in self._config["feeds"]:
            self._config["feeds"][feed_name] = {}
        self._config["feeds"][feed_name]["failure_mode"] = mode
        self._save_config()

    def get_failure_mode(self, feed_name: FeedName) -> ObservationStatus:
        """Get current failure mode for a specific feed."""
        if feed_name not in self.FEED_STUBS:
            raise ValueError(f"Unknown feed: {feed_name}")
        return self.FEED_STUBS[feed_name].get_failure_mode()

    def get_all_modes(self) -> dict[str, ObservationStatus]:
        """Get all feed failure modes for UI visibility."""
        return {
            feed_name: stub.get_failure_mode()
            for feed_name, stub in self.FEED_STUBS.items()
        }

    def get_status_report(self) -> dict:
        """
        Generate status report for UI visibility.
        Shows active modes and any failure conditions.
        """
        return {
            "controller": "hostility_simulation",
            "phase": 3,
            "modes": self.get_all_modes(),
            "constraints": {
                "no_randomness": True,
                "no_retries": True,
                "no_auto_recovery": True,
            },
        }


# Module-level singleton
_controller = None


def get_controller() -> HostilityController:
    """Get or create the singleton controller instance."""
    global _controller
    if _controller is None:
        _controller = HostilityController()
    return _controller


def set_failure_mode(feed_name: FeedName, mode: ObservationStatus) -> None:
    """Set failure mode for a specific feed."""
    get_controller().set_failure_mode(feed_name, mode)


def get_failure_mode(feed_name: FeedName) -> ObservationStatus:
    """Get current failure mode for a specific feed."""
    return get_controller().get_failure_mode(feed_name)


def get_all_modes() -> dict[str, ObservationStatus]:
    """Get all feed failure modes."""
    return get_controller().get_all_modes()


def get_status_report() -> dict:
    """Get status report for UI visibility."""
    return get_controller().get_status_report()
