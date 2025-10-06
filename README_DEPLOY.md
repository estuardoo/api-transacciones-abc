
# api-transacciones-abc

Implementación Serverless (AWS Lambda + API Gateway HTTP API) para:
- Importar Comercios y Transacciones a DynamoDB
- Consultar Transacciones por ID, Cliente, Tarjeta y Comercio

## Requisitos
- **NO** se crean recursos IAM ni DynamoDB desde CloudFormation (evita errores de permisos/GSIs).
- Debes contar con:
  - Un **rol IAM existente** (para Lambda) con:
    - Trust policy para `lambda.amazonaws.com`
    - `AWSLambdaBasicExecutionRole`
    - Permisos mínimos a DynamoDB sobre tus tablas/GSIs: `dynamodb:GetItem`, `PutItem`, `BatchWriteItem`, `Query`, `DescribeTable`
  - Tablas DynamoDB **preexistentes**:
    - `TablaTransaccion` (PK: `IDTransaccion` [S])
      - GSIs recomendados (**no obligatorios para desplegar**, pero necesarios para buen performance):
        - `GSI_IDCliente_Fecha (HASH=IDCliente [N], RANGE=FechaHoraOrden [S])`
        - `GSI_IDComercio_Fecha (HASH=IDComercio [N], RANGE=FechaHoraOrden [S])`
        - `GSI_IDTarjeta_Fecha (HASH=IDTarjeta [N], RANGE=FechaHoraOrden [S])`
      - Si aún tienes GSIs viejos (`GSI_Cliente_Fecha`, `GSI_Comercio_Fecha`): los handlers harán **fallback** automático.
    - `TablaComercio` (PK: `IDComercio` [N])

## Variables de entorno
Configúralas en tu shell o en tu CI/CD (`.env` de ejemplo incluido):
```bash
export LAMBDA_IAM_ROLE_ARN=arn:aws:iam::<ACCOUNT_ID>:role/lambda-exec-transacciones
export AWS_REGION=us-east-1
export STAGE=dev
export TABLA_TRANSACCION=TablaTransaccion
export TABLA_COMERCIO=TablaComercio
```

## Despliegue
```bash
sls deploy --region $AWS_REGION --stage $STAGE
```

## Rutas
- `POST /import/comercios`
- `POST /import/transacciones`
- `GET  /transacciones/buscar-por-id?IDTransaccion=...`
- `GET  /transacciones/buscar-cliente?IDCliente=...&fecha=YYYY-MM-DD` **o** `&desde=YYYY-MM-DD&hasta=YYYY-MM-DD`
- `GET  /transacciones/buscar-tarjeta?IDTarjeta=...&fecha=YYYY-MM-DD` **o** `&desde=YYYY-MM-DD&hasta=YYYY-MM-DD`
- `GET  /transacciones/buscar-comercio?IDComercio=...&fecha=YYYY-MM-DD` **o** `&desde=YYYY-MM-DD&hasta=YYYY-MM-DD`

### Reglas de búsqueda
- **Orden**: `Fecha` desc, y a igualdad, `Hora` desc (internamente usando `FechaHoraOrden = "YYYY-MM-DD#HH:MM:SS"`).
- Si llega **solo `fecha`** → devuelve **ese día** completo.
- Si llegan **`desde` y `hasta`** → devuelve el rango **[desde, hasta]** (inclusive por día).
- Si **no** llegan fechas → devuelve **todo el mes** correspondiente a la **última fecha** registrada para ese ID.

## Matriz de importación

### ImportTransacciones (JSON array)
Campos **obligatorios**: `IDTransaccion (string)`, `IDCliente (int)`, `IDComercio (int)`, `Fecha (YYYY-MM-DD)`, `Hora (HH:MM:SS)`

Campos **opcionales**: `IDTarjeta (int)`, `IDMoneda (int)`, `CodigoMoneda (string/int)`, `IDCanal (int)`, `Canal (string)`, `Monto (number)`, `Estado (string)`, `Descripcion (string)`

> Regla: si llega `CodigoMoneda` pero **no** `IDMoneda`, se deriva `IDMoneda` intentando convertir `CodigoMoneda` a entero.

### ImportComercios (JSON array)
- `IDComercio (int)` **o** `ComercioID (int)` (legacy, mapeado a `IDComercio`)
- Los demás campos se almacenan tal cual si vienen.

## Notas
- **IDs enteros**: `IDCliente`, `IDComercio`, `IDTarjeta`, `IDMoneda`, `IDCanal` se castea a int si vienen.
- `IDTransaccion` se almacena como **string** (PK).
- Esta versión **no** crea/actualiza GSIs. Si necesitas crear GSIs vía CloudFormation, usa un stack de infraestructura separado o migración por fases (1 GSI por update).
