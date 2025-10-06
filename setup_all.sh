#!/usr/bin/env bash
set -euo pipefail
if [[ -f ".env" ]]; then set -a; source ./.env; set +a; fi
: "${AWS_REGION:=us-east-1}"; : "${STAGE:=dev}"
: "${TABLA_TRANSACCION:=TablaTransaccion}"; : "${TABLA_COMERCIO:=TablaComercio}"
: "${LAMBDA_IAM_ROLE_ARN:=arn:aws:iam::102362304326:role/lambda-exec-transacciones}"
echo "AWS_REGION=$AWS_REGION STAGE=$STAGE"
aws sts get-caller-identity >/dev/null || (echo "Credenciales AWS inválidas"; exit 1)
