import sqlite3
from secrets import API_KEY

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

from logger import log

markup = ReplyKeyboardMarkup([['Ресурсы', 'Рынок'],
                              ['Население', 'Строительство'],
                              ['Внешняя политика']], one_time_keyboard=False, resize_keyboard=True)
WAITING_FOR_CITY_NAME, MENU, RESOURCES, MARKET, POPULATION, CONSTRUCTION, FOREIGN_POLICY = range(7)
con = sqlite3.connect("players.db", check_same_thread=False)
cur = con.cursor()
list_of_players = [i[0] for i in cur.execute('SELECT tg_id FROM cities').fetchall()]


@log
def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    if user_id not in list_of_players:
        update.message.reply_text(
            '''
Приветствуем тебя в Texity - пошаговой стратегии, в которой ты можешь развивать свой город, чтобы достичь светлого экономического будущего.

Итак, введи имя своего города! ''',
        )

        return WAITING_FOR_CITY_NAME

    context.chat_data['city_name'] = cur.execute(
        'SELECT city FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    update.message.reply_text("Вновь добро пожаловать в {}!".format(
        context.chat_data['city_name']), reply_markup=markup)
    return MENU


@log
def set_name(update: Update, context: CallbackContext) -> int:
    name, user_id = update.message.text, update.message.from_user.id
    update.message.reply_text('''
Прекрасный выбор! Мы уверены, что ваш город с гордым именем «{}» ждут небывалые свершения.
Удачи, император.
Вы всегда можете отправить команду /help, чтобы получить подробную справку по управлению и механикам.
    '''.format(name),
    )
    cur.execute('''INSERT INTO cities VALUES ({}, "{}")'''.format(user_id, name))
    cur.execute('''INSERT INTO buildings VALUES ({}, 1, 1, 1, 1, 1)'''.format(user_id))
    cur.execute('''INSERT INTO resources VALUES ({}, 1000, 1000, 1000, 1000, 1000)'''.format(user_id))
    list_of_players.append(user_id)
    con.commit()
    context.chat_data['city_name'] = name
    

    # ? Не совсем понимаю, зачем это нужно ¯\_(ツ)_/¯
    # if not context.chat_data['city_name']:
    #     context.chat_data['city_name'] = cur.execute('SELECT city FROM cities WHERE tg_id = {}'.format(user_id))

    update.message.reply_text("Добро пожаловать в {}!".format(context.chat_data['city_name']), reply_markup=markup)
    return MENU


@log
def help(update: Update, context: CallbackContext) -> int:
    # todo: Вызввать админов или порешать, как должен работать /help
    update.message.reply_text(
        'Мир суров. Поэтому рабирайся сам.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


@log
def menu(update: Update, context: CallbackContext):
    update.message.reply_text("Добро пожаловать в {}!".format(context.chat_data['city_name']), reply_markup=markup)
    return MENU


@log
def resources(update: Update, context: CallbackContext):
    resources_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    user_id = update.message.from_user.id
    if user_id in list_of_players:
        resources_1 = cur.execute('SELECT farms FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        resources_2 = cur.execute('SELECT quarries FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        resources_3 = cur.execute('SELECT sawmills FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        resources_4 = cur.execute('SELECT iron_mines FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        resources_5 = cur.execute('SELECT gold_mines FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        update.message.reply_text('Ваши ресурсы\n'
                                  '🧑🏻‍🌾 Фермы: {}\n'
                                  '🪨 Каменоломни: {}\n'
                                  '🪵 Лесопилки: {}\n'
                                  '🏭 Железные заводы: {}\n'
                                  '💰 Заводы по производству золота: {}'.format(
                                      resources_1, resources_2, resources_3, resources_4, resources_5
                                  ), reply_markup=resources_markup)
    else:
        update.message.reply_text('Нет такого пользователя ¯\_(ツ)_/¯')
    return RESOURCES


@log
def market(update: Update, context: CallbackContext):
    market_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text("Рынок", reply_markup=market_markup)
    return MARKET


@log
def population(update: Update, context: CallbackContext):
    population_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text("Ваше население", reply_markup=population_markup)
    return POPULATION


@log
def construction(update: Update, context: CallbackContext):
    construction_markup = ReplyKeyboardMarkup([['Ферма', 'Каменоломня', 'Лесопилка'],
                                               ['Железный рудник', 'Золотой рудник'],
                                               ['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text(
        "Каких производств желаете построить?", reply_markup=construction_markup)
    return CONSTRUCTION


@log
def foreign_policy(update: Update, context: CallbackContext):
    foreign_policy_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text(
        "Внешняя политика", reply_markup=foreign_policy_markup)
    return FOREIGN_POLICY


def run():
    updater = Updater(API_KEY)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_CITY_NAME: [MessageHandler(Filters.text, set_name)],
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
