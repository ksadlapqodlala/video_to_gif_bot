import telebot
import logging
import urllib.request
import requests
import os
from moviepy.editor import *
import json
import shutil
import time
import threading


token = "<bot_token>"

heroku_app = "<heroku_app_link>"

def run_forever():
    while True:
        try:
            bot.polling()
        except:
            pass

def ping_app_sometimes():
    while True:
        requests.get(heroku_app)
        time.sleep(1200)            

def download_file(message_id, file_id):
    json_response = requests.get("https://api.telegram.org/bot" + token + "/getFile?file_id=" + file_id).json()
    file_path = json_response['result']['file_path']
    url = "https://api.telegram.org/file/bot" + token + "/" + file_path
    os.mkdir(message_id)
    file_name = ""
    file_name_reversed = ""
    for character in range(len(file_path)):
        if file_path[-character] != "/":
            file_name_reversed += file_path[-character]
        else:
            break
    for char in range(len(file_name_reversed)):
        file_name += file_name_reversed[-char]
    urllib.request.urlretrieve(url, message_id + "/" + file_name)
    return file_name    

def mp4_to_gif(message_id, filename):
    os.chdir(message_id)
    video = (VideoFileClip(filename))
    video.write_gif(filename + '.gif')
    os.chdir("..")
    
bot = telebot.TeleBot(token, parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def send_isntructions(message):
    bot.reply_to(message, "Hello! Send me the mp4 file and I will convert it to the gif file.\nYou can also download a gif file from Telegram.")

@bot.message_handler(content_types=['animation', 'video'])
def downl(message):
    bot.reply_to(message, "Wait a minute or two, please!\nIf your file's size is more than 50mb, than it won't be uploaded.\nIf link for the file won't be sended in a few minutes, either check your file's size or try again, please.")
    name = download_file(str(message.message_id), message.document.file_id)
    mp4_to_gif(str(message.message_id), name) 
    session = requests.Session()
    files = {'file': (open(str(message.message_id) + "/" + name + ".gif", 'rb'))}
    link = session.post('https://file.io', files=files)
    print(link.text)
    bot.reply_to(message, "Here is link for your gif: " + json.loads(link.text)['link'] + "\nIt will expire at " + json.loads(link.text)['expires'][0:10])
    shutil.rmtree(str(message.message_id), ignore_errors=True)


t1 = threading.Thread(target=run_forever)
t2 = threading.Thread(target=ping_app_sometimes)
t1.start()
t2.start()
