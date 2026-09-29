#!/usr/bin/env bash
# Minimal API smoke test for health and CV/job analysis endpoints.
set -euo pipefail
API="${1:-http://localhost:8000}"
curl -fsS "$API/health"
printf '\n'
curl -fsS -X POST "$API/analyze" -H 'content-type: application/json' \
  -d '{"cv":"Python Vue Firebase Google Cloud Gemini","job":"Nexora Labs AI Native Software Engineer - Python AWS SQL LLM"}'
printf '\n'
