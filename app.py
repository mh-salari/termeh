#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jun 18 2020
@author: MohammadHossein Salari
@sorces:
    - https://github.com/eternnoir/pyTelegramBotAPI
"""
import telebot
from telebot import types
import logging as log
import pickle
import time
import sys
import os
import re

from watermark.watermark import watermark_image
import config

# logger = telebot.logger
# telebot.logger.setLevel(log.ERROR)

log.basicConfig(
    level=log.INFO, format="%(asctime)s %(levelname)s %(message)s")

users_dict = {}


class UserSettings:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.initialized = False
        self.step = "upload_logo"
        self.counter = 0
        self.watermark_path = None
        self.scale = 0.25
        self.transparency = 0.5
        self.position = "bottom_left"

    def __repr__(self):
        rep = f"chat_id: {self.chat_id}, watermark_path: {self.watermark_path}, " +\
              f"chat_id: {self.chat_id}, watermark_path: {self.watermark_path}, " +\
              f"scale: {self.scale}, : {self.transparency}, position: {self.position}"
        return rep


users_dict_pkl_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "data", "users_dict.pkl")


bot = telebot.TeleBot(config.bot_token, threaded=False, skip_pending=True)


def log_command(message):
    log.info(
        f"Command '{message.text}' has been received." +
        f"Chat data: '{message.chat.first_name} {message.chat.last_name}' @{message.chat.username}, id:{message.chat.id}"

    )


def save_users_dict(pkl_path):

    with open(pkl_path, "wb") as pkl:
        pickle.dump(users_dict, pkl)


def load_users_dict(pkl_path):

    with open(pkl_path, "rb") as pkl:
        users_dict = pickle.load(pkl)
    return users_dict


# def get_user_step(chat_id):
#     if chat_id in users_dict:
#         return users_dict[chat_id].step
#     else:
#         # users_dict[chat_id] = UserSettings(chat_id)
#         log.info('New user detected, who hasn\'t used "/start" yet')
#         return 0


all_content_types = ["text", "audio", "document", "photo", "sticker",
                     "video", "voice", "location", "contact", "video_note"]


@ bot.message_handler(commands=["start"])
def command_start(message):

    log_command(message)

    # if user hasn't used the "/start" command yet:
    if (message.chat.id not in users_dict) or users_dict[message.chat.id].initialized != True:

        users_dict[message.chat.id] = UserSettings(message.chat.id)

        # users_dict[message.chat.id].step = "upload_logo"
        markup = types.ForceReply(selective=False)
        bot.send_message(
            message.chat.id, "Termeh (ترمه) is a simple bot to add watermark on images." +
            "\nTo start please upload a transparent PNG logo with you want to use as watermark."
            + "\n[send your logo as a 'file' not 'photo' to keep it transparent]",
            reply_markup=markup)

    else:
        bot.send_message(
            message.chat.id, "Welcome Back! :)",
        )
        if users_dict[message.chat.id].initialized == True:

            users_dict[message.chat.id].step = "watermark"
            command_help(message)



# @bot.message_handler(commands=["stop"])
# def command_aborte(message):
#     log_command(message)
#     if users_dict[message.chat.id].initialized == False:

#         users_dict[message.chat.id].step = "upload_logo"
#         bot.send_message(
#             message.chat.id,
#             "Bot stoped",
#         )
#     else:
#         users_dict[message.chat.id].step = "stop"
#         bot.send_message(
#             message.chat.id,
#             "Bot stoped",
#         )


@bot.message_handler(commands=["initialize"])
def init_settings(message):
    log_command(message)
    users_dict[message.chat.id].step = "upload_logo"
    users_dict[message.chat.id].initialized = False
    markup = types.ForceReply(selective=False)

    bot.send_message(
        message.chat.id,
        "To start please upload a transparent PNG logo with you want to use as watermark."
        + "\n[send your logo as a 'file' not 'photo' to keep it transparent]",
        reply_markup=markup)


@bot.message_handler(commands=["help"])
def command_help(message):
    log_command(message)
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            "developer", url="telegram.me/mh_salari"
        )
    )

    help_message = "/start\n" +\
        "/initialize\n" +\
        "/logo\n" +\
        "/scale\n" +\
        "/transparency\n" +\
        "/position\n" +\
        "/help\n"

    bot.send_message(
        message.chat.id,
        help_message,
        reply_markup=keyboard,
    )


@bot.message_handler(commands=["logo"])
def init_upload_logo(message):
    log_command(message)
    users_dict[message.chat.id].step = "upload_logo"
    markup = types.ForceReply(selective=False)
    bot.send_message(
        message.chat.id, "please upload a transparent PNG logo with you want to use as watermark." +
                         "\n[send your logo as a 'file' not 'photo' to keep it transparent]",
        reply_markup=markup)


@bot.message_handler(func=lambda message: users_dict[message.chat.id].step == "upload_logo", content_types=all_content_types)
def save_logo(message):

    if message.content_type == "photo":

        markup = types.ForceReply(selective=False)
        bot.send_message(
            message.chat.id, "Send your logo as a 'file' not 'photo' to keep it transparent.",
            reply_markup=markup)

    elif message.content_type == "document":
        file_info = bot.get_file(message.document.file_id)
        _, extension = os.path.splitext(file_info.file_path)

        if extension.lower() == ".png":

            downloaded_file = bot.download_file(file_info.file_path)
            watermark_path = os.path.join(os.path.dirname(
                os.path.realpath(__file__)), "data", f"{message.chat.id}.png")
            with open(watermark_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            if watermark_path !=None:

                users_dict[message.chat.id].watermark_path = watermark_path
                if users_dict[message.chat.id].initialized == True:
                    bot.send_message(message.chat.id,
                            f"new logo uploded",
                            )
                    users_dict[message.chat.id].step = "watermark"
                    save_users_dict(users_dict_pkl_path)
                else:
                    users_dict[message.chat.id].step = "set_default_scale"
                    init_default_settings(message)
            else:
                markup = types.ForceReply(selective=False)
                bot.send_message(message.chat.id, "Please upload '.png' file",
                                reply_markup=markup)

        else:
            markup = types.ForceReply(selective=False)
            bot.send_message(
                message.chat.id, "Please upload '.png' file",
                reply_markup=markup)

    else:
        markup = types.ForceReply(selective=False)
        bot.send_message(
            message.chat.id, "Please upload '.png' file",
            reply_markup=markup)


@bot.message_handler(commands=["scale"])
def init_default_settings(message):
    log_command(message)
    markup = types.ForceReply(selective=False)
    
    bot.send_message(message.chat.id,
     "Set logo scale between (0.00 to 1.00)" +\
     f"\n[current value is {users_dict[message.chat.id].scale}]", 
     reply_markup=markup)
    users_dict[message.chat.id].step = "set_default_scale"


@bot.message_handler(func=lambda message: users_dict[message.chat.id].step == "set_default_scale", content_types=all_content_types)
def set_default_scale(message):

    try:
        scale = float(message.text)
        if scale > 1.0 or scale < 0.0:
            raise ValueError
        users_dict[message.chat.id].scale = scale
        if users_dict[message.chat.id].initialized == True:
            bot.send_message(message.chat.id,
                            f"scale value updated to: {users_dict[message.chat.id].scale}",
                            )
            users_dict[message.chat.id].step = "watermark"
            save_users_dict(users_dict_pkl_path)
        else:
            users_dict[message.chat.id].step = "transparency"
            init_default_transparency(message)
    except:
        markup = types.ForceReply(selective=False)
        bot.send_message(
            message.chat.id, f"invalid value for scale: {message.text}\n[0.00<valid scale<1.00]", reply_markup=markup)


@bot.message_handler(commands=["transparency"])
def init_default_transparency(message):
    log_command(message)
    markup = types.ForceReply(selective=False)
    bot.send_message(message.chat.id,
         "Set logo transparency between (0.00 to 1.00)" +\
         f"\n[current value is {users_dict[message.chat.id].transparency}] (smaller is more transparent)",
         reply_markup=markup)
    users_dict[message.chat.id].step = "set_default_transparency"


@bot.message_handler(func=lambda message: users_dict[message.chat.id].step == "set_default_transparency", content_types=all_content_types)
def set_default_transparency(message):

    try:
        transparency = float(message.text)
        if transparency > 1.0 or transparency < 0.0:
            raise ValueError

        users_dict[message.chat.id].transparency = transparency
        if users_dict[message.chat.id].initialized == True:
            bot.send_message(message.chat.id,
                            f"transparency value updated to: {users_dict[message.chat.id].transparency}",
                            )
            users_dict[message.chat.id].step = "watermark"
            save_users_dict(users_dict_pkl_path)
        else:
            users_dict[message.chat.id].step = "set_default_position"
            init_default_position(message)

    except:
        markup = types.ForceReply(selective=False)
        bot.send_message(
            message.chat.id, f"invalid value for transparency: {message.text} [0.00<transparency<1.00]", reply_markup=markup)


@bot.message_handler(commands=["position"])
def init_default_position(message):
    log_command(message)
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

    users_dict[message.chat.id].step = "set_default_position"
    bot.send_message(
        message.chat.id, "Set defalt watermark position",
        reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    if users_dict[call.from_user.id].step == "set_default_position":

        users_dict[call.from_user.id].step = "watermark"
        users_dict[call.from_user.id].position = call.data
        

        if users_dict[call.from_user.id].initialized == True:
            bot.send_message(call.from_user.id,
                            f"position value updated to: {users_dict[call.from_user.id].position}",
                            )
            users_dict[call.from_user.id].step = "watermark"
            save_users_dict(users_dict_pkl_path)
        else:
            users_dict[call.from_user.id].initialized = True
            bot.send_message(call.from_user.id,
                            f"We are good to go! you can start uploading your images to watermark them",
                            )

    elif users_dict[call.from_user.id].step == "watermark":
        pass


@bot.message_handler(func=lambda message: users_dict[message.chat.id].step == "watermark", content_types=["document", "photo"])
def watermarking(message):

    if message.content_type == "photo":

        file_info = bot.get_file(message.photo[-1].file_id)
        _, extension = os.path.splitext(file_info.file_path)

    elif message.content_type == "document":
        file_info = bot.get_file(message.document.file_id)
        _, extension = os.path.splitext(file_info.file_path)

    if extension.lower() in [".jpg", ".png", ".bmp"]:
        bot.send_chat_action(message.chat.id, 'typing')
        downloaded_file = bot.download_file(file_info.file_path)

        input_image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "data", f"{message.chat.id}_temp{extension}")
        with open(input_image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        user = users_dict[message.chat.id]

        output_image = watermark_image(
            user.watermark_path, input_image_path, user.scale, user.transparency, user.position, 15)

        output_image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "data", f"{message.chat.id}_temp_wm_{extension}")

        output_image.save(output_image_path)

        with open(output_image_path, 'rb') as im_f:
            bot.send_document(message.chat.id, im_f)


# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=["text"])
def command_default(message):
    log_command(message)
    bot.send_message(message.chat.id,
                     f"invalid command: '{message.text}', send /help to get instructions.")


def main_loop():

    if os.path.exists(users_dict_pkl_path):
        if os.path.getsize(users_dict_pkl_path) > 0:
            global users_dict
            users_dict = load_users_dict(users_dict_pkl_path)

    
    try:
        log.info("Starting bot polling...")
        bot.polling(none_stop=True)
    except Exception as err:
        log.error("Bot polling error: {0}".format(err.args))
        # bot.stop_polling()
        time.sleep(5)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        log.info("\nExiting by user request.\n")
        sys.exit(0)
