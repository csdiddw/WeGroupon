import wegroupon_pb2 as wg
import webaas_client as wc

meta_id = 1

g_status_str = {
    wg.G_STATUS_OPEN: "Open",
    wg.G_STATUS_FINISH: "Finished"
}


def print_group_item(item):
    print(f"------- Group Item #{item.g_i_id} -------")
    print(f"Name of the item: {item.g_i_name}")
    print(f"Description: {item.g_i_description}")
    print(f"Number: {item.g_i_count}")
    print(f"Price: {item.g_i_price}")


def print_group_participator_item(item):
    print(f"------- Group Participator Item #{item.g_p_id} -------")
    print(f"Phone: {item.g_p_id}")
    print(f"Count: {item.g_p_count}")
    print(f"Price: {item.g_p_price}")


def print_group_participator(participator):
    print(f"------- Group Participator #{participator.g_p_id} -------")
    print(f"Phone: {participator.g_p_id}")
    for item in participator.g_p_items:
        print_group_participator_item(item)


def print_group(group):
    print(f"------- Group #{group.g_id} -------")
    print(f"Name: {group.g_name}")
    print(f"Description: {group.g_description}")
    for participant in group.g_participators:
        print_group_participator(participant)
    print("-" * 27)
    print(f"Total items: {len(group.g_items)}")
    for item in group.g_items:
        print_group_item(item)
    print("-" * 27)
    print(f"owner: {group.g_owner_id}")
    print(f"status: {g_status_str[group.g_status]}")
    print("-" * (23 + len(str(group.g_id))))


def print_customer(customer):
    print(f"------- Customer #{customer.c_phone} -------")
    print(f"Phone: {customer.c_phone}")
    print(f"Name: {customer.c_name}")
    print(f"Password: {customer.c_password}")
    print(f"Your Groups: {list(customer.c_owned_groups)}")
    print(f"Your Participated Groups: {list(customer.c_participated_groups)}")
    print("-" * (26 + len(str(customer.c_phone))))


def initialize_meta():
    meta = wg.Meta()
    meta.m_id = meta_id
    meta.m_group_id = 0
    meta.m_history_item_id = 0
    meta.m_audit_id = 0
    wc.put(meta)
