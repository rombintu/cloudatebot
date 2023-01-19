from telebot import types
from internal import memory

on_page = 5

def keyboard_for_server(_id, vnc_url):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(
        types.InlineKeyboardButton(text="⚙️", callback_data=f"settings_{_id}"),
        types.InlineKeyboardButton(text="🖥", url=vnc_url),
        types.InlineKeyboardButton(text="⌛️", callback_data=f"server_refresh_{_id}"),
    )
    keyboard.add(
        types.InlineKeyboardButton(text="▶️", callback_data=f"server_start_{_id}"),
        types.InlineKeyboardButton(text="⏹", callback_data=f"server_stop_{_id}"),
        types.InlineKeyboardButton(text="🔁", callback_data=f"server_reboot_soft_{_id}"),
        types.InlineKeyboardButton(text="🔂", callback_data=f"server_reboot_hard_{_id}"),
    )
    return keyboard

def keyboard_for_server_refresh(_id, vnc_url):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text="⚙️", callback_data=f"settings_{_id}"),
        types.InlineKeyboardButton(text="🖥", url=vnc_url),
        types.InlineKeyboardButton(text="⌛️", callback_data=f"server_refresh_{_id}"),
    )
    return keyboard

def get_keyboard_servers_list(servers, start_i=0):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    btn_refresh = types.InlineKeyboardButton(text="🔄", callback_data=f"servers_refresh")
    if not servers:
        keyboard.add(btn_refresh)
        return keyboard
    btn_next_r = types.InlineKeyboardButton(text="➡️", callback_data=f"servers_{start_i+on_page}_>")
    btn_next_l = types.InlineKeyboardButton(text="⬅️", callback_data=f"servers_{start_i-on_page}_>")
    for i in range(start_i, start_i + on_page):
        if i == len(servers): break
        keyboard.add(
            types.InlineKeyboardButton(text=f"{servers[i].base.name}", callback_data=f"server_show_{servers[i].base.id}")
        )

    if start_i == 0 and start_i + on_page >= len(servers):
        keyboard.add(btn_refresh)
    elif start_i + on_page >= len(servers): 
        keyboard.add(btn_next_l, btn_refresh)
    elif start_i == 0: 
        keyboard.add(btn_refresh, btn_next_r)
    else: 
        keyboard.add(btn_next_l, btn_refresh, btn_next_r,)
    return keyboard

def keyboard_services_list():
    keyboard = types.InlineKeyboardMarkup()      
    keyboard.add(types.InlineKeyboardButton(text="⌛️", callback_data="refresh_services_list"))
    return keyboard

def keyboard_user_settings(uuid):
    keyboard = types.InlineKeyboardMarkup()
    btn_update_creds = types.InlineKeyboardButton(text="В разработке", callback_data=f"user_settings")
    keyboard.add(btn_update_creds)
    return keyboard