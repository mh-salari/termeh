# https://github.com/eternnoir/pyTelegramBotAPI


import telebot
from telebot import types
import logging as log
import time


import sys
import os
import re
from pathlib import Path
from os.path import dirname
from os.path import realpath


import logging

logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)

log.basicConfig(
    level=log.INFO, format="%(asctime)s %(levelname)s %(message)s")

# calcifer_path = dirname(dirname(dirname(realpath(__file__))))


TOKEN = "1244219534:AAEAuWL-hm8mBcNV6Ocr6IfzaDODeHQm4Uc"
bot = telebot.TeleBot(TOKEN, threaded=False)


known_users = []  # todo: save these in a file,
user_step = {}  # so they won't reset every time the bot restarts


def log_command(message):
    log.info(
        "Command {} has been received. Chat data: {}".format(
            message.text, str(message.chat)
        )
    )


def get_user_step(uid):
    if uid in user_step:
        return user_step[uid]
    else:
        known_users.append(uid)
        user_step[uid] = 0

        log.info('New user detected, who hasn\'t used "/start" yet')
        return 0


all_content_types = ["text", "audio", "document", "photo", "sticker",
                     "video", "voice", "location", "contact", "video_note"]


@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 0, content_types=all_content_types)
def confused_user(message):
    command_start(message)


@bot.message_handler(commands=["start"])
def command_start(message):

    log_command(message)

    # if user hasn't used the "/start" command yet:
    if (message.chat.id not in known_users) or (user_step[message.chat.id] == 0):
        user_step[message.chat.id] = "upload_logo"
        markup = types.ForceReply(selective=False)
        bot.send_message(
            message.chat.id, "Terme (ترمه) is a simple bot to add watermark on images." +
            "\nTo start please upload a transparent PNG logo with you want to use as watermark."
            + "\n[send your logo as a 'file' not 'photo' to keep it transparent]",
            reply_markup=markup)

    else:
        bot.send_message(
            message.chat.id, "Terme (ترمه) is a simple bot to add watermark on images." +
            "\nTo start please upload a transparent PNG logo with you want to use as watermark."
            + "\n[send your logo as a 'file' not 'photo' to keep it transparent]",
        )
        command_help(message)

        # command_help(message)  # show the new user the help page


@bot.message_handler(commands=["cancel", "stop"])
def command_aborte(message):

    user_step[message.chat.id] = "idel"
    bot.send_message(
        message.chat.id,
        "Command aborted!",
    )


@bot.message_handler(commands=["help"])
def command_help(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            "developer", url="telegram.me/mh_salari"
        )
    )

    bot.send_message(
        message.chat.id,
        "\nfssf",
        reply_markup=keyboard,
    )


@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == "upload_logo", content_types=all_content_types)
def save_logo(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        _, extension = os.path.splitext(file_info.file_path)
        if extension == ".jpg":
            markup = types.ForceReply(selective=False)
            bot.send_message(
                message.chat.id, "Send your logo as a 'file' not 'photo' to keep it transparent!",
                reply_markup=markup)

        elif extension == ".PNG" or extension == ".png":

            downloaded_file = bot.download_file(file_info.file_path)

            with open("image.jpg", 'wb') as new_file:
                new_file.write(downloaded_file)
                user_step[message.chat.id] = "init_default_scale"
                init_default_settings(message)
        else:
            markup = types.ForceReply(selective=False)
            bot.send_message(
                message.chat.id, "Please upload '.png' file",
                reply_markup=markup)

    except:
        markup = types.ForceReply(selective=False)
        bot.send_message(
            message.chat.id, "Please upload '.png' file",
            reply_markup=markup)


@bot.message_handler(commands=["init_default_scale"])
def init_default_settings(message):

    markup = types.ForceReply(selective=False)
    bot.send_message(
        message.chat.id, "Set logo scale between (0.00 to 1.00), [default value is 0.25]", reply_markup=markup)
    user_step[message.chat.id] = "set_default_scale"


@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == "set_default_scale", content_types=all_content_types)
def set_default_scale(message):

    try:
        scale = float(message.text)
        if scale > 1.0 or scale < 0.0:
            raise ValueError
        user_step[message.chat.id] = "init_default_transparency"
        init_default_transparency(message)
    except:
        markup = types.ForceReply(selective=False)
        bot.send_message(
            message.chat.id, f"invalid value for scale: {message.text}\n[0.00<valid scale<1.00]", reply_markup=markup)


@bot.message_handler(commands=["init_default_transparency"])
def init_default_transparency(message):

    markup = types.ForceReply(selective=False)
    bot.send_message(
        message.chat.id, "Set logo transparency between (0.00 to 1.00), [default value is 0.50]", reply_markup=markup)
    user_step[message.chat.id] = "set_default_transparency"


@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == "set_default_transparency", content_types=all_content_types)
def set_default_transparency(message):

    try:
        transparency = float(message.text)
        if transparency > 1.0 or transparency < 0.0:
            raise ValueError

        user_step[message.chat.id] = "set_default_position"
        init_default_position(message)

    except:
        markup = types.ForceReply(selective=False)
        bot.send_message(
            message.chat.id, f"invalid value for transparency: {message.text} [0.00<transparency<1.00]", reply_markup=markup)


@bot.message_handler(commands=["init_default_position"])
def init_default_position(message):

    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("Top Left",
                                          callback_data="top_left"),
               types.InlineKeyboardButton("Top Right",
                                          callback_data="top_right"),
               types.InlineKeyboardButton("Bottom Left",
                                          callback_data="bottom_left"),
               types.InlineKeyboardButton("Bottom Right",
                                          callback_data="bottom_right"),
               types.InlineKeyboardButton("Center",
                                          callback_data="center"),
               types.InlineKeyboardButton("Tile",
                                          callback_data="tile"))

    user_step[message.chat.id] = "set_default_position"
    bot.send_message(
        message.chat.id, "Set defalt watermark position",
        reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    if user_step[call.from_user.id] == "set_default_position":

        if call.data == "top_left":
            bot.answer_callback_query(call.id, "Answer is Top Left")
        elif call.data == "top_right":
            bot.answer_inline_query(call.id, "Answer is Top Right")
        elif call.data == "bottom_left":
            bot.answer_inline_query(call.id, "Answer is Bottom Left")
        elif call.data == "bottom_right":
            bot.answer_inline_query(call.id, "Answer is Bottom Right")
        elif call.data == "center":
            bot.answer_inline_query(call.id, "Answer is Center")
        elif call.data == "tile":
            bot.answer_inline_query(call.id, "Answer is Tile")

        bot.send_message(
            call.from_user.id, f"We are good to go!  you can start uploading your images to watermark them",
        )
        user_step[call.from_user.id] = "watermark"


def main_loop():

    try:
        log.info("Starting bot polling...")
        bot.polling(none_stop=True)
    except Exception as err:
        log.error("Bot polling error: {0}".format(err.args))
        bot.stop_polling()
        time.sleep(30)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        log.info("\nExiting by user request.\n")
        sys.exit(0)
