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

    for i in range(0, 4):
        keyboard.add(types.InlineKeyboardButton(text=f"{mem.servers[i].name}", callback_data=f"{mem.servers[i].id}"))
    keyboard.add(
        types.InlineKeyboardButton(text=f"🔄", callback_data=f"refresh"),
        types.InlineKeyboardButton(text=f"➡️", callback_data=f"4>")
        )

    bot.send_message(message.chat.id, "Виртуальные машины", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda c: c.data)
def servers_callback(c: types.CallbackQuery):
    if c.data == "refresh":
        keyboard = types.InlineKeyboardMarkup()
        mem.refresh_servers()
        
        for i in range(0, 4):
            keyboard.add(types.InlineKeyboardButton(text=f"{mem.servers[i].name}", callback_data=f"{mem.servers[i].id}"))
        keyboard.add(
            types.InlineKeyboardButton(text=f"🔄", callback_data=f"refresh"),
            types.InlineKeyboardButton(text=f"➡️", callback_data=f"4>")
            )
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
                types.InlineKeyboardButton(text=f"🔄", callback_data=f"refresh"),
                types.InlineKeyboardButton(text=f"➡️", callback_data=f"{start_id+4}>")
            )
        else: 
            keyboard.add(
                types.InlineKeyboardButton(text=f"⬅️", callback_data=f"{start_id-4}>"),
                types.InlineKeyboardButton(text=f"🔄", callback_data=f"refresh"),
                types.InlineKeyboardButton(text=f"➡️", callback_data=f"{start_id+4}>")
            )
        bot.edit_message_reply_markup(c.from_user.id, c.message.id, reply_markup=keyboard)
        return
    else:
        bot.send_message(c.from_user.id, f"`{c.data}`\n\tSome info", parse_mode="markdown")

def main():
    print("Service status: OK")
    bot.polling(none_stop=True, timeout=60)
    
if __name__ == "__main__":
    main()