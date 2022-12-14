# local imports
import os
from datetime import datetime as dt
# external imports
import telebot
from telebot import types

# internal imports
from internal import content, memory
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"), parse_mode=None)
# db = database.Database(envs["DATABASE"])
# osapi = api.OpenStackApi()

mem = memory.MEM()
page_size = "5"

def get_last_update_format():
    return f"Последнее обновление: \n\t{dt.now().strftime('%d %B в %H:%M')}"

def keyboard_for_server(_id, vnc_url):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(
        types.InlineKeyboardButton(text="⚙️", callback_data=f"settings_{_id}"),
        types.InlineKeyboardButton(text="🖥", url=vnc_url),
        types.InlineKeyboardButton(text="⌛️", callback_data=f"refresh_server_{_id}"),
    )
    keyboard.add(
        types.InlineKeyboardButton(text="▶️", callback_data=f"start_{_id}"),
        types.InlineKeyboardButton(text="⏹", callback_data=f"stop_{_id}"),
        types.InlineKeyboardButton(text="🔁", callback_data=f"soft_reboot_{_id}"),
        types.InlineKeyboardButton(text="🔂", callback_data=f"hard_reboot_{_id}"),
    )
    return keyboard

def keyboard_for_server_refresh(_id, vnc_url):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text="⚙️", callback_data=f"settings_{_id}"),
        types.InlineKeyboardButton(text="🖥", url=vnc_url),
        types.InlineKeyboardButton(text="⌛️", callback_data=f"refresh_server_{_id}"),
    )
    return keyboard

class Access(telebot.custom_filters.SimpleCustomFilter):
    key='user_have_access'
    @staticmethod
    def check(message: telebot.types.Message):
        return mem.login_check(message.from_user.id)

bot.add_custom_filter(Access())

@bot.message_handler(commands=['start', 'help'])
def handle_message_start(message):
    bot.send_message(
        message.chat.id, 
        content.start_message
    )

@bot.message_handler(commands=['admin'])
def handle_message_start(message):
    if message.from_user.id in mem.admins:
        bot.send_message(message.from_user.id, f'Пользователи: {[(u._id, u.username) for u in mem.users]}')
        return 
    elif mem.login_check(message.from_user.id):
        bot.send_message(message.from_user.id, "У вас уже есть доступ")
        return 
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Предоставить доступ  ✅", 
                callback_data=f"{message.from_user.id}_{message.from_user.username or 'noname'}_access_true"))
    for admin in mem.admins:
        bot.send_message(admin, 
            f"Запрашивает доступ\
                \nСсылка: @{message.from_user.username}\
                \nИмя: {message.from_user.first_name} {message.from_user.last_name or ''}\
                \nID: {message.from_user.id}",
            reply_markup=keyboard,
        )
    bot.send_message(
        message.from_user.id, 
        "Запрос отправлен ⌛️"
    )

@bot.message_handler(commands=['services'], user_have_access=True)
def handle_message_services(message):
    keyboard = types.InlineKeyboardMarkup()
    if not mem.services:
        bot.send_message(message.chat.id, "Список сервисов пуст")
        return         
    keyboard.add(types.InlineKeyboardButton(text="⌛️", callback_data="refresh_services_list"))
    bot.send_message(
        message.chat.id, get_last_update_format() + mem.services_info(), 
        reply_markup=keyboard, parse_mode="markdown")

@bot.message_handler(commands=['servers'], user_have_access=True)
def handle_message_servers(message):
    keyboard = types.InlineKeyboardMarkup()
    if not mem.servers:
        bot.send_message(message.chat.id, "Список серверов пуст")
        return         
    for i in range(0, int(page_size)):
        keyboard.add(types.InlineKeyboardButton(text=f"{mem.servers[i].name}", callback_data=f"{mem.servers[i].id}_id"))
    keyboard.add(
        types.InlineKeyboardButton(text="🔄", callback_data=f"refresh_servers_list"),
        types.InlineKeyboardButton(text="➡️", callback_data=f"{page_size}_>")
        )

    bot.send_message(message.chat.id, get_last_update_format(), reply_markup=keyboard)

@bot.callback_query_handler(func=lambda c: c.data, user_have_access=True)
def servers_callback(c: types.CallbackQuery):
    data = c.data.split("_")
    page_size = 5 # TODO
    match data:
        case ["refresh", "servers", "list"]:
            keyboard = types.InlineKeyboardMarkup()
            mem.refresh_servers()
            for i in range(0, int(page_size)):
                keyboard.add(types.InlineKeyboardButton(text=f"{mem.servers[i].name}", callback_data=f"{mem.servers[i].id}_id"))
            keyboard.add(
                types.InlineKeyboardButton(text="🔄", callback_data="refresh_servers_list"),
                types.InlineKeyboardButton(text="➡️", callback_data=f"{page_size}_>")
                )
            bot.edit_message_text(
                get_last_update_format(),
                c.from_user.id, c.message.id)
            bot.edit_message_reply_markup(c.from_user.id, c.message.id, reply_markup=keyboard)
        case [_, ">"]:
            start_id = int(data[0])
            if start_id <= 0: start_id = 0
            elif start_id >= len(mem.servers): start_id = 0 
            keyboard = types.InlineKeyboardMarkup()
            
            for i in range(start_id, start_id+page_size):
                keyboard.add(types.InlineKeyboardButton(text=f"{mem.servers[i].name}", callback_data=f"{mem.servers[i].id}_id"))
                if i == len(mem.servers)-1: 
                    break
            if start_id == 0:
                keyboard.add(
                    types.InlineKeyboardButton(text="🔄", callback_data="refresh_servers_list"),
                    types.InlineKeyboardButton(text="➡️", callback_data=f"{start_id+page_size}_>")
                )
            else: 
                keyboard.add(
                    types.InlineKeyboardButton(text="⬅️", callback_data=f"{start_id-page_size}_>"),
                    types.InlineKeyboardButton(text="🔄", callback_data="refresh_servers_list"),
                    types.InlineKeyboardButton(text="➡️", callback_data=f"{start_id+page_size}_>")
                )
            bot.edit_message_reply_markup(c.from_user.id, c.message.id, reply_markup=keyboard)
        case ["90bb6608-4ea2-4af6-b27f-bfe75247643f", "id"]:
            server = mem.server_find(data[0])
            server_info = server.get_pretty_info()
            bot.send_message(c.from_user.id, server_info, parse_mode="markdown", 
                            reply_markup=keyboard_for_server(server.base.id, vnc_url=server.vnc_url))
        case ["soft", "reboot", "90bb6608-4ea2-4af6-b27f-bfe75247643f"]:
            server = mem.server_find(data[-1])
            try:
                server.base.reboot("SOFT")
            except Exception as err:
                bot.send_message(c.from_user.id, err)
                return
            server.status = "REBOOT"
            server_info = server.get_pretty_info()
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode="markdown",
                            reply_markup=keyboard_for_server_refresh(server.base.id, vnc_url=server.vnc_url))
        case ["hard", "reboot", "90bb6608-4ea2-4af6-b27f-bfe75247643f"]:
            server = mem.server_find(data[-1])
            try:
                server.base.reboot("HARD")
            except Exception as err:
                bot.send_message(c.from_user.id, err)
                return
            server.status = "HARD REBOOT"
            server_info = server.get_pretty_info()
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode="markdown",
                            reply_markup=keyboard_for_server_refresh(server.base.id, vnc_url=server.vnc_url))
        case ["start", "90bb6608-4ea2-4af6-b27f-bfe75247643f"]:
            server = mem.server_find(data[-1])
            if server.status.lower() == "active":
                return
            try:
                server.base.start()
            except Exception as err:
                bot.send_message(c.from_user.id, err)
                return
            server.status = "LAUNCH"
            server_info = server.get_pretty_info()
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode="markdown",
                            reply_markup=keyboard_for_server_refresh(server.base.id, vnc_url=server.vnc_url))
        case ["stop", "90bb6608-4ea2-4af6-b27f-bfe75247643f"]:
            server = mem.server_find(data[-1])
            if server.status.lower() == "shutoff":
                return
            try:
                server.base.stop()
            except Exception as err:
                bot.send_message(c.from_user.id, err)
                return
            server.status = "STOPPING"
            server_info = server.get_pretty_info()
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode="markdown",
                            reply_markup=keyboard_for_server_refresh(server.base.id, vnc_url=server.vnc_url))
        case ["refresh", "server", "90bb6608-4ea2-4af6-b27f-bfe75247643f"]:
            server = mem.server_find(data[-1])
            try:
                server.base.get()
            except Exception as err:
                bot.send_message(c.from_user.id, err)
                return
            server.refresh_info()
            server_info = server.get_pretty_info()
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode="markdown",
                            reply_markup=keyboard_for_server(server.base.id, vnc_url=server.vnc_url))
        case [_, _, "access", _]:
            user_id = int(data[0])
            user_name = data[1]
            user = memory.User(user_id, user_name)
            action = data[-1]
            
            keyboard = types.InlineKeyboardMarkup()
            if action == "true":
                keyboard.add(types.InlineKeyboardButton(text="Исключить ❌", callback_data=f"{user._id}_{user.username}_access_false"))
                mem.login(user)
                bot.send_message(user._id, "Доступ разрешен ✅")
            elif action == "false":
                keyboard.add(types.InlineKeyboardButton(text="Предоставить доступ ✅", callback_data=f"{user._id}_{user.username}_access_true"))
                try: mem.logout(user)
                except: pass
                bot.send_message(user._id, "Доступ запрещен ❌")
            bot.edit_message_reply_markup(c.from_user.id, c.message.id, reply_markup=keyboard)
        case _:
            print(data)
            bot.send_message(c.from_user.id, ", ".join(data))
def main():
    print("Service status: OK")
    bot.polling(none_stop=True, timeout=60)
    
if __name__ == "__main__":
    main()