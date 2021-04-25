from secrets import API_KEY
from logger import log

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

ABOUT_RESOURCES, ABOUT_MARKET, ABOUT_POPULATION, ABOUT_CONSTRUCTION, ABOUT_FOREIGN_POLICY, ABOUT_CITY, HELP = range(17, 23)


@log
def help(update: Update, context: CallbackContext):

    update.message.reply_text(
        'Постройте свой город и реализуйте его действия, нажмите на кнопки, чтобы узнать больше информации')
    return HELP


@log
def about_market(update: Update, context: CallbackContext):
    update.message.reply_text(
        'На рынке Вы можете покупать ресурсы за золото.')
    return ABOUT_MARKET


@log
def about_city(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Повышайте уровень своего города для увеличения производства. В городе Вы можте узнать количество производств')
    return ABOUT_CONSTRUCTION


@log
def about_resources(update: Update, context: CallbackContext):
    update.message.reply_text(
        'В ресурсах можно узнать количество отределенного вида ресурсов и переплавить различные виды руды')
    return ABOUT_RESOURCES


@log
def about_population(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Бла-бла-бла')
    return ABOUT_POPULATION


@log
def about_constrution(update: Update, context: CallbackContext):
    update.message.reply_text(
        'В строительстве Вы можете строить здания')
    return ABOUT_CONSTRUCTION


@log
def about_foreign_policy(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Бла-бла-бла')
    return ABOUT_FOREIGN_POLICY


def run():
    updater = Updater(API_KEY)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [MessageHandler(Filters.regex('^(Город)$'), get_info_about_city),
                   MessageHandler(Filters.regex('^(Ресурсы)$'), resources),
                   MessageHandler(Filters.regex('^(Рынок)$'), market),
                   MessageHandler(Filters.regex('^(Население)$'), population),
                   MessageHandler(Filters.regex('^(Строительство)$'), construction),
                   MessageHandler(Filters.regex('^(Внешняя политика)$'), foreign_policy)],
            ABOUT_RESOURCES: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                              MessageHandler(Filters.regex('^(Про ресурсы)$'), about_resources)],
            ABOUT_MARKET: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                           MessageHandler(Filters.regex('^(Про рынлк)$'), about_market)],
            ABOUT_POPULATION: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                               MessageHandler(Filters.regex('^(Про население)$'), about_population)],
            ABOUT_CONSTRUCTION: [MessageHandler(Filters.regex('^(Про строительство)$'), about_constrution),
                                 MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],
            ABOUT_FOREIGN_POLICY: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                   MessageHandler(Filters.regex('^(Про внешнюю политику)$'), about_foreign_policy)],
            HELP: [[MessageHandler(Filters.regex('^(Про рынок)$'), about_market),
                    MessageHandler(Filters.regex('^(Про город)$'), about_city),
                    MessageHandler(Filters.regex('^(Про ресурсы)$'), about_resources)],
                  [MessageHandler(Filters.regex('^(Про население)$'), about_population),
                    MessageHandler(Filters.regex('^(Про строительство)$'), about_constrution),
                    MessageHandler(Filters.regex('^(Про внешнюю политику)$'), about_foreign_policy)],
                  [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)]]
        },
        fallbacks=[CommandHandler('cancel', menu)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


run()
