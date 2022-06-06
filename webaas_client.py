import asyncio
import requests
import websockets
import json
import dto_pb2 as dto
import wegroupon_pb2 as wg


http_endpoint = "http://tea2:8000"
ws_endpoint = "ws://tea2:8000"
app_id = None
app_name = None

def bug_on(cond):
    if cond:
        raise RuntimeError()


def register_app(app_name_, app_id_=None):
    global app_id
    global app_name
    if app_id_ is None:
        r = requests.post(f"{http_endpoint}/app",
                          params={"appName": app_name_})
        bug_on(r.status_code != 200)
        app_id_ = r.json()["appID"]
    app_id = app_id_
    app_name = app_name_
    print(f"App ID: {app_id}")


def create_schema(schema_file):
    with open(schema_file, "rb") as f:
        r = requests.put(f"{http_endpoint}/schema", data=f.read(),
                         params={"appID": app_id, "fileName": schema_file, "version": "1.0.0"})
        bug_on(r.status_code != 200)
    r = requests.post(http_endpoint+"/schema",
                      params={"appID": app_id, "version": "1.0.0"})
    bug_on(r.status_code != 200)


def tx_begin():
    r = requests.post(f"{http_endpoint}/transaction",
                      params={"action": "begin"})
    bug_on(r.status_code != 200)
    return r.json()["transactionID"]


def tx_abort(tx_id):
    r = requests.post(f"{http_endpoint}/transaction",
                      params={"action": "abort", "transactionID": tx_id})
    bug_on(r.status_code != 200)


def tx_commit(tx_id):
    r = requests.post(f"{http_endpoint}/transaction",
                      params={"action": "commit", "transactionID": tx_id})
    bug_on(r.status_code != 200)


def tx_get(tx_id, schema, key):
    r = requests.get(f"{http_endpoint}/query/transactional",
                     params={"appID": app_id, "schemaName": f"{app_name}.{schema.__name__}", "transactionID": tx_id, "recordKey": key})
    if r.status_code == 200:
        record = schema()
        record.ParseFromString(r.content)
        return record
    else:
        bug_on(r.json()["code"] != 1002)
        return None


def tx_put(tx_id, record):
    r = requests.post(f"{http_endpoint}/record/transactional", data=record.SerializeToString(),
                      params={"appID": app_id, "schemaName": f"{app_name}.{type(record).__name__}", "transactionID": tx_id})
    bug_on(r.status_code != 200)


def get(schema, key):
    r = requests.get(f"{http_endpoint}/query",
                     params={"appID": app_id, "schemaName": f"{app_name}.{schema.__name__}", "recordKey": key})
    if r.status_code == 200:
        record = schema()
        record.ParseFromString(r.content)
        return record
    else:
        bug_on(r.json()["code"] != 1002)
        return None


def parse_range_query_result(schema, buf):
    more = bool(buf[0])
    buf = buf[1:]

    records = []
    while len(buf) > 0:
        size = buf[0] * 256 + buf[1]
        record = schema()
        record.ParseFromString(buf[2:2 + size])
        buf = buf[2 + size:]
        records.append(record)

    return records, more


def get_range(schema, begin_key, end_key, itr):
    r = requests.get(http_endpoint+"/query",
                     params={"appID": app_id, "schemaName": f"{app_name}.{schema.__name__}", "range": True, "beginKey": begin_key, "endKey": end_key, "iteration": itr})
    bug_on(r.status_code != 200)
    return parse_range_query_result(schema, r.content)


def put(record):
    r = requests.post(f"{http_endpoint}/record", data=record.SerializeToString(),
                      params={"appID": app_id, "schemaName": f"{app_name}.{type(record).__name__}"})
    bug_on(r.status_code != 200)


def create_notifc(schema, keys):
    r = requests.post(f"{http_endpoint}/notification",
                      data=json.dumps({"appID": app_id, "schemaName": f"{app_name}.{schema.__name__}", "recordKeys": keys}))
    bug_on(r.status_code != 200)
    return r.json()["notificationID"]


def delete_notifc(notifc_id):
    r = requests.delete(f"{http_endpoint}/notification",
                        params={"appID": app_id, "notificationID": notifc_id})
    bug_on(r.status_code != 200)


async def subscribe(notifc_id, callback):
    async with websockets.connect(f"{ws_endpoint}/notification?appID={app_id}&notificationID={notifc_id}") as websocket:
        async for msg in websocket:
            await asyncio.sleep(1) # Wait for the transactions to be committed
            notifc_msg = dto.NotificationMessage()
            notifc_msg.ParseFromString(bytes(msg, 'utf-8'))
            for key in notifc_msg.record_keys:
                await callback(key)
