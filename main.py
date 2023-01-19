# local imports
import os

# external imports
from telebot import types, TeleBot, custom_filters

# internal imports
from internal.database import User, Database
from internal import content, memory
from internal import keyboards as kb
from dotenv import load_dotenv

load_dotenv()

bot = TeleBot(os.getenv("BOT_TOKEN"), parse_mode=None)
db = Database(os.getenv("DATABASE"))
# osapi = api.OpenStackApi()

mem = memory.MEM()

class Access(custom_filters.SimpleCustomFilter):
    key='user_have_access'
    @staticmethod
    def check(message: types.Message):
        return mem.login_check(message.from_user.id)

bot.add_custom_filter(Access())

@bot.message_handler(commands=['start', 'help'])
def handle_message_start(message):
    bot.send_message(
        message.chat.id, 
        content.start_message
    )

@bot.message_handler(commands=['settings'])
def handle_message_start(message):
    bot.send_message(
        message.chat.id, 
        "⚙️ Настройки"
    )

@bot.message_handler(commands=['access'])
def handle_message_start(message):
    bot.send_message(message.chat.id, content.access_warn, parse_mode=content.md)
    bot.send_document(message.chat.id, content.get_default_creds_file())
    bot.register_next_step_handler(message, user_creds_update)

def user_creds_update(message):
    if not message.document:
        bot.send_message(message.chat.id, content.access_err) # TODO
        return 
    elif message.text == "/cancel":
        return
    file_id = bot.get_file(message.document.file_id)
    if file_id.file_path.split(".")[-1] != "txt":
        bot.send_message(message.chat.id, content.access_err) # TODO
        return 
    creds = bot.download_file(file_id.file_path)
    user = db.login(memory.User(message.from_user.id, message.from_user.first_name))
    user.set_creds(creds)
    db.update_creds(user)
    bot.send_message(message.chat.id, content.access_updated)

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
    bot.send_message(
        message.chat.id, content.get_last_update_format() + mem.services_info(), 
        reply_markup=kb.keyboard_services_list(), parse_mode=content.md)

@bot.message_handler(commands=['servers'], user_have_access=True)
def handle_message_servers(message):
    bot.send_message(
        message.chat.id, content.get_last_update_format(),
        reply_markup=kb.get_keyboard_servers_list(mem.servers)
    )

@bot.callback_query_handler(func=lambda c: c.data, user_have_access=True)
def servers_callback(c: types.CallbackQuery):
    data = c.data.split("_")
    match data:
        case ["servers", "refresh"]:
            keyboard = types.InlineKeyboardMarkup()
            mem.refresh_servers()
            bot.edit_message_text(
                content.get_last_update_format(),
                c.from_user.id, c.message.id,
                reply_markup=kb.get_keyboard_servers_list(mem.servers)
                )
        case ["servers", _, ">"]:
            start_id = int(data[-2])
            if start_id <= 0: start_id = 0
            elif start_id >= len(mem.servers): start_id = 0 
            bot.edit_message_text(
                content.get_last_update_format(), c.from_user.id, c.message.id, 
                reply_markup=kb.get_keyboard_servers_list(mem.servers, start_i=start_id)
                )
        case ["server", "show", "90bb6608-4ea2-4af6-b27f-bfe75247643f"]:
            server = mem.server_find(data[0])
            server_info = server.get_pretty_info()
            bot.send_message(c.from_user.id, server_info, parse_mode=content.md, 
                            reply_markup=kb.keyboard_for_server(server.base.id, vnc_url=server.vnc_url))
        case ["server", "reboot", "soft", "90bb6608-4ea2-4af6-b27f-bfe75247643f"]:
            server = mem.server_find(data[-1])
            try:
                server.base.reboot("SOFT")
            except Exception as err:
                bot.send_message(c.from_user.id, err)
                return
            server.status = "REBOOT"
            server_info = server.get_pretty_info()
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode=content.md,
                            reply_markup=kb.keyboard_for_server_refresh(server.base.id, vnc_url=server.vnc_url))
        case ["server", "reboot", "hard", "90bb6608-4ea2-4af6-b27f-bfe75247643f"]:
            server = mem.server_find(data[-1])
            try:
                server.base.reboot("HARD")
            except Exception as err:
                bot.send_message(c.from_user.id, err)
                return
            server.status = "HARD REBOOT"
            server_info = server.get_pretty_info()
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode=content.md,
                            reply_markup=kb.keyboard_for_server_refresh(server.base.id, vnc_url=server.vnc_url))
        case ["server", "start", "90bb6608-4ea2-4af6-b27f-bfe75247643f"]:
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
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode=content.md,
                            reply_markup=kb.keyboard_for_server_refresh(server.base.id, vnc_url=server.vnc_url))
        case ["server", "stop", "90bb6608-4ea2-4af6-b27f-bfe75247643f"]:
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
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode=content.md,
                            reply_markup=kb.keyboard_for_server_refresh(server.base.id, vnc_url=server.vnc_url))
        case ["server", "refresh", "90bb6608-4ea2-4af6-b27f-bfe75247643f"]:
            server = mem.server_find(data[-1])
            try:
                server.base.get()
            except Exception as err:
                bot.send_message(c.from_user.id, err)
                return
            server.refresh_info()
            server_info = server.get_pretty_info()
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode=content.md,
                            reply_markup=kb.keyboard_for_server(server.base.id, vnc_url=server.vnc_url))
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