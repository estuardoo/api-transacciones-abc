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

def _parse_dt(fecha:str, hora:str):
    if not fecha or not hora:
        raise ValueError("Fecha y Hora son obligatorias")
    try:
        dt = datetime.fromisoformat(f"{fecha}T{hora}")
    except ValueError:
        try:
            dt = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M:%S")
        except Exception:
            raise ValueError(f"Fecha/Hora inválidas: {fecha} {hora}")
    return dt.replace(tzinfo=timezone.utc)

def _fmt_hash(fecha, hora): return _parse_dt(fecha, hora).strftime("%Y-%m-%d#%H:%M:%S")
def _fmt_iso (fecha, hora): return _parse_dt(fecha, hora).strftime("%Y-%m-%dT%H:%M:%S")

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

                it = dict(it)
                # Normalización nombres nuevos y legacy
                it.setdefault("IDTransaccion", it.get("TransaccionID"))
                it.setdefault("IDCliente", it.get("ClienteID"))
                it.setdefault("IDComercio", it.get("ComercioID"))
                it.setdefault("IDTarjeta", it.get("IDTransaccionOrigen"))

                # Mapeos opcionales
                if "IDMoneda" not in it and "CodigoMoneda" in it:
                    try: it["IDMoneda"] = _to_int_or_none(it["CodigoMoneda"])
                    except ValueError: pass
                if "IDCanal" not in it and "Canal" in it:
                    try: it["IDCanal"] = _to_int_or_none(it["Canal"])
                    except ValueError: pass

                required = ("IDTransaccion", "IDCliente", "IDComercio", "Fecha", "Hora")
                if not all(k in it and it[k] not in (None, "") for k in required):
                    continue

                clean = {k: v for k, v in it.items() if v is not None}
                # Tipos
                clean["IDTransaccion"] = str(clean["IDTransaccion"])
                clean["IDCliente"] = _to_int_or_none(clean["IDCliente"])
                clean["IDComercio"] = _to_int_or_none(clean["IDComercio"])
                if "IDTarjeta" in clean: clean["IDTarjeta"] = _to_int_or_none(clean["IDTarjeta"])
                if "IDMoneda" in clean: clean["IDMoneda"] = _to_int_or_none(clean["IDMoneda"])
                if "IDCanal" in clean:
                    try: clean["IDCanal"] = _to_int_or_none(clean["IDCanal"])
                    except ValueError: pass

                # Orden nuevo y legacy
                clean["FechaHoraOrden"] = _fmt_hash(clean["Fecha"], clean["Hora"])  # nuevo: YYYY-MM-DD#HH:MM:SS
                clean["FechaHoraISO"]   = _fmt_iso (clean["Fecha"], clean["Hora"])  # legacy: YYYY-MM-DDTHH:MM:SS

                # espejos legacy para GSIs viejos
                clean["ClienteID"]  = clean["IDCliente"]
                clean["ComercioID"] = clean["IDComercio"]

                bw.put_item(Item=clean); count += 1

        return _resp(200, {"ok": True, "insertados": count})
    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response["Error"]["Message"]})
    except Exception as ex:
        return _resp(500, {"ok": False, "msg": str(ex)})
