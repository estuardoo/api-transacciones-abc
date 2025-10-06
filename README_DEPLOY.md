# api-transacciones-abc

## Despliegue rápido (sin crear recursos IAM/DynamoDB desde CloudFormation)
Requisitos:
- Rol IAM **existente** con trust policy para Lambda y permisos a DynamoDB.
- Tabla DynamoDB `TablaTransaccion` ya creada con PK `IDTransaccion (S)` e índices (`GSI_IDCliente_Fecha`, `GSI_IDComercio_Fecha`, `GSI_IDTarjeta_Fecha`) o sus equivalentes antiguos.

```bash
export LAMBDA_IAM_ROLE_ARN=arn:aws:iam::<ACCOUNT_ID>:role/lambda-exec-transacciones
export AWS_REGION=us-east-1
export STAGE=dev
sls deploy --region $AWS_REGION --stage $STAGE
```

## Endpoints
- POST `/import/comercios`
- POST `/import/transacciones`
- GET `/transacciones/buscar-por-id?IDTransaccion=...`
- GET `/transacciones/buscar-cliente?IDCliente=...&fecha=YYYY-MM-DD` o `&desde=YYYY-MM-DD&hasta=YYYY-MM-DD`
- GET `/transacciones/buscar-tarjeta?IDTarjeta=...&...`
- GET `/transacciones/buscar-comercio?IDComercio=...&...`

## Notas clave
- IDs (`IDCliente`, `IDComercio`, `IDTarjeta`, `IDMoneda`, `IDCanal`) como enteros; `IDTransaccion` es PK string.
- Fechas separadas: `Fecha` (YYYY-MM-DD) y `Hora` (HH:MM:SS). Se genera `FechaHoraOrden` = `YYYY-MM-DD#HH:MM:SS`.
- Búsqueda sin fechas: devuelve **todo el mes del último registro**, orden `Fecha desc, Hora desc`.
- Los handlers intentan primero los **índices nuevos** y hacen **fallback** a los antiguos si no existen.
