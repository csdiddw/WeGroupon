from cgitb import handler
from cmath import log
import requests
import sys
import group_purchase_pb2
import websockets
import json
import logging
from google.protobuf.json_format import Parse

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

endpoint = "http://tea2:8000"
back_endpoint = "http://202.120.40.82:11232"
appName = "group_purchase"  # unique app name
appID = "71575aec-bfa8-45e7-b355-299a08d96f4c"
personId = -1

group_schema = appName+".Group"
customer_schema = appName+".Customer"
itemhistory_schema = appName+".ItemHistory"
audit_schema = appName+".Audit"


def register_app():
    global appID
    global endpoint
    logging.info("Registering app " + appName)
    try:
        r = requests.post(endpoint+"/app", params={"appName": appName})
        if r.status_code == 200:
            appID = r.json()["appID"]
            logging.info("App registered with ID: " + appID)
        else:
            logging.error("Error registering app: " + r.text)
            sys.exit(1)
    except Exception as e:
        logging.warning("Error registering app: " + str(e))
        if(endpoint == back_endpoint):
            logging.error("error in register_app")
            exit(1)
        else:
            logging.warning("try to register app in back_endpoint")
            endpoint = back_endpoint
            register_app()

def create_schema():
    logging.info("Creating schema...")
    # upload schema file
    with open("proto/group_purchase.proto", "rb") as f:
        r = requests.put(endpoint+"/schema", data=f.read(), params={
                         "appID": appID, "fileName": "group_purchase.proto", "version": "1.0.0"})
        if r.status_code != 200:
            logging.error("Error creating schema: "+r.text)
            sys.exit(1)
    logging.info("Schema file uploaded.")
    # update schema version
    r = requests.post(endpoint+"/schema",
                      params={"appID": appID, "version": "1.0.0"})
    if r.status_code != 200:
        logging.error("Error updating schema version: "+r.text)
        sys.exit(1)
    logging.info("Schema version updated.")

def put_group(group: group_purchase_pb2.Group):
    r = requests.post(endpoint+"/record", params={
                      "appID": appID, "schemaName": group_schema}, data=group.SerializeToString())
    if r.status_code != 200:
        handle_error_msg(r)

def get_group(g_id):
    r = requests.get(endpoint+"/query",
                     params={"appID": appID, "schemaName": group_schema, "recordKey": g_id})
    if r.status_code != 200:
        handle_error_msg(r)
        return None
    group = group_purchase_pb2.Group().ParseFromString(r.content)
    return group

def put_customer(customer: group_purchase_pb2.Customer):
    r = requests.post(endpoint+"/record", params={
                      "appID": appID, "schemaName": customer_schema}, data=customer.SerializeToString())
    if r.status_code != 200:
        handle_error_msg(r)

def get_customer(c_id):
    r = requests.get(endpoint+"/query",
                     params={"appID": appID, "recordKey": c_id, "schemaName": customer_schema})
    if r.status_code != 200:
        handle_error_msg(r)
        return None
    customer = group_purchase_pb2.Customer().ParseFromString(r.content)
    return customer

def put_itemhistory(itemhistory: group_purchase_pb2.ItemHistory):
    r = requests.post(endpoint+"/record", params={
                      "appID": appID, "schemaName": itemhistory_schema}, data=itemhistory.SerializeToString())
    if r.status_code != 200:
        handle_error_msg(r)

def get_itemhistory(i_id):
    r = requests.get(endpoint+"/query",
                        params={"appID": appID, "recordKey": i_id, "schemaName": itemhistory_schema})
    if r.status_code != 200:
        handle_error_msg(r)
        return None
    itemhistory = group_purchase_pb2.ItemHistory().ParseFromString(r.content)
    return itemhistory

def put_audit(audit: group_purchase_pb2.Audit):
    r = requests.post(endpoint+"/record", params={
                        "appID": appID, "schemaName": audit_schema}, data=audit.SerializeToString())
    if r.status_code != 200:
        handle_error_msg(r)

def get_audit(g_id):
    r = requests.get(endpoint+"/query",
                        params={"appID": appID, "recordKey": g_id, "schemaName": audit_schema})
    if r.status_code != 200:
        handle_error_msg(r)
        return None
    audit = group_purchase_pb2.Audit().ParseFromString(r.content)
    return audit

def get_notificationId(g_id):
    data = {
        "appID": appID, "schemaName": "example.Group", "recordKeys": [str(g_id)]
    }
    print(json.dumps(data))
    r = requests.post(endpoint+"/notification", data=json.dumps(data))

    if r.status_code != 200:
        handle_error_msg(r)
    return int(r.json()["notificationID"])

async def listen_msg(n_id):
    async with websockets.connect(
            endpoint + 'notification', params={
                "appID": appID, "notificationID": n_id}) as websocket:
        msg = await websocket.recv()
        print(msg)

def handle_error_msg(msg):
   logging.warning(msg.json()["message"])