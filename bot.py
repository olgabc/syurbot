from utils.coll import Config
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import ConversationHandler
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


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="""
я Сюробот,
я знаю команду "/book",
я молодец.

Еще знаю команду "/answer" + ваше предложение,
Например, "/answer Никогда не надоест."

Или поговорите со мной, мне скучно.
        """
    )


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def book_sentence(bot, update):

    text_gen_sen = generate_sentence("ann_kar")
    bot.send_message(chat_id=update.message.chat_id, text=text_gen_sen)


book_handler = CommandHandler('book', book_sentence, pass_args=False)
dispatcher.add_handler(book_handler)


def users_words(bot, update, args):

    text_gen_sen = generate_sentence(my_sentence=" ".join(args))
    bot.send_message(chat_id=update.message.chat_id, text=text_gen_sen)


answer_handler = CommandHandler('answer', users_words, pass_args=True)
dispatcher.add_handler(answer_handler)


def users_sentence(bot, update):

    talk_text = generate_sentence(my_sentence=update.message.text)
    bot.send_message(chat_id=update.message.chat_id, text=talk_text)


talk_handler = MessageHandler(Filters.text, users_sentence)
dispatcher.add_handler(talk_handler)