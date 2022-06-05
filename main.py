#!/usr/bin/env python3


import asyncio
import sys
import group_purchase_pb2 as gp
import webaas_client as wc
from aioconsole import ainput


current_customer = None
current_notifc_id = None
current_subscribing_task = None


async def cancel_task(task):
    task.cancel()
    try:
        await task
    except asyncio.exceptions.CancelledError:
        return


g_status_str = {
    gp.G_STATUS_OPEN: "Open",
    gp.G_STATUS_FINISH: "Finished"
}


def print_group(group):
    print(f"------- Group #{group.g_id} -------")
    print(f"Name: {group.g_name}")
    print(f"Description: {group.g_description}")
    print(f"Total participants: {len(group.g_participators)}")
    print(f"status: {g_status_str[group.g_status]}")
    print("-" * (23 + len(str(group.g_id))))


def print_customer(customer):
    print(f"------- Customer #{customer.c_id} -------")
    print(f"Name: {customer.c_name}")
    print(f"Phone: {customer.c_phone}")
    print("-" * (26 + len(str(customer.c_id))))


def on_group_update(g_id):
    g_id = int(g_id)
    
    group = wc.get(gp.Group, g_id)

    if g_id in current_customer.c_owned_groups and \
        group.g_status == gp.G_STATUS_OPEN:
        print(f"\n[Notification] Group #{g_id} has new participants")
    
    if g_id in current_customer.c_participated_groups and \
        group.g_status == gp.G_STATUS_FINISH:
        print(f"\n[Notification] Group #{g_id} has been finished")


async def update_current_customter(customer):
    global current_customer
    global current_notifc_id
    global current_subscribing_task
    
    current_customer = customer
    
    if current_notifc_id is not None:
        await cancel_task(current_subscribing_task)
        wc.delete_notifc(current_notifc_id)

    c_owned_groups = list(customer.c_owned_groups)
    c_participated_groups = list(customer.c_participated_groups)
    subscribed_groups = c_owned_groups + c_participated_groups
    subscribed_groups = [str(g_id) for g_id in subscribed_groups]
    
    if len(subscribed_groups) == 0:
        current_notifc_id = None
        current_subscribing_task = None
    else:
        current_notifc_id = wc.create_notifc(gp.Group, subscribed_groups)
        current_subscribing_task = asyncio.create_task(
            wc.subscribe(current_notifc_id, on_group_update))


async def register():
    c_id = int(await ainput("Enter customer ID: "))
    
    tx_id = wc.tx_begin()
    
    if wc.tx_get(tx_id, gp.Customer, c_id) is not None:
        print(f"Customer #{c_id} already exists")
        wc.tx_abort(tx_id)
        return
    
    customer = gp.Customer()
    customer.c_id = c_id
    customer.c_name = await ainput("Enter customer name: ")
    customer.c_phone = await ainput("Enter customer phone: ")
    wc.tx_put(tx_id, customer)
    
    wc.tx_commit(tx_id)

    print_customer(customer)


async def login():
    c_id = int(await ainput("Enter customer ID: "))
    customer = wc.get(gp.Customer, c_id)
    if customer is None:
        print(f"Customer #{c_id} not found")
    else:
        await update_current_customter(customer)
        print_customer(customer)


async def create_group():
    if current_customer is None:
        print("Please login first")
        return

    c_id = current_customer.c_id
    g_id = int(await ainput("Enter group ID: "))

    tx_id = wc.tx_begin()
    
    group = wc.tx_get(tx_id, gp.Group, g_id)
    if group is not None:
        print(f"Group #{g_id} already exists")
        wc.tx_abort(tx_id)
        return

    group = gp.Group()
    group.g_id = g_id
    group.g_name = await ainput("Enter group name: ")
    group.g_description = await ainput("Enter group description: ")
    group.g_status = gp.G_STATUS_OPEN

    customer = wc.tx_get(tx_id, gp.Customer, c_id)
    customer.c_owned_groups.append(g_id)

    g_participator = group.g_participators.add()
    g_participator.g_p_id = c_id

    wc.tx_put(tx_id, group)
    wc.tx_put(tx_id, customer)
    
    wc.tx_commit(tx_id)

    await update_current_customter(customer)

    print_group(group)


async def join_group():
    if current_customer is None:
        print("Please login first")
        return
    
    c_id = current_customer.c_id
    g_id = int(await ainput("Enter group ID: "))

    tx_id = wc.tx_begin()

    group = wc.tx_get(tx_id, gp.Group, g_id)
    if group is None:
        print(f"Group #{g_id} not found")
        wc.tx_abort(tx_id)
        return

    if group.g_status == gp.G_STATUS_FINISH:
        print(f"Group #{g_id} has been finished")
        wc.tx_abort(tx_id)
        return

    customer = wc.tx_get(tx_id, gp.Customer, c_id)
    
    if g_id in customer.c_participated_groups or \
       g_id in customer.c_owned_groups:
       print(f"Already in group #{g_id}")
       wc.tx_abort(tx_id)
       return

    customer.c_participated_groups.append(g_id)

    g_participator = group.g_participators.add()
    g_participator.g_p_id = customer.c_id

    wc.tx_put(tx_id, group)
    wc.tx_put(tx_id, customer)

    wc.tx_commit(tx_id)

    await update_current_customter(customer)

    print_group(group)


async def print_all_groups():
    more = True
    itr = 1
    while more:
        groups, more = wc.get_range(gp.Group, "0", "999", itr)
        for group in groups:
            print_group(group)
        itr += 1


async def finish_group():
    if current_customer is None:
        print("Please login first")
        return

    c_id = current_customer.c_id
    g_id = int(await ainput("Enter group ID: "))

    tx_id = wc.tx_begin()

    customer = wc.tx_get(tx_id, gp.Customer, c_id)
    if g_id not in customer.c_owned_groups:
        print(f"Not the owner of group #{g_id}")
        wc.tx_abort(tx_id)
        return

    group = wc.tx_get(tx_id, gp.Group, g_id)
    if group.g_status == gp.G_STATUS_FINISH:
        print(f"Group #{g_id} has already been finished")
        wc.tx_abort(tx_id)
        return

    group.g_status = gp.G_STATUS_FINISH
    
    wc.tx_put(tx_id, group)
    
    wc.tx_commit(tx_id)

    print_group(group)


ops = [
    (register, "Register"),
    (login, "Login"),
    (create_group, "Create a group"),
    (join_group, "Join a group"),
    (print_all_groups, "Print all groups"),
    (finish_group, "Finish a group"),
    (exit, "Exit")
]


async def main():
    if len(sys.argv) == 1:
        wc.register_app("group_purchase")
        wc.create_schema("proto/group_purchase.proto")
    else:
        wc.register_app("group_purchase", sys.argv[1])
    
    print("\nWelcome to the group buy application")
    while True:
        print("\nPlease tell me what you want to do")
        for (op_idx, (_, op_desc)) in enumerate(ops):
            print(f"{op_idx}. {op_desc}")
        op_idx = int(await ainput("Enter choice: "))
        if op_idx < len(ops):
            await ops[op_idx][0]()


if __name__ == "__main__":
    asyncio.run(main())
