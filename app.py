from telebot import TeleBot
from telebot import apihelper

from config import TELEGRAM_TOKEN, CHAT_ID

import csv

from datetime import datetime

import uuid

import re

# proxy settings
# apihelper.proxy = {'http': 'http://45.55.53.22844578'}

bot = TeleBot(TELEGRAM_TOKEN)

user_dict = dict()

# for check email validity
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

FILENAME = 'output.csv'


class Request:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.uuid = str(uuid.uuid4())
        self.user_id = None
        self.datetime = None
        self.username = None
        self.email = None
        self.user_info = None
        
    def find_email(self):
        """Read a csv file"""
        try:
            with open(FILENAME, "r") as f_obj:
                reader = csv.reader(f_obj)
                for row in reader:
                    info = row[0].split(';')
                    if info[4] == self.email:
                        self.user_info = info
                        return True
            return False
        except FileNotFoundError:
            return False
        
    def save(self):
        self.datetime = datetime.now()

        with open(FILENAME, "a", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow([self.uuid, self.user_id, self.datetime.strftime('%Y-%m-%d %H:%M'), self.username, self.email])
    
    def is_subscriber(self) -> bool:
        try:
            status = bot.get_chat_member(CHAT_ID, self.user_id).status
        except apihelper.ApiException:
            status = 'undefined'
            
        if status in ['creator', 'administrator', 'member']:
            return True
        else:
            return False


@bot.message_handler(commands=['giveaway_command'])
def init_chat(message):
    markdown = """
    Greetings!
    To participate in giveaway, please let us know your email you used to sign up at the website.
    In case you don’t have an account at the website, please [Sign Up for free here](http://google.com)
    """
    msg = bot.reply_to(message, markdown, parse_mode="Markdown")
    bot.register_next_step_handler(msg, mail_processing)


def mail_processing(message):
        chat_id = message.chat.id
        email = message.text
        if not re.search(regex, email):
            msg = bot.reply_to(message, 'That does not look like an email. Please input full email you used to sign up '
                                        'at the website.')
            bot.register_next_step_handler(msg, mail_processing)
        else:
            request = Request(chat_id)
            user_dict[chat_id] = request
            request.email = email
            request.user_id = message.from_user.id
            request.username = message.from_user.username
            if not request.is_subscriber():
                msg = bot.reply_to(message, 'You need to be subscribed to our official [Channel](http://google.com) '
                                            'Please click the link and join the Channel to be able to participate into '
                                            'our giveaway. ', parse_mode="Markdown")
                bot.register_next_step_handler(msg, mail_processing)
                return

            if request.find_email():
                if request.user_id == request.user_info[1]:
                    bot.reply_to(message,
                                 'Oh-oh, it seems like you have already participated in this giveaway by entering '
                                 'this email. To keep the giveaway fair, we accept only one user account. '
                                 'You can always participate in other giveaways. To do so, just stay up to date '
                                 'with our [Channel](http://google.com)', parse_mode="Markdown")
                else: # another user
                    bot.reply_to(message,
                                 'Oh-oh, it seems like you have already participated in this giveaway by entering '
                                 'this email. To keep the giveaway fair, we accept only one user account. '
                                 'You can always participate in other giveaways. To do so, just stay up to date '
                                 'with our [Channel](http://google.com)', parse_mode="Markdown")
                    # bot.register_next_step_handler(msg, mail_processing)
            else:
                bot.reply_to(message, 'Thnx, bro')
                request.save()


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling()

# https://t.me/proxy?server=ru.tgproxy.today&port=8080&secret=ddfb175d6d7f820cdc73ab11edbdcdbd74