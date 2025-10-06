# Infraestructura DynamoDB (CloudFormation)

- `serverless.infra.final.yml` → crea TablaComercio/TablaTransaccion con GSIs **nuevos** (ID* + FechaHoraOrden).
- `infra/serverless.stepN.yml` → migra en 5 pasos si ya tienes índices legacy:
  - `GSI_Cliente_Fecha (ClienteID + FechaHoraISO)`
  - `GSI_Comercio_Fecha (ComercioID + FechaHoraISO)`

**Pasos sugeridos** (uno por despliegue):
```bash
cp infra/serverless.step1.yml serverless.yml && sls deploy --region $AWS_REGION --stage $STAGE
cp infra/serverless.step2.yml serverless.yml && sls deploy --region $AWS_REGION --stage $STAGE
cp infra/serverless.step3.yml serverless.yml && sls deploy --region $AWS_REGION --stage $STAGE
cp infra/serverless.step4.yml serverless.yml && sls deploy --region $AWS_REGION --stage $STAGE
cp infra/serverless.step5.yml serverless.yml && sls deploy --region $AWS_REGION --stage $STAGE
```
