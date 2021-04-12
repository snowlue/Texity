import sqlite3

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext

from logger import log

con = sqlite3.connect("players.db", check_same_thread=False)
cur = con.cursor()
list_of_players = [i[0] for i in cur.execute('SELECT tg_id FROM cities').fetchall()]

RESOURCES, MARKET, POPULATION, CONSTRUCTION, FOREIGN_POLICY = range(2, 7)

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
