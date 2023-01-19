# local imports
import os

# external imports
from telebot import types, TeleBot, custom_filters
# internal imports
from internal.database import Database
from internal.memory import User, MEM
from internal.api import OpenStackApi
from internal import content
from internal import keyboards as kb
from dotenv import load_dotenv

load_dotenv()

bot = TeleBot(os.getenv("BOT_TOKEN"), parse_mode=None)
db = Database(os.getenv("DATABASE"))
osapi = OpenStackApi()
mem = MEM()


class Access(custom_filters.SimpleCustomFilter):
    key='user_have_access'
    @staticmethod
    def check(message: types.Message):
        user = db.login(User(message.from_user.id, message.from_user.first_name))
        if user.get_creds():
            return True
        bot.send_message(message.chat.id, "❗️ Не могу найти ваши доступы\nОбновите их /access")
        return False

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
    bot.send_message(message.chat.id, content.access_info, parse_mode=content.md)
    bot.register_next_step_handler(message, user_creds_update)

def user_creds_update(message):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, content.access_cancel, parse_mode=content.md)
        return
    user = db.login(User(message.from_user.id, message.from_user.first_name))
    user.set_creds(message.text)
    db.update_creds(user)
    _, err = user.servers_refresh()
    if err:
        bot.send_message(message.chat.id, content.ERROR.format(str(err)))
        return
    bot.send_message(message.chat.id, content.access_updated)


@bot.message_handler(commands=['services'], user_have_access=True)
def handle_message_services(message):
    bot.send_message(
        message.chat.id, content.get_last_update_format() + mem.services_info(), 
        reply_markup=kb.keyboard_services_list(), parse_mode=content.md)

@bot.message_handler(commands=['servers'], user_have_access=True)
def handle_message_servers(message):
    user = db.login(User(message.chat.id, message.from_user.username))
    servers, err = user.servers_refresh()
    if err:
        bot.send_message(message.chat.id, content.ERROR.format(str(err)))
        return
    bot.send_message(
        message.chat.id, content.get_last_update_format(),
        reply_markup=kb.get_keyboard_servers_list(servers)
    )

@bot.callback_query_handler(func=lambda c: c.data, user_have_access=True)
def servers_callback(c: types.CallbackQuery):
    data = c.data.split("_")
    match data:
        case ["servers", "refresh"]:
            user = db.login(User(c.message.chat.id, c.message.from_user.username))
            servers, err = user.servers_refresh()
            if err:
                bot.send_message(c.message.chat.id, content.ERROR.format(str(err)))
                return
            # mem.refresh_servers(user.uuid)
            bot.edit_message_text(
                content.get_last_update_format(),
                c.from_user.id, c.message.id,
                reply_markup=kb.get_keyboard_servers_list(servers)
                )
        case ["servers", _, ">"]:
            start_id = int(data[-2])
            if start_id <= 0: start_id = 0
            elif start_id >= len(mem.servers): start_id = 0
            user = db.login(User(c.message.chat.id, c.message.from_user.username))
            servers, err = user.servers_refresh()
            if err:
                bot.send_message(c.message.chat.id, content.ERROR.format(str(err)))
                return
            bot.edit_message_text(
                content.get_last_update_format(), c.from_user.id, c.message.id, 
                reply_markup=kb.get_keyboard_servers_list(servers, start_i=start_id)
                )
        case ["server", "show", "49ada3cb-5045-47ed-b325-a737b515381c"]:
            # TODO
            user = db.login(User(c.message.chat.id, c.message.from_user.username))
            servers, err = user.servers_refresh()
            if err:
                bot.send_message(c.message.chat.id, content.ERROR.format(str(err)))
                return
            server = user.get_server_by_id(data[-1])
            if not server:
                bot.send_message(c.from_user.id, "None")
                return
            server_info = server.get_pretty_info()
            bot.send_message(c.from_user.id, server_info, parse_mode=content.md, 
                            reply_markup=kb.keyboard_for_server(server.base.id, vnc_url=server.vnc_url))
        case ["server", "reboot", "soft", "49ada3cb-5045-47ed-b325-a737b515381c"]:
            user = db.login(User(c.message.chat.id, c.message.from_user.username))
            servers, err = user.servers_refresh()
            if err:
                bot.send_message(c.message.chat.id, content.ERROR.format(str(err)))
                return
            server = user.get_server_by_id(data[-1])
            if not server:
                bot.send_message(c.from_user.id, "None")
                return
            try:
                server.base.reboot("SOFT")
            except Exception as err:
                bot.send_message(c.from_user.id, err)
                return
            server.status = "REBOOT"
            server_info = server.get_pretty_info()
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode=content.md,
                            reply_markup=kb.keyboard_for_server_refresh(server.base.id, vnc_url=server.vnc_url))
        case ["server", "reboot", "hard", "49ada3cb-5045-47ed-b325-a737b515381c"]:
            user = db.login(User(c.message.chat.id, c.message.from_user.username))
            servers, err = user.servers_refresh()
            if err:
                bot.send_message(c.message.chat.id, content.ERROR.format(str(err)))
                return
            server = user.get_server_by_id(data[-1])
            if not server:
                bot.send_message(c.from_user.id, "None")
                return
            try:
                server.base.reboot("HARD")
            except Exception as err:
                bot.send_message(c.from_user.id, err)
                return
            server.status = "HARD REBOOT"
            server_info = server.get_pretty_info()
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode=content.md,
                            reply_markup=kb.keyboard_for_server_refresh(server.base.id, vnc_url=server.vnc_url))
        case ["server", "start", "49ada3cb-5045-47ed-b325-a737b515381c"]:
            user = db.login(User(c.message.chat.id, c.message.from_user.username))
            servers, err = user.servers_refresh()
            if err:
                bot.send_message(c.message.chat.id, content.ERROR.format(str(err)))
                return
            server = user.get_server_by_id(data[-1])
            if not server:
                bot.send_message(c.from_user.id, "None")
                return
            elif server.status.lower() == "active":
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
        case ["server", "stop", "49ada3cb-5045-47ed-b325-a737b515381c"]:
            user = db.login(User(c.message.chat.id, c.message.from_user.username))
            servers, err = user.servers_refresh()
            if err:
                bot.send_message(c.message.chat.id, content.ERROR.format(str(err)))
                return
            server = user.get_server_by_id(data[-1])
            if not server:
                bot.send_message(c.from_user.id, "None")
            elif server.status.lower() == "shutoff":
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
        case ["server", "refresh", "49ada3cb-5045-47ed-b325-a737b515381c"]:
            user = db.login(User(c.message.chat.id, c.message.from_user.username))
            servers, err = user.servers_refresh()
            if err:
                bot.send_message(c.message.chat.id, content.ERROR.format(str(err)))
                return
            server = user.get_server_by_id(data[-1])
            try:
                server.base.get()
            except Exception as err:
                bot.send_message(c.from_user.id, err)
                return
            server.refresh_info()
            server_info = server.get_pretty_info()
            bot.edit_message_text(server_info,c.from_user.id, c.message.id, parse_mode=content.md,
                            reply_markup=kb.keyboard_for_server(server.base.id, vnc_url=server.vnc_url))
        case _:
            print(data)
            bot.send_message(c.from_user.id, ", ".join(data))
def main():
    print("Service status: OK")
    bot.polling(none_stop=True, timeout=60)
    
if __name__ == "__main__":
    main()