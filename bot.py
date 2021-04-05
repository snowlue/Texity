from secrets import API_KEY

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater

from logger import log

markup = ReplyKeyboardMarkup([['Ресурсы', 'Рынок'],
                              ['Население', 'Строительство'],
                              ['Внешняя политика']], one_time_keyboard=False)


@log
def resources(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Ваши ресурсы", reply_markup=markup)


@log
def market(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Рынок", reply_markup=markup)


@log
def population(update: Update, context: CallbackContext):
    update.message.reply_text("Ваше население", reply_markup=markup)


@log
def construction(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Строительство", reply_markup=markup)


@log
def foreign_policy(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Внешняя политика", reply_markup=markup)


def run():
    updater = Updater(API_KEY)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text("Ресурсы"), resources))
    dp.add_handler(MessageHandler(Filters.text("Рынок"), market))
    dp.add_handler(MessageHandler(Filters.text("Население"), population))
    dp.add_handler(MessageHandler(Filters.text("Строительство"), construction))
    dp.add_handler(MessageHandler(Filters.text("Внешняя политика"), foreign_policy))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run()
