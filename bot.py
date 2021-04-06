from secrets import API_KEY
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler


markup = ReplyKeyboardMarkup([['/resources', '/market'],
                              ['/population', '/construction'],
                              ['/foreign_policy']], one_time_keyboard=False)
markup_2 = ReplyKeyboardMarkup([['/resources', '/market'],
                                ['/population', '/construction'],
                                ['/foreign_policy', '/menu']], one_time_keyboard=False)


def menu(update, context):
    update.message.reply_text('Welcome to бла-бла-бла',  reply_markup=markup_2)


def resources(update, context):
    update.message.reply_text(
        "resources", reply_markup=markup)
    menu(update, context)


def market(update, context):
    update.message.reply_text(
        "market", reply_markup=markup)
    menu(update, context)


def population(update, context):
    update.message.reply_text("population", reply_markup=markup)
    menu(update, context)


def construction(update, context):
    update.message.reply_text(
        "construction", reply_markup=markup)
    menu(update, context)


def foreign_policy(update, context):
    update.message.reply_text(
        "foreign_policy", reply_markup=markup)
    menu(update, context)


def run():
    updater = Updater(API_KEY)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("resources", resources))
    dp.add_handler(CommandHandler("market", market))
    dp.add_handler(CommandHandler("population", population))
    dp.add_handler(CommandHandler("construction", construction))
    dp.add_handler(CommandHandler("foreign_policy", foreign_policy))
    dp.add_handler((CommandHandler("menu", menu)))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run()
