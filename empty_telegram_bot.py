#!/usr/bin/env python3

# An empty telegram bot as a template


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

# if this is __main__ 
if __name__ == "__main__":
    # create telegram bot object
    bot = TelegramBot()
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
            else:
                reply = 'I do not understand you.'
            bot.send_message(chat_id, reply)
        bot.save_offset()

print('done')




    
