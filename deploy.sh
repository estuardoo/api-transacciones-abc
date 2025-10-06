#!/usr/bin/env bash
set -euo pipefail
if [[ -f ".env" ]]; then set -a; source ./.env; set +a; fi
: "${AWS_REGION:=us-east-1}"; : "${STAGE:=dev}"
sls deploy --region "$AWS_REGION" --stage "$STAGE"
