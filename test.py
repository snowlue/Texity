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
import sqlite3

markup = ReplyKeyboardMarkup([['Ресурсы', 'Рынок'],
                              ['Население', 'Строительство'],
                              ['Внешняя политика']], one_time_keyboard=False)
MENU, RESOURCES, MARKET, POPULATION, CONSTRUCTION, FOREIGN_POLICY = range(6)
con = sqlite3.connect("players (1).db")
cur = con.cursor()

list_of_players = [i for i in cur.execute('''SELECT tg_id FROM cities''').fetchall()]
NAME_OF_CITY = ''
USER = ''


@log
def start(update: Update, context: CallbackContext) -> int:
    global NAME_OF_CITY, USER
    user_id = update.message.from_user.id
    print(user_id)
    if user_id not in list_of_players:
        update.message.reply_text(
            '''
Приветствуем тебя в Texity - пошаговой стратегии, в которой ты можешь развивать свой город, чтобы достичь светлого экономического будущего.

Итак, введи имя своего города! ''',
        )
        name = update.message.text
        # в name попадаеет /start
        update.message.reply_text(
            '''
    Прекрасный выбор! Мы уверены, что ваш город с гордым именем "{}" ждут небывалые свершения.
    Удачи, император.
    Вы всегда можете отправить команду /help, чтобы получить подробную справку по управлению и механикам.
    '''.format(name),
        )
        cur.execute('''INSERT INTO cities(tg_id, city) VALUES({}, {})'''.format(user_id, name))
        NAME_OF_CITY = name
    if not NAME_OF_CITY:
        NAME_OF_CITY = cur.execute('''SELECT city FROM cities WHERE tg_id = {}'''.format(user_id))
    USER = user_id
    return MENU


@log
def help(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    # todo: Вызввать админов или порешать, как должен работать /help
    update.message.reply_text(
        'Мир суров. Поэтому рабирайся сам.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


@log
def menu(update: Update, context: CallbackContext):
    update.message.reply_text("Добро пожаловать в Город {}".format(NAME_OF_CITY), reply_markup=markup)
    return MENU


@log
def resources(update: Update, context: CallbackContext):
    global NAME_OF_CITY, USER
    resources_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False)
    update.message.reply_text(
        "Ваши ресурсы", reply_markup=resources_markup)
    user_id = update.message.from_user.id
    print(user_id)
    name = update.message.text
    # в name попадаеет /start
    if user_id in list_of_players:
        resources_1 = cur.execute('''SELECT farms FROM cities WHERE tg_id = {}'''.format(user_id)).fetchone()
        resources_2 = cur.execute('''SELECT quarries FROM cities WHERE tg_id = {}'''.format(user_id)).fetchone()
        resources_3 = cur.execute('''SELECT sawmills FROM cities WHERE tg_id = {}'''.format(user_id)).fetchone()
        resources_4 = cur.execute('''SELECT iron mines FROM cities WHERE tg_id = {}'''.format(user_id)).fetchone()
        resources_5 = cur.execute('''SELECT gold mines FROM cities WHERE tg_id = {}'''.format(user_id)).fetchone()
        update.message.reply_text('Фермы:' + str(resources_1))
        update.message.reply_text('Каменоломни:' + str(resources_2))
        update.message.reply_text('Лесопилки:' + str(resources_3))
        update.message.reply_text('Железные заводы:' + str(resources_4))
        update.message.reply_text('Заводы по производству золота:' + str(resources_5))
    else:
        update.message.reply_text('Нет такого пользователя')
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
        entry_points=[CommandHandler('start', start)],
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
