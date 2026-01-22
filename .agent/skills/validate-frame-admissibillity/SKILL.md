---
name: validate_frame_admissibility
description: |
  Validate that a given signal set is admissible for a specific frame,
  based on the canonical frame enforcement contract. This does not compute
  views or render; it only checks whether the combination of signals is allowed
  for the specified frame.
---

# Validate Frame Admissibility

## Input
- `frame_id`: one of:
  - `market_aggressiveness`
  - `visibility_dominance`
  - `efficiency_stress`
- `signal_types`: list of signal_type values

## Rules
Refer to the canonical enforcement contract:
- `market_aggressiveness`: only `price_observed`
- `visibility_dominance`: only `visibility_observed`
- `efficiency_stress`: only `input_proxy_observed`

## Failure Handling
- If frame_id is unknown → reject
- If signal_types contain disallowed entries → reject

## Output
- `"ADMISSIBLE"` or `"NOT_ADMISSIBLE"` with violation details

## Scripts
The following script assists the agent:
