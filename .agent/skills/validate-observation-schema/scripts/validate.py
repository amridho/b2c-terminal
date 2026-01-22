import json
from typing import Any, Dict

ALLOWED_SIGNAL_TYPES = {
    "price_observed",
    "visibility_observed",
    "inventory_proxy_observed",
    "input_proxy_observed",
}
REQUIRED_FIELDS = {
    "observation_time",
    "market_object",
    "actor_id",
    "signal_type",
    "signal_value",
    "provenance",
    "observation_status",
}
REQUIRED_PROVENANCE = {
    "source",
    "collection_method",
    "freshness_class",
    "reliability_class",
}

def load_json(path: str):
    with open(path, "r") as f:
        return json.load(f)

def validate_observation(obs: Dict[str, Any]):
    missing = REQUIRED_FIELDS - obs.keys()
    if missing:
        return False, f"Missing fields: {missing}"
    stype = obs["signal_type"]
    if stype not in ALLOWED_SIGNAL_TYPES:
        return False, f"Invalid signal_type: {stype}"
    prov = obs["provenance"]
    if not all(k in prov for k in REQUIRED_PROVENANCE):
        return False, "Provenance missing required fields"
    return True, ""

def main(file_path: str):
    data = load_json(file_path)
    if not isinstance(data, list):
        return "INVALID: Root is not a list of observations"
    errors = []
    for idx, obs in enumerate(data):
        ok, msg = validate_observation(obs)
        if not ok:
            errors.append(f"Record {idx}: {msg}")
    if errors:
        return "INVALID", errors
    return "VALID"
