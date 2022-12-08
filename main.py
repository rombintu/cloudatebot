# local imports
# import os, sys

# external imports
import telebot
from telebot import types
import keystoneauth1.identity.v2 as auth

# internal imports
from internal import content, api
from tools import parser

envs = parser.parse_dotenv()

bot = telebot.TeleBot(envs["TOKEN"], parse_mode=None)
# db = database.Database(envs["DATABASE"])
osapi = api.OpenStackApi(
    auth = auth.Password(
        username=envs["OS_USERNAME"],
        tenant_name=envs["OS_TENANT_NAME"],
        auth_url=envs["OS_AUTH_URL"],
        password=envs["OS_PASSWORD"],
    )
)


@bot.message_handler(commands=['start', 'help'])
def handle_message_start(message):
    bot.send_message(
        message.chat.id, 
        content.start_message
    )

@bot.message_handler(commands=['ping'])
def handle_message_expenses(message):
    bot.send_message(message.chat.id, osapi.ping())

def main():
    print("Service status: OK")
    bot.polling(none_stop=True, timeout=60)

if __name__ == "__main__":
    main()