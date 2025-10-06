# api-transacciones-abc

API Serverless (Lambda + API Gateway) con DynamoDB.

## Rutas
- POST `/import/comercios`
- POST `/import/transacciones`
- GET `/transacciones/buscar-por-id?IDTransaccion=...`
- GET `/transacciones/buscar-cliente?IDCliente=...&fecha=YYYY-MM-DD` o `&desde=YYYY-MM-DD&hasta=YYYY-MM-DD`
- GET `/transacciones/buscar-tarjeta?IDTarjeta=...`
- GET `/transacciones/buscar-comercio?IDComercio=...`

## Reglas de búsqueda
- Orden: `Fecha desc, Hora desc` usando `FechaHoraOrden = "YYYY-MM-DD#HH:MM:SS"`.
- Solo `fecha`: devuelve ese día.
- Sin fechas: devuelve **todo el mes** del último registro de ese ID.

## Despliegue (por defecto con rol LabRole)
```bash
export AWS_REGION=us-east-1
export STAGE=dev
# si quieres otro rol, sobreescribe:
# export LAMBDA_IAM_ROLE_ARN=arn:aws:iam::<ACCOUNT_ID>:role/tu-rol

sls deploy --region $AWS_REGION --stage $STAGE
```
