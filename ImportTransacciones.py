
import os, json, boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
ddb = boto3.resource("dynamodb")
table = ddb.Table(TABLE_NAME)

def _resp(code, data):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(data)
    }

def _to_int_or_none(v):
    if v is None or v == "":
        return None
    try:
        return int(v)
    except Exception:
        raise ValueError(f"Valor no entero para ID: {v}")

def _fmt_hash(fecha:str, hora:str) -> str:
    # NUEVO formato usado por los GSIs nuevos
    dt = _parse_dt(fecha, hora)
    return dt.strftime("%Y-%m-%d#%H:%M:%S")

def _fmt_iso(fecha:str, hora:str) -> str:
    # LEGACY formato usado por GSIs viejos (FechaHoraISO)
    dt = _parse_dt(fecha, hora)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

def _parse_dt(fecha:str, hora:str):
    if not fecha or not hora:
        raise ValueError("Fecha y Hora son obligatorias")
    try:
        dt = datetime.fromisoformat(f"{fecha}T{hora}")
    except ValueError:
        try:
            from datetime import datetime as _dt
            dt = _dt.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M:%S")
        except Exception:
            raise ValueError(f"Fecha/Hora inválidas: {fecha} {hora}")
    return dt.replace(tzinfo=timezone.utc)

def lambda_handler(event, context):
    try:
        body = event.get("body")
        if not body:
            return _resp(400, {"ok": False, "msg": "Body vacío"})
        items = json.loads(body)
        if not isinstance(items, list):
            return _resp(400, {"ok": False, "msg": "Se espera una lista de objetos"})

        count = 0
        with table.batch_writer(overwrite_by_pkeys=["IDTransaccion"]) as bw:
            for it in items:
                if not it: 
                    continue

                # Normaliza keys (acepta legacy)
                if "TransaccionID" in it and "IDTransaccion" not in it:
                    it["IDTransaccion"] = it["TransaccionID"]
                if "ClienteID" in it and "IDCliente" not in it:
                    it["IDCliente"] = it["ClienteID"]
                if "ComercioID" in it and "IDComercio" not in it:
                    it["IDComercio"] = it["ComercioID"]
                if "IDTransaccionOrigen" in it and "IDTarjeta" not in it:
                    it["IDTarjeta"] = it["IDTransaccionOrigen"]
                if "CodigoMoneda" in it and "IDMoneda" not in it:
                    try:
                        it["IDMoneda"] = _to_int_or_none(it["CodigoMoneda"])
                    except ValueError:
                        pass

                required = ("IDTransaccion", "IDCliente", "IDComercio", "Fecha", "Hora")
                if not all(k in it and it[k] not in (None, "") for k in required):
                    continue

                clean = {k: v for k, v in it.items() if v is not None}

                # Casteos
                clean["IDTransaccion"] = str(clean.get("IDTransaccion"))
                clean["IDCliente"] = _to_int_or_none(clean.get("IDCliente"))
                clean["IDComercio"] = _to_int_or_none(clean.get("IDComercio"))
                if "IDTarjeta" in clean:
                    clean["IDTarjeta"] = _to_int_or_none(clean.get("IDTarjeta"))
                if "IDMoneda" in clean:
                    clean["IDMoneda"] = _to_int_or_none(clean.get("IDMoneda"))
                if "IDCanal" in clean:
                    try:
                        clean["IDCanal"] = _to_int_or_none(clean.get("IDCanal"))
                    except ValueError:
                        pass

                # Formatos de ordenamiento NUEVO y LEGACY (para alimentar ambos GSIs)
                clean["FechaHoraOrden"] = _fmt_hash(clean.get("Fecha"), clean.get("Hora"))
                clean["FechaHoraISO"] = _fmt_iso(clean.get("Fecha"), clean.get("Hora"))  # legacy

                # ESPEJOS LEGACY para GSIs viejos
                clean["ClienteID"] = clean["IDCliente"]
                clean["ComercioID"] = clean["IDComercio"]

                bw.put_item(Item=clean); count += 1

        return _resp(200, {"ok": True, "insertados": count})
    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response["Error"]["Message"]})
    except Exception as ex:
        return _resp(500, {"ok": False, "msg": str(ex)})
