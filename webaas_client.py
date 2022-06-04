import requests


endpoint = "http://tea2:8000"
app_id = None
app_name = None


def bug_on(cond):
    if cond:
        raise RuntimeError()


def register_app(app_name_, app_id_=None):
    global app_id
    global app_name
    if app_id_ is None:
        r = requests.post(f"{endpoint}/app", params={"appName": app_name_})
        bug_on(r.status_code != 200)
        app_id_ = r.json()["appID"]
    app_id = app_id_
    app_name = app_name_
    print(f"App ID: {app_id}")


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


def tx_abort(tx_id):
    r = requests.post(f"{endpoint}/transaction", params={"action": "abort", "transactionID": tx_id})
    bug_on(r.status_code != 200)


def tx_commit(tx_id):
    r = requests.post(f"{endpoint}/transaction", params={"action": "commit", "transactionID": tx_id})
    bug_on(r.status_code != 200)


def tx_get(tx_id, schema, key):
    r = requests.get(f"{endpoint}/query/transactional",
                     params={"appID": app_id, "schemaName": f"{app_name}.{schema.__name__}", "transactionID": tx_id, "recordKey": key})
    if r.status_code == 200:
        record = schema()
        record.ParseFromString(r.content)
        return record
    else:
        bug_on(r.json()["code"] != 1002)
        return None
    

def tx_put(tx_id, record):
    r = requests.post(f"{endpoint}/record/transactional", data=record.SerializeToString(),
                      params={"appID": app_id, "schemaName": f"{app_name}.{type(record).__name__}", "transactionID": tx_id})
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
