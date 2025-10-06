from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

def _query_with_index_fallback(table, hash_key_name, hash_key_value, ini=None, fin=None, preferred_index=None, fallback_indexes=None):
    kwargs = {}
    if ini and fin:
        kwargs['KeyConditionExpression'] = Key(hash_key_name).eq(hash_key_value) & Key('FechaHoraOrden').between(ini, fin)
    else:
        kwargs['KeyConditionExpression'] = Key(hash_key_name).eq(hash_key_value)

    indexes = [i for i in [preferred_index] + (fallback_indexes or []) if i]
    last_err = None
    for idx in indexes:
        try:
            return table.query(IndexName=idx, ScanIndexForward=False, **kwargs)
        except ClientError as e:
            code = e.response.get('Error', {}).get('Code', '')
            msg = e.response.get('Error', {}).get('Message', '')
            if code in ('ValidationException','ResourceNotFoundException') or 'index' in msg.lower():
                last_err = e
                continue
            raise
    if last_err:
        raise last_err
    # fallback final (poco eficiente)
    return table.query(ScanIndexForward=False, **kwargs)
