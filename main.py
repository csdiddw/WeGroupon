#!/usr/bin/env python3
import requests
import uuid
import sys
import group_buy_pb2
import websockets
import json
from google.protobuf.json_format import Parse

endpoint = "http://localhost:8000"
appName = "python-crud"+str(uuid.uuid4())  # unique app name
appID = None
personId = -1

def register():
    global appID
    print("Registering app...")
    r = requests.post(endpoint+"/app", params={"appName": appName})
    if r.status_code == 200:
        appID = r.json()["appID"]
        print("App registered with ID: "+appID)
    else:
        print("Error registering app: "+r.text)
        sys.exit(1)


def create_schema():
    print("Creating schema...")
    # upload schema file
    with open("proto/group_buy.proto", "rb") as f:
        r = requests.put(endpoint+"/schema", data=f.read(), params={
                         "appID": appID, "fileName": "group_buy.proto", "version": "1.0.0"})
        if r.status_code != 200:
            print("Error creating schema: "+r.text)
            sys.exit(1)
    print("Schema file uploaded.")
    # update schema version
    r = requests.post(endpoint+"/schema",
                      params={"appID": appID, "version": "1.0.0"})
    if r.status_code != 200:
        print("Error updating schema version: "+r.text)
        sys.exit(1)
    print("Schema version updated.")


def create_group(group: group_buy_pb2.Group):
    print("Creating group...")
    r = requests.post(endpoint+"/record", params={
                      "appID": appID, "schemaName": "example.Group"}, data=group.SerializeToString())
    if r.status_code != 200:
        print("Error creating group: "+r.text)
        sys.exit(1)
    print("Group created.")

def create_person(person: group_buy_pb2.Person):
    global personId
    print("Creating person...")
    print(person.SerializeToString())
    print(person)
    r = requests.post(endpoint+"/record", params={
        "appID": appID, "schemaName": "example.Person"}, data=person.SerializeToString())
    if r.status_code != 200:
        print("Error creating person: "+r.text)
        sys.exit(1)
    personId = r.json()["record_key"]
    get_person(personId)


def user_register(person: group_buy_pb2.Person):
    person.id = int(input("Enter person ID: "))
    person.name = input("Enter person name: ")
    email = input("Enter person email (blank for none): ")
    if email != "":
        person.email = email
    while True:
        number = input("Enter person phone number (blank for none): ")
        if number == "":
            break
        phone_number = person.phones.add()
        phone_number.number = number
        phone_type = input("Is this a mobile, home, or work phone? ")
        if phone_type == "mobile":
            phone_number.type = group_buy_pb2.Person.MOBILE
        elif phone_type == "home":
            phone_number.type = group_buy_pb2.Person.HOME
        elif phone_type == "work":
            phone_number.type = group_buy_pb2.Person.WORK
        else:
            print("Invalid phone type; leaving as default.")


def user_update(person: group_buy_pb2.Person):
    person.name = input("Enter person name: ")
    email = input("Enter person email (blank for none): ")
    if email != "":
        person.email = email
    while True:
        number = input("Enter person phone number (blank for none): ")
        if number == "":
            break
        phone_number = person.phones.add()
        phone_number.number = number
        phone_type = input("Is this a mobile, home, or work phone? ")
        if phone_type == "mobile":
            phone_number.type = group_buy_pb2.Person.MOBILE
        elif phone_type == "home":
            phone_number.type = group_buy_pb2.Person.HOME
        elif phone_type == "work":
            phone_number.type = group_buy_pb2.Person.WORK
        else:
            print("Invalid phone type; leaving as default.")

def group_update(group: group_buy_pb2.Group):
    group.name = input("Enter group name: ")
    group.description = input("Enter group description: ")
    while True:
        person_id = input("Enter person ID to add to group (blank to finish): ")
        if person_id == "":
            break
        add_person_to_group(group.id, person_id)

def get_person(person_id):
    r = requests.get(endpoint+"/query",
                     params={"appID": appID, "recordKey": person_id, "schemaName": "example.Person"})
    if r.status_code != 200:
        print("Error getting person: "+r.text)
        return None
    person = Parse(r.json()['record_value'],group_buy_pb2.Person())
    return person


def get_group(group_id):
    r = requests.get(endpoint+"/query",
                     params={"appID": appID, "schemaName": "example.Group", "recordKey": group_id})
    if r.status_code != 200:
        print("Error getting group: "+r.text)
        sys.exit(1)
    group = Parse(r.json()['record_value'],group_buy_pb2.Group())
    return group

def get_groups():
    print("Getting groups...")
    print("not implemented yet")
    return

def get_noficationId(groupId):
    data = {
        "appID": appID, "schemaName": "example.Group", "recordKeys":[str(groupId)]
    }
    print(json.dumps(data))
    r = requests.post(endpoint+"/notification", data=json.dumps(data))

    if r.status_code != 200:
        print("Error getting notification ID: "+r.text)
        sys.exit(1)
    return int(r.json()["notificationID"])

def add_person_to_group(group_id, person_id):
    group = get_group(group_id)
    new_person = group.people.add()
    person = get_person(person_id)
    new_person.CopyFrom(person)
    new_person.notificationIds.append(get_noficationId(group_id))
    create_person(new_person)
    create_group(group)

async def listen(person_id):
    print("Listening for updates...")
    person = get_person(person_id)
    for notificationId in person.notificationIds:
        async with websockets.connect(
            endpoint + 'notication',params={
                      "appID": appID, "notificationID": notificationId}) as websocket:
            msg = await websocket.recv()
            print(msg)
            print("{}".format(person))

def notificate(group_id):
    group = get_group(group_id)
    group.description = "Group buy has been completed!"
    create_group(group)

def main():
    global personId
    register()
    create_schema()
    # group = group_buy_pb2.Group()
    # group.id = input("Enter group ID: ")
    # group.name = input("Enter group name: ")
    # group.description = input("Enter group description: ")
    # create_group(group)
    print("\nWelcome to the group buy application")
    while True:
        print("\nPlease tell me what you want to do")
        print("1. Register")
        print("2. Login")
        print("3. Check personal information")
        print("4. Update personal information")
        print("5. Join a group")
        print("6. Create a group")
        print("7. Check group information")
        print("8. Update group information")
        print("9. Notification person in group")
        print("10. Get all group")
        print("11. Exit")
        choice = int(input("Enter choice: "))
        if choice == 1:
            person = group_buy_pb2.Person()
            user_register(person)
            create_person(person)
        elif choice == 2:
            id = int(input("Enter person ID: "))
            person = get_person(id)
            if person != None:
                print("{}".format(person))
                personId = id
            else:
                print("Person not found")
        elif choice == 3:
            if personId != -1:
                person = get_person(personId)
                if person != None:
                    print("{}".format(person))
                else:
                    print("Person not found")
            else:
                print("Please login first")
        elif choice == 4:
            if personId != -1:
                person = get_person(personId)
                if person != None:
                    print("{}".format(person))
                    user_update(person)
                    create_person(person)
                else:
                    print("Person not found")
            else:
                print("Please login first")
        elif choice == 5:
            if personId != -1:
                group_id = int(input("Enter group ID: "))
                add_person_to_group(group_id, personId)
            else:
                print("Please login first")
        elif choice == 6:
            group = group_buy_pb2.Group()
            group.id = int(input("Enter group ID: "))
            group.name = input("Enter group name: ")
            group.description = input("Enter group description: ")
            create_group(group)
            add_person_to_group(group.id, personId)
        elif choice == 7:
            group_id = int(input("Enter group ID: "))
            group = get_group(group_id)
            if group != None:
                print("{}".format(group))
            else:
                print("Group not found")
        elif choice == 8:
            group_id = int(input("Enter group ID: "))
            group = get_group(group_id)
            if group != None:
                print("{}".format(group))
                group_update(group)
                create_group(group)
            else:
                print("Group not found")
        elif choice == 9:
            group_id = int(input("Enter group ID: "))
            notificate(group_id)
        elif choice == 10:
            group = get_group(group.id)
            print("{}".format(group))
        elif choice ==11:
            break


if __name__ == "__main__":
    main()
