import logging

from dotenv import load_dotenv

from entity.game import Game
from entity.player import Player
from entity.role import GodFather, HostageTaker, \
    DoctorLecter, Doctor, Detective, \
    Sniper, Guard, Investigator, Armored
from utils.telegramcommunicator import TelegramCommunicator

load_dotenv()

import os
import telebot

API_KEY = os.environ.get('API_KEY')

bot = telebot.TeleBot(API_KEY)


def init_game(chat_id):
    game = Game([Player("godfather", GodFather()),
                 Player("doctor", Doctor()),
                 Player("drlecter", DoctorLecter()),
                 Player("detective", Detective()),
                 Player("hostage taker", HostageTaker()),
                 Player("investigator", Investigator()),
                 Player("sniper", Sniper()),
                 Player("guard", Guard()),
                 Player("armored", Armored())
                 ], TelegramCommunicator(bot, chat_id))
    game.start()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi, Let's play mafia, reply /play to start")


@bot.message_handler(commands=['play'])
def sign_handler(message):
    text = "Let's play"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    init_game(message.chat.id)


if __name__ == '__main__':
    bot.infinity_polling()
