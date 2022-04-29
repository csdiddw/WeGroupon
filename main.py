#!/usr/bin/env python3

import group_purchase_pb2
import webaas_client as wc

def register_customer():
    customer = group_purchase_pb2.Customer()
    customer.c_id = int(input("Enter your customer ID: "))
    if(wc.get_customer(customer.c_id) != None):
        print("Customer already exists")
        return
    customer.c_name = input("Enter customer name: ")
    customer.c_email = input("Enter customer email: ")
    wc.put_customer(customer)


def group_update(group: group_purchase_pb2.Group):
    group.name = input("Enter group name: ")
    group.description = input("Enter group description: ")
    while True:
        person_id = input("Enter customer ID to add to group (blank to finish): ")
        if person_id == "":
            break
        add_person_to_group(group.id, person_id)
    wc.put_group(group)


def get_groups():
    print("Getting groups...")
    print("not implemented yet")
    return

def add_person_to_group(group_id, person_id):
    group = wc.get_group(group_id)
    new_person = group.people.add()
    customer = wc.get_person(person_id)
    new_person.CopyFrom(customer)
    new_person.notificationIds.append(wc.get_notificationId(group_id))
    wc.put_customer(new_person)
    wc.put_group(group)

async def listen(person_id):
    print("Listening for updates...")
    customer = wc.get_customer(person_id)
    for n_id in customer.notificationIds:
       wc.listen_msg(n_id)

def notify(g_id):
    group = wc.get_group(g_id)
    group.description = "Group buy has been completed!"
    wc.put_group(group)

def main():
    global personId
    # wc.register_app()
    # wc.create_schema()
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
        print("9. Notify customer in group")
        print("10. Get all group")
        print("11. Exit")
        choice = int(input("Enter choice: "))
        if choice == 1:
            register_customer()
        elif choice == 2:
            id = int(input("Enter customer ID: "))
            customer = wc.get_customer(id)
            if customer != None:
                print("{}".format(customer))
                personId = id
            else:
                print("Customer not found")
        elif choice == 3:
            if personId != -1:
                customer = wc.get_customer(personId)
                if customer != None:
                    print("{}".format(customer))
                else:
                    print("Customer not found")
            else:
                print("Please login first")
        elif choice == 4:
            if personId != -1:
                customer = wc.get_customer(personId)
                if customer != None:
                    print("{}".format(customer))
                    wc.put_customer(customer)
                else:
                    print("Customer not found")
            else:
                print("Please login first")
        elif choice == 5:
            if personId != -1:
                group_id = int(input("Enter group ID: "))
                add_person_to_group(group_id, personId)
            else:
                print("Please login first")
        elif choice == 6:
            group = group_purchase_pb2.Group()
            group.id = int(input("Enter group ID: "))
            group.name = input("Enter group name: ")
            group.description = input("Enter group description: ")
            wc.put_group(group)
            add_person_to_group(group.id, personId)
        elif choice == 7:
            group_id = int(input("Enter group ID: "))
            group = wc.get_group(group_id)
            if group != None:
                print("{}".format(group))
            else:
                print("Group not found")
        elif choice == 8:
            group_id = int(input("Enter group ID: "))
            group = wc.get_group(group_id)
            if group != None:
                print("{}".format(group))
                group_update(group)
            else:
                print("Group not found")
        elif choice == 9:
            group_id = int(input("Enter group ID: "))
            notify(group_id)
        elif choice == 10:
            group = wc.get_group(group.id)
            print("{}".format(group))
        elif choice ==11:
            break


if __name__ == "__main__":
    main()
