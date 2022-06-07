

import asyncio
from threading import Thread
import utils
import webaas_client as wc
import wegroupon_pb2 as wg

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
    #TODO: 改成gui版本的通知
    g_id = int(g_id)

    group = wc.get(wg.Group, g_id)

    if g_id in current_customer.c_owned_groups and \
            group.g_status == wg.G_STATUS_OPEN:
        print(f"\n[Notification] Group #{g_id} has new participants")

    if g_id in current_customer.c_participated_groups and \
            group.g_status == wg.G_STATUS_FINISH:
        print(f"\n[Notification] Group #{g_id} has been finished")


def subscribe_thread(notifc_id):
    asyncio.run(wc.subscribe(notifc_id, on_group_update))


async def update_current_customer(customer):
    global current_customer
    global current_notifc_id
    global current_subscribing_task

    current_customer = customer

    if current_notifc_id is not None:
        # await cancel_task(current_subscribing_task)
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
        current_subscribing_task = Thread(
            target=subscribe_thread, args=(current_notifc_id,)).start()


async def get_customer(c_phone):
    return wc.get(wg.Customer, c_phone)


async def register_with_param(c_phone, c_name, c_password):

    customer = wg.Customer()
    customer.c_phone = c_phone
    customer.c_name = c_name
    customer.c_password = c_password

    tx_id = wc.tx_begin()
    wc.tx_put(tx_id, customer)
    wc.tx_commit(tx_id)

    utils.print_customer(customer)
    await update_current_customer(customer)
    return customer


async def login_with_param(c_phone, c_password):
    customer = wc.get(wg.Customer, c_phone)
    if customer is None:
        print(f"Customer with #{c_phone} not found")
    elif customer.c_password != c_password:
        print("Wrong password")
    else:
        await update_current_customer(customer)
        utils.print_customer(customer)
    return customer


async def get_user_info():
    return wc.get(wg.Customer, current_customer.c_phone)


async def create_group_with_param(g_name, g_description, c_phone, g_item_list):

    tx_id = wc.tx_begin()

    meta = wc.tx_get(tx_id, wg.Meta, utils.meta_id)

    g_id = meta.m_group_id

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


async def join_group_with_param(c_phone, g_id, g_p_item_list):

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
            group.g_items[items.g_p_id].g_i_count = group.g_items[items.g_p_id].g_i_count - items.g_p_count

    customer = wc.tx_get(tx_id, wg.Customer, c_phone)

    customer.c_participated_groups.append(g_id)

    g_participator = group.g_participators.add()
    g_participator.g_p_id = customer.c_phone
    g_participator.g_p_items.extend(g_p_item_list)

    wc.tx_put(tx_id, group)
    wc.tx_put(tx_id, customer)

    wc.tx_commit(tx_id)

    await update_current_customer(customer)

    utils.print_group(group)

    return group


async def get_all_groups():
    more = True
    itr = 1
    all_groups = []
    while more:
        groups, more = wc.get_range(wg.Group, "0", "999", itr)
        for group in groups:
            utils.print_group(group)
            all_groups.append(group)
        itr += 1
    return all_groups

# TODO: bug: finish 后查看还是open


async def finish_group_with_param(g_id):
    if current_customer is None:
        print("Please login first")
        return

    c_phone = current_customer.c_phone

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
