import os, json, boto3
from decimal import Decimal
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
dynamodb = boto3.resource("dynamodb")

def _to_jsonable(obj):
    if isinstance(obj, Decimal):
        # Convert Decimal to int when whole-number, else float
        return int(obj) if obj % 1 == 0 else float(obj)
    if isinstance(obj, list):
        return [ _to_jsonable(x) for x in obj ]
    if isinstance(obj, dict):
        return { k: _to_jsonable(v) for k,v in obj.items() }
    return obj

def _resp(code, data):
    return {
        "statusCode": code,
        "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
        "body": json.dumps(_to_jsonable(data), ensure_ascii=False)
    }
, "body": json.dumps(data)}

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    tid = params.get("IDTransaccion")
    if not tid:
        return _resp(400, {"ok": False, "msg": "Falta IDTransaccion"})
    table = dynamodb.Table(TABLE_NAME)
    try:
        r = table.get_item(Key={"IDTransaccion": str(tid)})
        if "Item" not in r:
            return _resp(404, {"ok": False, "msg": "Transacción no encontrada"})
        return _resp(200, {"ok": True, "data": r["Item"]})
    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response["Error"]["Message"]})
