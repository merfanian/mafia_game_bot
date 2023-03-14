from dotenv import load_dotenv

from utils.game_facilitator import Facilitator
from utils.telegramcommunicator import TelegramCommunicator

load_dotenv()

import os
import telebot

API_KEY = os.environ.get('API_KEY')

bot = telebot.TeleBot(API_KEY)


def init_game(tc):
    facilitator = Facilitator(tc)
    game = facilitator.handle_game_init()
    game.start()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi, Let's play mafia, reply /play to start")


@bot.message_handler(commands=['play'])
def play_handler(message):
    text = "Let's play 🎮"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    init_game(TelegramCommunicator(bot, message.chat.id))


if __name__ == '__main__':
    bot.infinity_polling()
