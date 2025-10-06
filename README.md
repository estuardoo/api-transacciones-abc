# api-transacciones-abc (completo)

Serverless (Lambda + API Gateway) + DynamoDB en **un solo `serverless.yml`** que crea tablas **y** funciones.

## Endpoints
- POST `/import/comercios`
- POST `/import/transacciones`
- GET `/transacciones/buscar-por-id?IDTransaccion=...`
- GET `/transacciones/buscar-cliente?IDCliente=...&fecha=YYYY-MM-DD` o `&desde=YYYY-MM-DD&hasta=YYYY-MM-DD`
- GET `/transacciones/buscar-tarjeta?IDTarjeta=...`
- GET `/transacciones/buscar-comercio?IDComercio=...`

## Reglas y cambios
- PK: `IDTransaccion` (string).
- IDs numéricos: `IDCliente`, `IDComercio`, `IDTarjeta`, `IDMoneda`, `IDCanal` (validados como enteros).
- Fecha/Hora separadas: `Fecha` y `Hora`; orden compuesto `FechaHoraOrden = "YYYY-MM-DD#HH:MM:SS"`.
- Import mapea legacy → nuevo (`TransaccionID→IDTransaccion`, `ClienteID→IDCliente`, `ComercioID→IDComercio`, `IDTransaccionOrigen→IDTarjeta`, `CodigoMoneda→IDMoneda`, `Canal→IDCanal` si es convertible).
- Búsquedas unificadas (Cliente/Tarjeta/Comercio): fecha única, rango, o **sin fechas** (mes del último registro). Orden **desc**.

## Despliegue
```bash
export AWS_REGION=us-east-1
export STAGE=dev
# si no tienes LabRole, usa tu rol:
# export LAMBDA_IAM_ROLE_ARN=arn:aws:iam::<ACCOUNT_ID>:role/tu-rol
# si ya existen tablas con esos nombres, usa otros:
# export TABLA_TRANSACCION=TablaTransaccionV2
# export TABLA_COMERCIO=TablaComercioV2

sls deploy --region $AWS_REGION --stage $STAGE
sls info   --region $AWS_REGION --stage $STAGE
```
