
# Infra as code (DynamoDB con CloudFormation via Serverless)

Incluye:
- `serverless.yml` (estado **final**: TablaComercio + TablaTransaccion con GSIs nuevos)
- `infra.step1.yml`..`infra.step5.yml` para migración por fases de **GSIs** si la tabla ya existe con índices viejos.
  - **Regla DynamoDB/CloudFormation:** solo 1 creación/eliminación de GSI por actualización.

## Migración sugerida (si ya existe la tabla):
```bash
cp infra.step1.yml serverless.yml && sls deploy --region $AWS_REGION --stage $STAGE
cp infra.step2.yml serverless.yml && sls deploy --region $AWS_REGION --stage $STAGE
cp infra.step3.yml serverless.yml && sls deploy --region $AWS_REGION --stage $STAGE
cp infra.step4.yml serverless.yml && sls deploy --region $AWS_REGION --stage $STAGE
cp infra.step5.yml serverless.yml && sls deploy --region $AWS_REGION --stage $STAGE
```
Al final, deja `serverless.yml` como el **final** (o vuelve a copiarlo).

> Si estás instalando desde cero (la tabla no existe), puedes usar directamente `serverless.yml` final.
