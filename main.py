#!/usr/bin/env python3

import sys
import asyncio
import services
import utils
from aioconsole import ainput
import webaas_client as wc


ops = [
    (services.register, "Register"),
    (services.login, "Login"),
    (services.get_user_info, "Get your info"),
    (services.create_group, "Create a group"),
    (services.join_group, "Join a group"),
    (services.get_all_groups, "Print all groups"),
    (services.finish_group, "Finish a group"),

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
