#!/usr/bin/env bash
# Request deletion of the deployed CloudFormation stack.
set -euo pipefail
STACK_NAME="${1:-careeragent-ai}"
aws cloudformation delete-stack --stack-name "$STACK_NAME"
echo "Delete requested for $STACK_NAME. Empty the generated S3 bucket first if CloudFormation reports a bucket-not-empty error."
