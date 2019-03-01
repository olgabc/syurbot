from utils.coll import Config
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from generation_funcs import generate_sentence


TOKEN = Config.get('TELEGRAM.token')
PROXY_URL = Config.get('TELEGRAM.proxy')

updater = Updater(
  token=TOKEN,
  request_kwargs=dict(proxy_url=PROXY_URL)
)
dispatcher = updater.dispatcher
updater.start_polling()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="""
я Сюробот,
я знаю команды "/book", "/wisdom"
я молодец.

Или поговорите со мной, мне скучно.
        """
    )


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def book_new_sentence(bot, update):

    text_gen_sen = generate_sentence(
        my_sentence="",
        word_source_id=2,
        sentence_source_id=2,
        sentence_length_min=7,
        sentence_length_max=15,
        unchangable_words_qty_max=3,
        fixed_words_qty_max=None,
        trash_words_qty_max=None
    )
    bot.send_message(chat_id=update.message.chat_id, text=text_gen_sen)


book_handler = CommandHandler('book', book_new_sentence, pass_args=False)
dispatcher.add_handler(book_handler)


def book_new_and_old_sentence(bot, update):

    text_gen_sen = generate_sentence(
        my_sentence="",
        word_source_id=2,
        sentence_source_id=2,
        sentence_length_min=7,
        sentence_length_max=15,
        unchangable_words_qty_max=3,
        fixed_words_qty_max=None,
        trash_words_qty_max=None,
        print_old_sentence=True
    )
    bot.send_message(chat_id=update.message.chat_id, text=text_gen_sen)


book_new_and_old_handler = CommandHandler('new_and_old', book_new_and_old_sentence, pass_args=False)
dispatcher.add_handler(book_new_and_old_handler)


def users_sentence(bot, update):

    talk_text = generate_sentence(
        my_sentence=update.message.text,
        word_source_id=1,
    )
    bot.send_message(chat_id=update.message.chat_id, text=talk_text)


talk_handler = MessageHandler(Filters.text, users_sentence)
dispatcher.add_handler(talk_handler)


def wisdom_new_and_old(bot, update):

    text_gen_sen = generate_sentence(
        my_sentence="",
        word_source_id=3,
        sentence_source_id=3,
        sentence_length_min=7,
        unchangable_words_qty_max=3,
        fixed_words_qty_max=None,
        trash_words_qty_max=None,
        print_old_sentence=True
    )
    bot.send_message(chat_id=update.message.chat_id, text=text_gen_sen)


wisdom_new_and_old_handler = CommandHandler('wisdom_new_and_old', wisdom_new_and_old, pass_args=False)
dispatcher.add_handler(wisdom_new_and_old_handler)


def wisdom(bot, update):

    text_gen_sen = generate_sentence(
        my_sentence="",
        word_source_id=3,
        sentence_source_id=3,
        sentence_length_min=7,
        unchangable_words_qty_max=3,
        fixed_words_qty_max=None,
        trash_words_qty_max=None,
        print_old_sentence=False
    )
    bot.send_message(chat_id=update.message.chat_id, text=text_gen_sen)


wisdom_handler = CommandHandler('wisdom', wisdom, pass_args=False)
dispatcher.add_handler(wisdom_handler)