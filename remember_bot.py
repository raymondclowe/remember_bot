#!/usr/bin/env python3

# Remember things and recall them. Keep things from different user id distinct. Persist the data in a json file.

# Based on An empty telegram bot as a template


import json
from time import sleep
import requests

import secrets


# telegram bot api class
class TelegramBot:
    def __init__ (self):
        self.token = secrets.TELEGRAM_BOT_TOKEN
        self.api_url = 'https://api.telegram.org/bot{}/'.format(self.token)
        self.session = requests.Session()
        self.offset = 0
        self.previous_offset = -1
        self.offset_filename = "telegram_update_offset.txt"
        self.get_next_update()

    def get_next_update(self):
        if self.offset == 0:
            try:
                with open(self.offset_filename, 'r') as f:
                    self.offset = int(f.read()) - 1
            except:
                with open(self.offset_filename, 'w') as f:
                    f.write(str(self.offset))
        params = {'offset': self.offset + 1, 'limit': 1, 'timeout': 10}
        response = self.session.get(self.api_url + 'getUpdates', params = params)
        if response.status_code != 200:
            return None
        try:
            response_json = response.json()
        except:
            return None
        if 'result' not in response_json:
            return None
        if len(response_json['result']) == 0:
            return []
        if response_json['result'][0]['update_id'] != self.offset:
            self.offset = response_json['result'][0]['update_id']
            return response_json['result'][0]
        return None

    def save_offset(self):
        if self.offset != self.previous_offset:
            with open(self.offset_filename, 'w') as f:
                f.write(str(self.offset))
            self.previous_offset = self.offset

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        response = self.session.post(self.api_url + 'sendMessage', params = params)
        return response.status_code == 200

# define the memory class
class Memory:
    def __init__(self):
        self.memory_filename = "memory.json"
        self.memory = {}
        self.load_memory()

    def load_memory(self):
        try:
            with open(self.memory_filename, 'r') as f:
                self.memory = json.load(f)
        except:
            pass

    def save_memory(self):
        with open(self.memory_filename, 'w') as f:
            json.dump(self.memory, f)

    def remember(self, user_id, thing):
        if user_id not in self.memory:
            self.memory[user_id] = []
        self.memory[user_id].append(thing)
        self.save_memory()

    def recall(self, user_id):
        if user_id not in self.memory:
            return None
        return self.memory[user_id]

# if this is __main__ 
if __name__ == "__main__":
    # create telegram bot object
    bot = TelegramBot()

    # create memory object
    memory = Memory()

    # loop continuously until keypress or break
    while True:
        # wait one second
        sleep(1)
        update = bot.get_next_update()
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            first_name = update['message']['from']['first_name']
            text = update['message']['text']
            if text == '/start':
                reply = 'Hello {}({})! I am an empty bot. I will do nothing'.format(first_name,chat_id)
            elif text == '/help':
                reply = 'I will remember things when you say /remember <thing> and recall them when you say /recall'
            # if the text starts with /remember the save the rest of the string as a thing
            elif text.startswith('/remember'):
                thing = text[10:]
                reply = 'I will remember {}'.format(thing)
                memory.remember(chat_id, thing)
            # if the text starts with /recall the recall the thing
            elif text.startswith('/recall'):
                things = memory.recall(chat_id)
                if things is None:
                    reply = 'I have no memory'
                else:
                    # turn the list of things into a string
                    reply = 'I remember {}'.format(', '.join(things))
            else:
                reply = 'I do not understand you.'
            bot.send_message(chat_id, reply)
        bot.save_offset()




print('done')




    
