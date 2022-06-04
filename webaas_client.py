import requests


endpoint = "http://tea2:8000"
app_id = None
app_name = None


def bug_on(cond):
    if cond:
        raise RuntimeError()


def register_app(app_name_):
    global app_id
    global app_name
    r = requests.post(f"{endpoint}/app", params={"appName": app_name_})
    bug_on(r.status_code != 200)
    app_id = r.json()["appID"]
    app_name = app_name_


def create_schema(schema_file):
    with open(schema_file, "rb") as f:
        r = requests.put(f"{endpoint}/schema", data=f.read(),
                         params={"appID": app_id, "fileName": schema_file, "version": "1.0.0"})
        bug_on(r.status_code != 200)
    r = requests.post(endpoint+"/schema",
                      params={"appID": app_id, "version": "1.0.0"})
    bug_on(r.status_code != 200)


def tx_begin():
    r = requests.post(f"{endpoint}/transaction", params={"action": "begin"})
    bug_on(r.status_code != 200)
    return r.json()["transactionID"]


def tx_abort(txid):
    r = requests.post(f"{endpoint}/transaction", params={"action": "abort", "transactionID": txid})
    bug_on(r.status_code != 200)


def tx_commit(txid):
    r = requests.post(f"{endpoint}/transaction", params={"action": "commit", "transactionID": txid})
    bug_on(r.status_code != 200)


def tx_get(txid, schema, key):
    r = requests.get(f"{endpoint}/query/transactional",
                     params={"appID": app_id, "schemaName": f"{app_name}.{schema.__name__}", "transactionID": txid, "recordKey": key})
    if r.status_code == 200:
        record = schema()
        record.ParseFromString(r.content)
        return record
    else:
        bug_on(r.json()["code"] != 1002)
        return None
    

def tx_put(txid, record):
    r = requests.post(f"{endpoint}/record/transactional", data=record.SerializeToString(),
                      params={"appID": app_id, "schemaName": f"{app_name}.{type(record).__name__}", "transactionID": txid})
    bug_on(r.status_code != 200)


def get(schema, key):
    r = requests.get(f"{endpoint}/query",
                     params={"appID": app_id, "schemaName": f"{app_name}.{schema.__name__}", "recordKey": key})
    if r.status_code == 200:
        record = schema()
        record.ParseFromString(r.content)
        return record
    else:
        bug_on(r.json()["code"] != 1002)
        return None


def put(record):
    r = requests.post(f"{endpoint}/record", data=record.SerializeToString(),
                      params={"appID": app_id, "schemaName": f"{app_name}.{type(record).__name__}"})
    bug_on(r.status_code != 200)
