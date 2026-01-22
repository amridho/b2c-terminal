FRAME_ALLOWED = {
    "market_aggressiveness": {"price_observed"},
    "visibility_dominance": {"visibility_observed"},
    "efficiency_stress": {"input_proxy_observed"},
}

def validate(frame_id: str, signal_types: list[str]):
    if frame_id not in FRAME_ALLOWED:
        return False, f"Unknown frame_id: {frame_id}"
    allowed = FRAME_ALLOWED[frame_id]
    for st in signal_types:
        if st not in allowed:
            return False, f"Signal {st} not allowed in frame {frame_id}"
    return True, ""

def main(frame_id: str, signal_types: list[str]):
    ok, msg = validate(frame_id, signal_types)
    if ok:
        return "ADMISSIBLE"
    return "NOT_ADMISSIBLE", msg
