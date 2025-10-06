
import os, json, boto3
from datetime import datetime, timezone, timedelta
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from utils_index import _query_with_index_fallback

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
dynamodb = boto3.resource("dynamodb")

def _resp(code, data):
    return {"statusCode": code, "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"}, "body": json.dumps(data)}

def _day_bounds(fecha_yyyy_mm_dd:str):
    return f"{fecha_yyyy_mm_dd}#00:00:00", f"{fecha_yyyy_mm_dd}#23:59:59"

PREFERRED_INDEX = "GSI_IDCliente_Fecha"
FALLBACK_INDEXES = ["GSI_Cliente_Fecha"]

def _parse_params(params):
    idv = params.get("IDCliente")
    if not idv: raise ValueError("Falta IDCliente")
    fecha = params.get("fecha"); desde = params.get("desde"); hasta = params.get("hasta")
    return int(idv), fecha, desde, hasta

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    table = dynamodb.Table(TABLE_NAME)
    try:
        idv, fecha, desde, hasta = _parse_params(params)

        if fecha and not (desde or hasta):
            ini, fin = _day_bounds(fecha)
            q = _query_with_index_fallback(table, "IDCliente", idv, ini, fin, PREFERRED_INDEX, FALLBACK_INDEXES)
            return _resp(200, {"ok": True, "data": q.get("Items", [])})

        if desde and hasta:
            ini, _ = _day_bounds(desde); _, fin = _day_bounds(hasta)
            q = _query_with_index_fallback(table, "IDCliente", idv, ini, fin, PREFERRED_INDEX, FALLBACK_INDEXES)
            return _resp(200, {"ok": True, "data": q.get("Items", [])})

        # sin fechas -> mes del último registro
        latest = None
        for idx in [PREFERRED_INDEX] + FALLBACK_INDEXES:
            try:
                latest = table.query(IndexName=idx, KeyConditionExpression=Key("IDCliente").eq(idv), ScanIndexForward=False, Limit=1)
                break
            except ClientError:
                continue
        items = (latest or {}).get("Items", [])
        if not items:
            return _resp(200, {"ok": True, "data": []})

        ult = items[0]
        fecha_str = ult.get("Fecha") or (str(ult.get("FechaHoraOrden","")).split("#")[0] if ult.get("FechaHoraOrden") else None)
        if not fecha_str: return _resp(200, {"ok": True, "data": items})

        dt = datetime.strptime(fecha_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        start = dt.replace(day=1)
        nextm = (start.replace(year=start.year+1, month=1, day=1) if start.month==12 else start.replace(month=start.month+1, day=1))
        end = nextm - timedelta(seconds=1)
        ini = start.strftime("%Y-%m-%d#00:00:00"); fin = end.strftime("%Y-%m-%d#%H:%M:%S")

        q = _query_with_index_fallback(table, "IDCliente", idv, ini, fin, PREFERRED_INDEX, FALLBACK_INDEXES)
        return _resp(200, {"ok": True, "data": q.get("Items", [])})
    except ValueError as ve:
        return _resp(400, {"ok": False, "msg": str(ve)})
    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response["Error"]["Message"]})
