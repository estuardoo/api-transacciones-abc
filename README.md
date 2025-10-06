# api-transacciones (actualizado)

API Serverless (AWS Lambda + API Gateway + DynamoDB) para gestionar y consultar transacciones y comercios.

## Cambios clave
- Renombrados campos en **TablaTransaccion**:
  - `TransaccionID` → **`IDTransaccion`** (PK)
  - `ClienteID` → **`IDCliente`**
  - `ComercioID` → **`IDComercio`**
  - `CodigoMoneda` → **`IDMoneda`**
  - `IDTransaccionOrigen` → **`IDTarjeta`**
- Fechas separadas: **`Fecha`** (YYYY-MM-DD) y **`Hora`** (HH:MM:SS).
- Campo auxiliar interno: **`FechaHoraOrden`** = `YYYY-MM-DD#HH:MM:SS` (UTC) para ordenar/filtrar.
- Todas las columnas **ID** se manejan como **enteros** (excepto `IDTransaccion` que se guarda como string PK).
- Eliminado **BusquedaClienteRango** y unificadas búsquedas con parámetros opcionales de fecha.

## Endpoints

### GET
- **Por ID de Transacción**  
  `GET /transacciones/buscar-por-id?IDTransaccion=...`

- **Por ID de Cliente**  
  `GET /transacciones/buscar-cliente?IDCliente=...&fecha=YYYY-MM-DD`  
  o `&desde=YYYY-MM-DD&hasta=YYYY-MM-DD`

- **Por ID de Tarjeta**  
  `GET /transacciones/buscar-tarjeta?IDTarjeta=...&fecha=YYYY-MM-DD`  
  o `&desde=YYYY-MM-DD&hasta=YYYY-MM-DD`

- **Por ID de Comercio**  
  `GET /transacciones/buscar-comercio?IDComercio=...&fecha=YYYY-MM-DD`  
  o `&desde=YYYY-MM-DD&hasta=YYYY-MM-DD`

### Reglas de fechas
- Si envías **solo `fecha`** ⇒ devuelve solo ese día.
- Si envías **`desde` y `hasta`** ⇒ rango completo [desde, hasta].
- Si **no** envías fechas ⇒ devuelve **todo el mes** del **último registro** existente para ese ID (ordenado **Fecha desc, Hora desc**).

## Importación

### `POST /import/transacciones`
Cuerpo: **lista** de objetos JSON con la siguiente **matriz**:

| Campo | Obligatorio | Tipo | Notas |
|---|---|---|---|
| IDTransaccion | Sí | string (PK) | Identificador único de transacción |
| IDCliente | Sí | int | |
| IDComercio | Sí | int | |
| Fecha | Sí | YYYY-MM-DD | |
| Hora | Sí | HH:MM:SS | |
| IDTarjeta | No | int | |
| IDMoneda | No | int | Si falta y llega `CodigoMoneda`, se intenta derivar |
| CodigoMoneda | No | string/int | Opcional |
| IDCanal | No | int | Si llega no numérico, se guarda literal |
| Canal | No | string | Opcional |
| Monto | No | number | Opcional |
| Estado | No | string | Opcional |
| Descripcion | No | string | Opcional |

**Notas:**
- El sistema genera **`FechaHoraOrden`** automáticamente a partir de `Fecha` y `Hora` (UTC).
- Validaciones: todos los **ID** (excepto `IDTransaccion`) se intentan castear a **int**.

### `POST /import/comercios`
Sin cambios respecto a versión anterior.

## Índices DynamoDB recomendados
- **PK TablaTransaccion**: `IDTransaccion` (S)
- **GSI_Cliente_Fecha**: HASH=`IDCliente` (N), RANGE=`FechaHoraOrden` (S)
- **GSI_IDTarjeta_Fecha**: HASH=`IDTarjeta` (N), RANGE=`FechaHoraOrden` (S)
- **GSI_Comercio_Fecha**: HASH=`IDComercio` (N), RANGE=`FechaHoraOrden` (S)
