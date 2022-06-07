#!/usr/bin/env python3

import sys
import asyncio
import services
import utils
from aioconsole import ainput
import webaas_client as wc
import services
import wegroupon_pb2 as wg


async def register():
    c_phone = await ainput("Enter your phone: ")
    c_name = await ainput("Enter your name: ")
    c_password = await ainput("Enter your password: ")
    while wc.get(wg.Customer, c_phone) is not None:
        print(
            f"Customer with #{c_phone} already exists, please try another one")
        c_phone = await ainput("Enter your phone: ")
    await services.register_with_param(c_phone, c_name, c_password)


async def login():
    c_phone = int(await ainput("Enter your phone: "))
    c_password = await ainput("Enter your password: ")
    await services.login_with_param(c_phone, c_password)


async def join_group():
    if services.current_customer is None:
        print("Please login first")
        return

    c_phone = services.current_customer.c_phone
    g_id = int(await ainput("Enter group ID: "))

    if g_id in services.customer.c_participated_groups or \
       g_id in services.customer.c_owned_groups:
        print(f"Already in group #{g_id}")
        return

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
    while(True):
        g_p_id = int(await ainput("Enter item id (enter -1 for finish):"))
        if(g_p_id == -1):
            break
        elif(g_p_id >= len(group.g_items)):
            print("Invalid item id")
            continue
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

    await services.join_group_with_param(c_phone, g_id, g_p_item_list)


async def create_group():
    if services.current_customer is None:
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
    c_phone = services.current_customer.c_phone
    await services.create_group_with_param(
        g_name, g_description, c_phone, g_item_list)


async def finish_group():
    if services.current_customer is None:
        print("Please login first")
        return

    g_id = int(await ainput("Enter group ID: "))

    await services.finish_group_with_param(g_id)


async def get_user_info():
    customer = await services.get_user_info()
    utils.print_customer(customer)


async def get_all_groups():
    await services.get_all_groups()

ops = [
    (register, "Register"),
    (login, "Login"),
    (get_user_info, "Get your info"),
    (create_group, "Create a group"),
    (join_group, "Join a group"),
    (get_all_groups, "Print all groups"),
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
