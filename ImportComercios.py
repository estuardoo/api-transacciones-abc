import os, json, boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLA_COMERCIO", "TablaComercio")
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
        "body": json.dumps(data, ensure_ascii=False)
    }

def _to_int_smart(v, name="IDComercio"):
    s = str(v).strip().replace(" ", "")
    if s == "":
        raise ValueError(f"{name} requerido")
    try:
        return int(s)
    except Exception:
        try:
            return int(float(s))
        except Exception:
            raise ValueError(f"{name} debe ser entero. Valor: {v!r}")

def _clean_str(v):
    if v is None:
        return ""
    return str(v).strip()

def lambda_handler(event, context):
    try:
        body = event.get("body")
        if not body:
            return _resp(400, {"ok": False, "msg": "Body vacío"})
        try:
            data = json.loads(body)
        except Exception:
            return _resp(400, {"ok": False, "msg": "JSON inválido"})

        # Acepta item único o array
        items = data if isinstance(data, list) else data.get("data") if isinstance(data, dict) else None
        if items is None:
            # si enviaron un solo objeto
            if isinstance(data, dict):
                items = [data]
            else:
                return _resp(400, {"ok": False, "msg": "Estructura inválida. Esperado array o {'data': [...]}."})

        count = 0
        with table.batch_writer(overwrite_by_pkeys=["IDComercio"]) as bw:
            for it in items:
                if not isinstance(it, dict):
                    continue
                clean = {}

                # IDComercio (requerido)
                if "IDComercio" in it and str(it["IDComercio"]).strip() != "":
                    clean["IDComercio"] = _to_int_smart(it["IDComercio"], "IDComercio")
                elif "ComercioID" in it and str(it["ComercioID"]).strip() != "":
                    clean["IDComercio"] = _to_int_smart(it["ComercioID"], "ComercioID")
                else:
                    raise ValueError("IDComercio requerido")

                # Espejo para compatibilidad
                clean["ComercioID"] = clean["IDComercio"]

                # Campos opcionales (string)
                for k in ["Nombre","RUC","ActividadEconomica","Sector","Direccion","Telefono","Email","Estado"]:
                    if k in it:
                        clean[k] = _clean_str(it[k])

                # IDEstado (opcional → int)
                if "IDEstado" in it and str(it["IDEstado"]).strip() != "":
                    clean["IDEstado"] = _to_int_smart(it["IDEstado"], "IDEstado")
                else:
                    # Si no viene, intentar inferir desde Estado
                    estado = str(it.get("Estado","")).strip().lower()
                    if estado in ("activo","active","1","true","sí","si"):
                        clean["IDEstado"] = 1
                    elif estado in ("inactivo","inactive","0","false","no"):
                        clean["IDEstado"] = 0

                bw.put_item(Item=clean)
                count += 1

        return _resp(200, {"ok": True, "insertados": count})
    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response["Error"]["Message"]})
    except Exception as ex:
        return _resp(500, {"ok": False, "msg": str(ex)})
