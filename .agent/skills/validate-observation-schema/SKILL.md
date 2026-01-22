
---
name: validate_observation_schema
description: |

Validate that a given artifact (file, JSON object, or database export) conforms to the canonical observation schema defined in the governance skill. 

This validator checks required fields, signal types, provenance structure, and observation status, rejecting anything that violates the policy.

---


# Validate Observation Schema

This skill verifies a candidate observation structure for strict compliance.

## Input
Expect one of:
- A JSON file path with observations array (`*.json`)
- A directory containing observation files
- A Python object representing one or more observations

## Rules
1. Each observation must have:
   - `observation_time` (ISO 8601)
   - `market_object` (string, abstract identifier)
   - `actor_id` (string, opaque identifier)
   - `signal_type` (one of the closed enum)
   - `signal_value` (raw numeric or categorical)
   - `provenance` object with:
     - `source`
     - `collection_method`
     - `freshness_class`
     - `reliability_class`
     - `failure_notes` (if applicable)
   - `observation_status` in:
     - observed, missing, blocked, inferred, stale

2. `signal_type` must be exactly one of:
   - `price_observed`
   - `visibility_observed`
   - `inventory_proxy_observed`
   - `input_proxy_observed`

3. No extra top-level fields are permitted.

## Failure Handling
- If any record violates the schema, reject with:
  - field name
  - expected type/enum
  - actual value
  - location in artifact

## Output
- Pass: `"VALID"`
- Fail: `"INVALID"` + detailed report

## Scripts
The following script will be available to the agent for execution:

