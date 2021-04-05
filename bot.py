from secrets import API_KEY
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler

#  не работает, потому что markup - локальная


def resources(update, context):
    update.message.reply_text(
        "Ваши ресурсы", reply_markup=markup)


def market(update, context):
    update.message.reply_text(
        "Рынок", reply_markup=markup)


def population(update, context):
    update.message.reply_text("Ваше население", reply_markup=markup)


def construction(update, context):
    update.message.reply_text(
        "Строительство", reply_markup=markup)


def foreign_policy(update, context):
    update.message.reply_text(
        "Внешняя политика", reply_markup=markup)


def main():
    updater = Updater(API_KEY)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("resources", resources))
    dp.add_handler(CommandHandler("market", market))
    dp.add_handler(CommandHandler("population", population))
    dp.add_handler(CommandHandler("construction", construction))
    dp.add_handler(CommandHandler("foreign_policy", foreign_policy))
    reply_keyboard = [['/resources', '/market'],
                      ['/population', '/construction'],
                      ['/foreign_policy']]

    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
