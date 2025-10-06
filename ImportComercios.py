import os, json, boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLA_COMERCIO", "TablaComercio")
ddb = boto3.resource("dynamodb")
table = ddb.Table(TABLE_NAME)

def _resp(code, data):
    return {"statusCode": code, "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"}, "body": json.dumps(data)}

def _to_int(v, name="IDComercio"):
    try:
        return int(v)
    except Exception:
        raise ValueError(f"{name} debe ser entero. Valor: {v!r}")

def lambda_handler(event, context):
    try:
        body = event.get("body")
        if not body:
            return _resp(400, {"ok": False, "msg": "Body vacío"})
        items = json.loads(body)
        if not isinstance(items, list):
            return _resp(400, {"ok": False, "msg": "El body debe ser un JSON array de objetos"})

        count = 0
        with table.batch_writer(overwrite_by_pkeys=["IDComercio"]) as bw:
            for it in items:
                if it is None: continue
                clean = {k: v for k, v in it.items() if v is not None and v != ""}

                if "IDComercio" in clean:
                    clean["IDComercio"] = _to_int(clean["IDComercio"], "IDComercio")
                elif "ComercioID" in clean:
                    clean["IDComercio"] = _to_int(clean["ComercioID"], "ComercioID")
                else:
                    continue

                bw.put_item(Item=clean); count += 1

        return _resp(200, {"ok": True, "insertados": count})
    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response["Error"]["Message"]})
    except Exception as ex:
        return _resp(500, {"ok": False, "msg": str(ex)})
