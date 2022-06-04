#!/usr/bin/env python3


import asyncio
import sys
import group_purchase_pb2 as gp
import webaas_client as wc
from aioconsole import ainput


cur_c_id = None


async def register():
    c_id = int(await ainput("Enter customer ID: "))
    
    tx_id = wc.tx_begin()
    
    if wc.tx_get(tx_id, gp.Customer, c_id) is not None:
        print(f"Customer {c_id} already exists")
        wc.tx_abort()
        return
    
    customer = gp.Customer()
    customer.c_id = c_id
    customer.c_name = await ainput("Enter customer name: ")
    customer.c_phone = await ainput("Enter customer phone: ")
    wc.tx_put(tx_id, customer)
    
    wc.tx_commit(tx_id)


async def login():
    global cur_c_id
    c_id = int(await ainput("Enter customer ID: "))
    customer = wc.get(gp.Customer, c_id)
    if customer is None:
        print(f"Customer {c_id} not found")
    else:
        cur_c_id = c_id


ops = [
    (register, "Register"),
    (login, "Login"),
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
        await ops[op_idx][0]()


if __name__ == "__main__":
    asyncio.run(main())
