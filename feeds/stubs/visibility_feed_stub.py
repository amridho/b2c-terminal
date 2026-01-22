"""
Visibility Feed Stub Adapter
Phase 3 — Hostility Simulation

Governance constraints:
- No real data ingestion
- No auto-recovery
- No inference
- Manual failure mode selection only
"""

import json
from datetime import datetime
from typing import Literal

ObservationStatus = Literal["observed", "missing", "blocked", "stale"]


class VisibilityFeedStub:
    """
    Stub adapter for visibility_feed interface.
    Returns exactly one observation status per invocation.
    Failure mode must be manually selected — no randomness, no retries.
    """

    SIGNAL_TYPE = "visibility_observed"
    STUB_MARKER = "[STUB_VALUE]"

    def __init__(self):
        self._failure_mode: ObservationStatus = "observed"

    def set_failure_mode(self, mode: ObservationStatus) -> None:
        """
        Manually select the failure mode.
        No validation bypass. No auto-recovery.
        """
        if mode not in ("observed", "missing", "blocked", "stale"):
            raise ValueError(f"Invalid failure mode: {mode}")
        self._failure_mode = mode

    def get_failure_mode(self) -> ObservationStatus:
        """Return current failure mode for UI visibility."""
        return self._failure_mode

    def fetch(
        self,
        market_object: str,
        actor_id: str,
        observation_time: str | None = None
    ) -> dict:
        """
        Fetch observation according to current failure mode.
        Returns canonical schema-compliant observation.
        """
        if observation_time is None:
            observation_time = datetime.utcnow().isoformat() + "Z"

        base_observation = {
            "observation_time": observation_time,
            "market_object": market_object,
            "actor_id": actor_id,
            "signal_type": self.SIGNAL_TYPE,
            "observation_status": self._failure_mode,
        }

        if self._failure_mode == "observed":
            base_observation["signal_value"] = 0.0  # Placeholder — marked as stub
            base_observation["provenance"] = {
                "source": f"{self.STUB_MARKER}_visibility_source",
                "collection_method": f"{self.STUB_MARKER}_manual_stub",
                "freshness_class": "stub",
                "reliability_class": "stub",
            }
        elif self._failure_mode == "missing":
            base_observation["signal_value"] = None
            base_observation["provenance"] = {
                "source": f"{self.STUB_MARKER}_unavailable",
                "collection_method": "none",
                "freshness_class": "unknown",
                "reliability_class": "unknown",
                "failure_notes": "Data source did not respond. No inference attempted.",
            }
        elif self._failure_mode == "blocked":
            base_observation["signal_value"] = None
            base_observation["provenance"] = {
                "source": f"{self.STUB_MARKER}_blocked",
                "collection_method": "none",
                "freshness_class": "unknown",
                "reliability_class": "unknown",
                "failure_notes": "Access denied by data source. No bypass attempted.",
            }
        elif self._failure_mode == "stale":
            base_observation["signal_value"] = 0.0  # Old value — not refreshed
            base_observation["provenance"] = {
                "source": f"{self.STUB_MARKER}_stale_cache",
                "collection_method": f"{self.STUB_MARKER}_cached",
                "freshness_class": "stale",
                "reliability_class": "degraded",
                "failure_notes": "Data exceeds freshness threshold. No refresh attempted.",
            }

        return base_observation

    def to_json(self, observation: dict) -> str:
        """Serialize observation to JSON."""
        return json.dumps(observation, indent=2)


# Module-level singleton for simple access
_instance = VisibilityFeedStub()

def set_failure_mode(mode: ObservationStatus) -> None:
    _instance.set_failure_mode(mode)

def get_failure_mode() -> ObservationStatus:
    return _instance.get_failure_mode()

def fetch(market_object: str, actor_id: str, observation_time: str | None = None) -> dict:
    return _instance.fetch(market_object, actor_id, observation_time)
