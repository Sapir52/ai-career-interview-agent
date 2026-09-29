#!/usr/bin/env bash
# Build the SAM application and start an interactive AWS deployment.
set -euo pipefail
cd "$(dirname "$0")/../infra"
sam build
sam deploy --guided
