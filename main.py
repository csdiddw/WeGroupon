#!/usr/bin/env python3


import asyncio
import sys
import wegroupon_pb2 as wg
import webaas_client as wc
from aioconsole import ainput
import utils


current_customer = None
current_notifc_id = None
current_subscribing_task = None


async def cancel_task(task):
    task.cancel()
    try:
        await task
    except asyncio.exceptions.CancelledError:
        return


def on_group_update(g_id):
    g_id = int(g_id)

    group = wc.get(wg.Group, g_id)

    if g_id in current_customer.c_owned_groups and \
            group.g_status == wg.G_STATUS_OPEN:
        print(f"\n[Notification] Group #{g_id} has new participants")

    if g_id in current_customer.c_participated_groups and \
            group.g_status == wg.G_STATUS_FINISH:
        print(f"\n[Notification] Group #{g_id} has been finished")


async def update_current_customer(customer):
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
        current_notifc_id = wc.create_notifc(wg.Group, subscribed_groups)
        current_subscribing_task = asyncio.create_task(
            wc.subscribe(current_notifc_id, on_group_update))


async def register():
    c_phone = await ainput("Enter your phone: ")
    c_name = await ainput("Enter your name: ")
    c_password = await ainput("Enter your password: ")

    while wc.get(wg.Customer, c_phone) is not None:
        print(
            f"Customer with #{c_phone} already exists, please try another one")
        c_phone = await ainput("Enter your phone: ")

    customer = wg.Customer()
    customer.c_phone = c_phone
    customer.c_name = c_name
    customer.c_password = c_password

    tx_id = wc.tx_begin()
    wc.tx_put(tx_id, customer)
    wc.tx_commit(tx_id)

    utils.print_customer(customer)
    await update_current_customer(customer)


async def login():
    c_phone = int(await ainput("Enter your phone: "))
    c_password = await ainput("Enter your password: ")
    customer = wc.get(wg.Customer, c_phone)
    if customer is None:
        print(f"Customer with #{c_phone} not found")
    elif customer.c_password != c_password:
        print("Wrong password")
    else:
        await update_current_customer(customer)
        utils.print_customer(customer)


async def get_user_info():
    if current_customer is None:
        print("Please login first")
        return
    utils.print_customer(current_customer)


async def create_group():
    if current_customer is None:
        print("Please login first")
        return

    g_name = await ainput("Enter group name: ")
    g_description = await ainput("Enter group description: ")

    g_item_list = []
    g_i_id = 0

    while(True):

        g_i_name = await ainput("Enter item name (enter done for finish):")
        if(g_i_name == "done"):
            break
        item = wg.G_Item()
        item.g_i_id = g_i_id
        item.g_i_name = g_i_name
        item.g_i_description = await ainput("Enter item description: ")
        item.g_i_count = int(await ainput("Enter item count: "))
        item.g_i_price = float(await ainput("Enter item price: "))
        g_i_id = g_i_id + 1
        g_item_list.append(item)

    c_phone = current_customer.c_phone

    tx_id = wc.tx_begin()

    meta = wc.tx_get(tx_id, wg.Meta, utils.meta_id)

    g_id = meta.m_group_id

#   check the group
    group = wc.tx_get(tx_id, wg.Group, g_id)
    if group is not None:
        print(f"Group #{g_id} already exists")
        wc.tx_abort(tx_id)
        return

    group = wg.Group()
    group.g_id = g_id
    group.g_owner_id = c_phone
    group.g_name = g_name
    group.g_description = g_description
    group.g_status = wg.G_STATUS_OPEN
    group.g_items.extend(g_item_list)
    print(g_item_list)
    print(group.g_items)

    customer = wc.tx_get(tx_id, wg.Customer, c_phone)
    customer.c_owned_groups.append(g_id)

    g_participator = group.g_participators.add()
    g_participator.g_p_id = c_phone

    wc.tx_put(tx_id, group)
    wc.tx_put(tx_id, customer)

    meta.m_group_id = meta.m_group_id+1
    wc.tx_put(tx_id, meta)

    wc.tx_commit(tx_id)

    await update_current_customer(customer)

    utils.print_group(group)


async def join_group():
    if current_customer is None:
        print("Please login first")
        return

    c_phone = current_customer.c_phone
    g_id = int(await ainput("Enter group ID: "))

    group = wc.get(wg.Group, g_id)
    if group is None:
        print(f"Group #{g_id} not found")
        return
    elif group.g_status == wg.G_STATUS_FINISH:
        print(f"Group #{g_id} has been finished")
        return
    else:
        utils.print_group(group)

    g_p_item_list = []

#  TODO: check valid

    while(True):
        g_p_id = int(await ainput("Enter item id (enter -1 for finish):"))
        if(g_p_id == -1):
            break
        elif(group.g_items[g_p_id].g_i_count <= 0):
            print(f"Item #{g_p_id} is not enough")
            continue

        item = wg.G_P_Item()
        item.g_p_id = g_p_id
        g_p_count = int(await ainput("Enter item count: "))
        if(group.g_items[g_p_id].g_i_count < g_p_count):
            print(f"Item #{g_p_id} is not enough")
            continue
        item.g_p_count = g_p_count
        item.g_p_price = group.g_items[g_p_id].g_i_price
        g_p_item_list.append(item)
        group.g_items[g_p_id].g_i_count = group.g_items[g_p_id].g_i_count - g_p_count

    tx_id = wc.tx_begin()
    
    # Recheck group
    group = wc.tx_get(tx_id, wg.Group, g_id)
    if group is None:
        print(f"Group #{g_id} not found")
        wc.tx_abort(tx_id)
        return
    elif group.g_status == wg.G_STATUS_FINISH:
        print(f"Group #{g_id} has been finished")
        wc.tx_abort(tx_id)
        return
    else:
        for items in g_p_item_list:
            if(group.g_items[items.g_p_id].g_i_count < items.g_p_count):
                print(f"Item #{items.g_p_id} is not enough")
                wc.tx_abort(tx_id)
                return

    customer = wc.tx_get(tx_id, wg.Customer, c_phone)

    if g_id in customer.c_participated_groups or \
       g_id in customer.c_owned_groups:
        print(f"Already in group #{g_id}")
        wc.tx_abort(tx_id)
        return

    customer.c_participated_groups.append(g_id)

    g_participator = group.g_participators.add()
    g_participator.g_p_id = customer.c_phone
    g_participator.g_p_items.extend(g_p_item_list)

    wc.tx_put(tx_id, group)
    wc.tx_put(tx_id, customer)

    wc.tx_commit(tx_id)

    await update_current_customer(customer)

    utils.print_group(group)


async def print_all_groups():
    more = True
    itr = 1
    while more:
        groups, more = wc.get_range(wg.Group, "0", "999", itr)
        for group in groups:
            utils.print_group(group)
        itr += 1


async def finish_group():
    if current_customer is None:
        print("Please login first")
        return

    c_phone = current_customer.c_phone
    g_id = int(await ainput("Enter group ID: "))

    tx_id = wc.tx_begin()

    customer = wc.tx_get(tx_id, wg.Customer, c_phone)
    if g_id not in customer.c_owned_groups:
        print(f"Not the owner of group #{g_id}")
        wc.tx_abort(tx_id)
        return

    group = wc.tx_get(tx_id, wg.Group, g_id)
    if group.g_status == wg.G_STATUS_FINISH:
        print(f"Group #{g_id} has already been finished")
        wc.tx_abort(tx_id)
        return

    group.g_status = wg.G_STATUS_FINISH

    wc.tx_put(tx_id, group)

    wc.tx_commit(tx_id)

    utils.print_group(group)


ops = [
    (register, "Register"),
    (login, "Login"),
    (get_user_info, "Get your info"),
    (create_group, "Create a group"),
    (join_group, "Join a group"),
    (print_all_groups, "Print all groups"),
    (finish_group, "Finish a group"),

    (exit, "Exit")
]


async def main():
    if len(sys.argv) == 1:
        wc.register_app("wegroupon")
        wc.create_schema("proto/wegroupon.proto")
        utils.initialize_meta()
    else:
        wc.register_app("wegroupon", sys.argv[1])

    print("\nWelcome to WeGroupon!\n")

    while True:
        print("\nPlease tell me what you want to do")
        for (op_idx, (_, op_desc)) in enumerate(ops):
            print(f"{op_idx}. {op_desc}")
        try:
            op_idx = int(await ainput("Enter choice: "))
        except ValueError:
            print("Invalid choice")
            continue
        if op_idx < len(ops):
            await ops[op_idx][0]()


if __name__ == "__main__":
    asyncio.run(main())
