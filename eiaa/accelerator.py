"""
EIAA Accelerator — Phase 5
Conditional acceleration for validation and stub I/O.

Governance constraints:
- Mechanics only, no semantics
- No retries, no bypass, no inference
- Toggle ON/OFF must produce identical results
- Blocked remains blocked
"""

import json
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Literal

# Acceleration toggle
_EIAA_ENABLED = False


def set_eiaa_enabled(enabled: bool) -> None:
    """Toggle EIAA acceleration on/off."""
    global _EIAA_ENABLED
    _EIAA_ENABLED = enabled


def is_eiaa_enabled() -> bool:
    """Check if EIAA acceleration is enabled."""
    return _EIAA_ENABLED


# =============================================================================
# Schema Validation (unchanged logic, optional parallelization)
# =============================================================================

REQUIRED_FIELDS = ['observation_time', 'market_object', 'actor_id', 'signal_type', 
                   'signal_value', 'provenance', 'observation_status']
VALID_SIGNAL_TYPES = ['price_observed', 'visibility_observed', 
                      'inventory_proxy_observed', 'input_proxy_observed']
VALID_STATUSES = ['observed', 'missing', 'blocked', 'inferred', 'stale']
REQUIRED_PROVENANCE = ['source', 'collection_method', 'freshness_class', 'reliability_class']

FRAME_RULES = {
    'market_aggressiveness': ['price_observed'],
    'visibility_dominance': ['visibility_observed'],
    'efficiency_stress': ['input_proxy_observed'],
}


def _validate_schema_single(obs: dict, index: int) -> list:
    """Validate a single observation. Same logic regardless of EIAA."""
    violations = []
    for field in REQUIRED_FIELDS:
        if field not in obs:
            violations.append(f'Record {index}: missing required field "{field}"')
    if obs.get('signal_type') not in VALID_SIGNAL_TYPES:
        violations.append(f'Record {index}: invalid signal_type')
    if obs.get('observation_status') not in VALID_STATUSES:
        violations.append(f'Record {index}: invalid observation_status')
    prov = obs.get('provenance', {})
    for field in REQUIRED_PROVENANCE:
        if field not in prov:
            violations.append(f'Record {index}: missing provenance field "{field}"')
    return violations


def validate_schema(observations: list) -> tuple[str, list]:
    """
    Validate observation schema.
    EIAA: parallelizes validation when enabled.
    Result is identical regardless of toggle.
    """
    if _EIAA_ENABLED and len(observations) > 1:
        # Parallel validation (accelerated)
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(
                lambda args: _validate_schema_single(*args),
                [(obs, i) for i, obs in enumerate(observations)]
            ))
        violations = [v for sublist in results for v in sublist]
    else:
        # Sequential validation (baseline)
        violations = []
        for i, obs in enumerate(observations):
            violations.extend(_validate_schema_single(obs, i))
    
    return ("INVALID", violations) if violations else ("VALID", [])


def validate_frame(frame_id: str, signal_types: list) -> tuple[str, list]:
    """
    Validate frame admissibility.
    No acceleration needed — simple lookup.
    Result is identical regardless of toggle.
    """
    if frame_id not in FRAME_RULES:
        return ("NOT_ADMISSIBLE", [f"Unknown frame_id: {frame_id}"])
    
    allowed = FRAME_RULES[frame_id]
    disallowed = [s for s in signal_types if s not in allowed]
    
    if disallowed:
        return ("NOT_ADMISSIBLE", [f"Disallowed signals: {disallowed}"])
    return ("ADMISSIBLE", [])


def validate_ephemerality(root: str) -> tuple[str, dict]:
    """
    Validate computed view ephemerality.
    EIAA: parallelizes file scanning when enabled.
    Result is identical regardless of toggle.
    """
    import os
    import re
    
    COMPUTED_PATTERNS = [r"latency", r"volatility", r"share_of_voice", r"efficiency_"]
    
    def scan_file(path: str) -> list:
        with open(path, "r", errors="ignore") as f:
            content = f.read()
        matches = []
        for pattern in COMPUTED_PATTERNS:
            if re.search(pattern, content):
                matches.append(pattern)
        return matches
    
    files_to_scan = []
    for dirpath, _, filenames in os.walk(root):
        for file in filenames:
            files_to_scan.append(os.path.join(dirpath, file))
    
    violations = {}
    
    if _EIAA_ENABLED and len(files_to_scan) > 1:
        # Parallel scanning (accelerated)
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(
                lambda path: (path, scan_file(path)),
                files_to_scan
            ))
        for path, matches in results:
            if matches:
                violations[path] = matches
    else:
        # Sequential scanning (baseline)
        for full_path in files_to_scan:
            matches = scan_file(full_path)
            if matches:
                violations[full_path] = matches
    
    if violations:
        return ("EPHEMERAL_VIOLATION", violations)
    return ("EPHEMERAL_OK", {})


# =============================================================================
# Full Validation Run
# =============================================================================

def run_full_validation(artifact_path: str, frame_id: str) -> dict:
    """
    Run all validators on an artifact.
    Returns identical results regardless of EIAA toggle.
    """
    with open(artifact_path, 'r') as f:
        observations = json.load(f)
    
    # Schema validation
    schema_result, schema_violations = validate_schema(observations)
    
    # Frame admissibility
    signal_types = [obs.get('signal_type') for obs in observations]
    frame_result, frame_violations = validate_frame(frame_id, signal_types)
    
    # Ephemerality check
    artifacts_dir = str(Path(artifact_path).parent)
    ephemeral_result, ephemeral_violations = validate_ephemerality(artifacts_dir)
    
    return {
        "eiaa_enabled": _EIAA_ENABLED,
        "artifact": artifact_path,
        "frame": frame_id,
        "schema_validation": {
            "result": schema_result,
            "violations": schema_violations
        },
        "frame_admissibility": {
            "result": frame_result,
            "violations": frame_violations
        },
        "ephemerality_check": {
            "result": ephemeral_result,
            "violations": ephemeral_violations
        }
    }


# =============================================================================
# A/B Comparison
# =============================================================================

def run_ab_comparison(artifact_path: str, frame_id: str) -> dict:
    """
    Run validation with EIAA OFF and ON.
    Verify identical results.
    """
    # Run with EIAA OFF
    set_eiaa_enabled(False)
    result_off = run_full_validation(artifact_path, frame_id)
    
    # Run with EIAA ON
    set_eiaa_enabled(True)
    result_on = run_full_validation(artifact_path, frame_id)
    
    # Compare results (excluding eiaa_enabled flag)
    def extract_results(r):
        return {
            "schema": r["schema_validation"]["result"],
            "schema_violations": r["schema_validation"]["violations"],
            "frame": r["frame_admissibility"]["result"],
            "frame_violations": r["frame_admissibility"]["violations"],
            "ephemeral": r["ephemerality_check"]["result"],
        }
    
    off_results = extract_results(result_off)
    on_results = extract_results(result_on)
    
    identical = off_results == on_results
    
    return {
        "artifact": artifact_path,
        "frame": frame_id,
        "eiaa_off": off_results,
        "eiaa_on": on_results,
        "identical": identical,
        "diff": [] if identical else ["Results differ — EIAA violation"]
    }
