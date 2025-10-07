# api-transacciones-full (compatible con versión que ya te funcionaba)

Se mantienen tus handlers de búsqueda y `serverless.yml` como estaban. Solo se actualizan los importadores para aceptar **más columnas** en `TablaTransacciones` y agregar soporte de agregados en `TablaComercios`.

## Endpoints (sin cambios)
- POST `/import/transacciones`
- POST `/import/comercios`
- GET `/transacciones/buscar-por-id?IDTransaccion=...`
- GET `/transacciones/buscar-cliente?IDCliente=...`
- GET `/transacciones/buscar-comercio?IDComercio=...`
- GET `/transacciones/buscar-tarjeta?IDTarjeta=...`

## TablaTransacciones (campos admitidos)
Obligatorios: `IDTransaccion (PK)`, `IDCliente`, `IDComercio`, `Fecha`, `Hora`  
Derivados: `FechaHoraOrden = "YYYY-MM-DD#HH:MM:SS"`, `FechaHoraISO = "YYYY-MM-DDTHH:MM:SS"`  
IDs opcionales: `IDTarjeta` (y espejo `TarjetaID`), `IDMoneda`, `IDCanal`, `IDEstado`  
Strings: `CodigoAutorizacion`, `Estado`, `Canal`, `CodigoMoneda`, `NombreComercio`, `Sector`, `Producto`, `NombreCompleto`, `DNI`, `telefono`, `email`, `Tarjeta`  
Números: `MontoBruto`, `TasaCambio`, `Monto` (Decimal), `IndicadorAprobada`, `LatenciaAutorizacionMs`, `Fraude` (int)  
Extras: `FechaCarga` (ISO o `YYYY-MM-DD HH:MM:SS`)

> Los handlers siguen usando tus GSIs y devuelven todos los atributos tal como se guardan.

## TablaComercios (agregados mensuales)
PK compuesta: `Tipo (N)` + `ID (N)`  
Atributos: `Agregado`, `Grupo`, `Ene..Dic`, `Promedio`, `TotalMonto`, `TotalFraude`, `Composicion`

## Variables de entorno (sin cambios)
- `TABLA_TRANSACCION` (p.ej. `TablaTransaccion`)
- `TABLA_COMERCIO` (detalle de comercios)
- `TABLA_COMERCIOS_AGREG` (agregados mensuales, default `TablaComercios`)

## Deploy (igual que antes)
```bash
export AWS_REGION=us-east-1
export STAGE=dev
export TABLA_TRANSACCION=TablaTransaccion
export TABLA_COMERCIO=TablaComercio
export TABLA_COMERCIOS_AGREG=TablaComercios

# usa tu CLI y serverless.yml de siempre
sls deploy --region $AWS_REGION --stage $STAGE
```