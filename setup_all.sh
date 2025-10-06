#!/usr/bin/env bash
set -euo pipefail
if [[ -f ".env" ]]; then set -a; source ./.env; set +a; fi
: "${AWS_REGION:=us-east-1}"; : "${STAGE:=dev}"
: "${TABLA_TRANSACCION:=TablaTransaccion}"; : "${TABLA_COMERCIO:=TablaComercio}"
: "${LAMBDA_IAM_ROLE_ARN:=arn:aws:iam::102362304326:role/lambda-exec-transacciones}"
echo "AWS_REGION=$AWS_REGION STAGE=$STAGE"
aws sts get-caller-identity >/dev/null || (echo "Credenciales AWS inválidas"; exit 1)
aws dynamodb describe-table --table-name "$TABLA_TRANSACCION" --region "$AWS_REGION" >/dev/null 2>&1 && echo "TablaTransaccion OK" || echo "No existe TablaTransaccion (se creará si usas serverless.yml final)"
aws dynamodb describe-table --table-name "$TABLA_COMERCIO" --region "$AWS_REGION" >/dev/null 2>&1 && echo "TablaComercio OK" || echo "No existe TablaComercio (se creará si usas serverless.yml final)"
