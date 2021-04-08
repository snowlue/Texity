from secrets import API_KEY

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from logger import log

markup = ReplyKeyboardMarkup([['Ресурсы', 'Рынок'],
                              ['Население', 'Строительство'],
                              ['Внешняя политика']], one_time_keyboard=False)
MENU, RESOURCES, MARKET, POPULATION, CONSTRUCTION, FOREIGN_POLICY = range(6)


@log
def menu(update: Update, context: CallbackContext):
    update.message.reply_text("Добро пожаловать в Город {}.format(name_of_city)", reply_markup=markup)
    return MENU


@log
def resources(update: Update, context: CallbackContext):
    resources_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False)
    update.message.reply_text(
        "Ваши ресурсы", reply_markup=resources_markup)
    return RESOURCES


@log
def market(update: Update, context: CallbackContext):
    market_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False)
    update.message.reply_text(
        "Рынок", reply_markup=market_markup)
    return MARKET


@log
def population(update: Update, context: CallbackContext):
    population_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False)
    update.message.reply_text("Ваше население", reply_markup=population_markup)
    return POPULATION


@log
def construction(update: Update, context: CallbackContext):
    construction_markup = ReplyKeyboardMarkup([['Ферма', 'Каменоломня', 'Лесопилка'],
                                               ['Железный рудник', 'Золотой рудник'],
                                               [['Вернуться в меню']]], one_time_keyboard=False)
    update.message.reply_text(
        "Каких производств желаете построить?", reply_markup=construction_markup)
    return CONSTRUCTION


@log
def foreign_policy(update: Update, context: CallbackContext):
    foreign_policy_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False)
    update.message.reply_text(
        "Внешняя политика", reply_markup=foreign_policy_markup)
    return FOREIGN_POLICY


def run():
    updater = Updater(API_KEY)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', menu)],
        states={
            MENU: [MessageHandler(Filters.regex('^(Ресурсы)$'), resources),
                   MessageHandler(Filters.regex('^(Рынок)$'), market),
                   MessageHandler(Filters.regex('^(Население)$'), population),
                   MessageHandler(Filters.regex('^(Строительство)$'), construction),
                   MessageHandler(Filters.regex('^(Внешняя политика)$'), foreign_policy)],
            RESOURCES: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],
            MARKET: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],
            POPULATION: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],
            CONSTRUCTION: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],
            FOREIGN_POLICY: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],
        },
        fallbacks=[CommandHandler('cancel', menu)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run()
