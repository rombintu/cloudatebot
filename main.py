# local imports
import os, sys

# external imports
import telebot
from telebot import types

# internal imports
from internal import content, api, memory
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv("TOKEN"), parse_mode=None)
# db = database.Database(envs["DATABASE"])
# osapi = api.OpenStackApi()

mem = memory.MEM()
mem.refresh_servers()

@bot.message_handler(commands=['start', 'help'])
def handle_message_start(message):
    bot.send_message(
        message.chat.id, 
        content.start_message
    )

@bot.message_handler(commands=['servers'])
def handle_message_expenses(message):
    keyboard = types.InlineKeyboardMarkup()
    # mem.refresh_servers()
    if not mem.servers:
        bot.send_message(message.chat.id, "Список серверов пуст")
        return         
    for i in range(0, 4):
        keyboard.add(types.InlineKeyboardButton(text=f"{mem.servers[i].name}", callback_data=f"{mem.servers[i].id}"))
    keyboard.add(
        types.InlineKeyboardButton(text="🔄", callback_data=f"refresh"),
        types.InlineKeyboardButton(text="➡️", callback_data=f"4>")
        )

    bot.send_message(message.chat.id, f"Последнее обновление: \n\t{mem.updated.strftime('%d %B в %H:%M')}", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda c: c.data)
def servers_callback(c: types.CallbackQuery):
    if c.data == "refresh":
        keyboard = types.InlineKeyboardMarkup()
        mem.refresh_servers()
        
        for i in range(0, 4):
            keyboard.add(types.InlineKeyboardButton(text=f"{mem.servers[i].name}", callback_data=f"{mem.servers[i].id}"))
        keyboard.add(
            types.InlineKeyboardButton(text="🔄", callback_data=f"refresh"),
            types.InlineKeyboardButton(text="➡️", callback_data=f"4>")
            )
        bot.edit_message_text(
            f"Последнее обновление: \n\t{mem.updated.strftime('%d %B в %H:%M')}",
            c.from_user.id, c.message.id)
        bot.edit_message_reply_markup(c.from_user.id, c.message.id, reply_markup=keyboard)
        return

    elif c.data[-1] == ">":
        start_id = int(c.data[:-1])
        if start_id <= 0: start_id = 0
        elif start_id >= len(mem.servers): start_id = 0 
        keyboard = types.InlineKeyboardMarkup()
        
        for i in range(start_id, start_id+4):
            keyboard.add(types.InlineKeyboardButton(text=f"{mem.servers[i].name}", callback_data=f"{mem.servers[i].id}"))
            if i == len(mem.servers)-1: 
                break
        if start_id == 0:
            keyboard.add(
                types.InlineKeyboardButton(text="🔄", callback_data=f"refresh"),
                types.InlineKeyboardButton(text="➡️", callback_data=f"{start_id+4}>")
            )
        else: 
            keyboard.add(
                types.InlineKeyboardButton(text="⬅️", callback_data=f"{start_id-4}>"),
                types.InlineKeyboardButton(text="🔄", callback_data=f"refresh"),
                types.InlineKeyboardButton(text="➡️", callback_data=f"{start_id+4}>")
            )
        bot.edit_message_reply_markup(c.from_user.id, c.message.id, reply_markup=keyboard)
        return
    else:
        server = mem.server_find(c.data)
        server_info = "Функционал не допилен"
        keyboard = types.InlineKeyboardMarkup(row_width=4)
        if server:
            server_info = server.get_pretty_info()
            keyboard.add(
                types.InlineKeyboardButton(text="⚙️", callback_data="settings"),
                types.InlineKeyboardButton(text="🔑", callback_data="key"),
            )
            keyboard.add(
                types.InlineKeyboardButton(text="Обновить информацию", callback_data="fresh"),
            )
            keyboard.add(
                types.InlineKeyboardButton(text="▶️", callback_data="start"),
                types.InlineKeyboardButton(text="⏹", callback_data="stop"),
                types.InlineKeyboardButton(text="🔁", callback_data="soft_reboot"),
                types.InlineKeyboardButton(text="🔂", callback_data="hard_reboot"),
            )
        bot.send_message(c.from_user.id, server_info, parse_mode="markdown", reply_markup=keyboard)

def main():
    print("Service status: OK")
    bot.polling(none_stop=True, timeout=60)
    
if __name__ == "__main__":
    main()