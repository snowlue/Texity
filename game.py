import sqlite3

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext

from logger import log

con = sqlite3.connect("players.db", check_same_thread=False)
cur = con.cursor()
list_of_players = [i[0] for i in cur.execute('SELECT tg_id FROM cities').fetchall()]

RESOURCES, MARKET, POPULATION, CONSTRUCTION, FOREIGN_POLICY, INFO, WAITING_FOR_SUMM, CHANGE_OR_GO_TO_MENU_MARKET, NOT_ENOUGH_GOLD, BAD_SUMM, SUCCESSFUL_BUYING = range(
    2, 13)
WAITING_FOR_CITY_NAME, MENU = range(2)
WAITING_FOR_COUNT_TO_BUILD = 14
SUCCESSFUL_BUILD = 15
CHANGE_OR_GO_TO_MENU_BUILDINGS = 16

PRICE_OF_BUILDINGS = {
    'farms': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
    'sawmills': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
    'quarries': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
    'iron_mines': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
    'gold_mines': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]]
}

@log
def get_info_about_city(update: Update, context: CallbackContext):
    resources_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    user_id = update.message.from_user.id
    if user_id in list_of_players:
        resources_1 = cur.execute('SELECT farms FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        resources_2 = cur.execute('SELECT quarries FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        resources_3 = cur.execute('SELECT sawmills FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        resources_4 = cur.execute('SELECT iron_mines FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        resources_5 = cur.execute('SELECT gold_mines FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        update.message.reply_text('Ваши предприятия\n'
                                  '🧑🏻‍🌾 Фермы: {}\n'
                                  '🪨 Каменоломни: {}\n'
                                  '🪵 Лесопилки: {}\n'
                                  '🏭 Железные рудники: {}\n'
                                  '💰 Золотые рудники: {}'.format(
            resources_1, resources_2, resources_3, resources_4, resources_5
        ), reply_markup=resources_markup)
    else:
        update.message.reply_text('Нет такого пользователя ¯\_(ツ)_/¯')
    return INFO


@log
def resources(update: Update, context: CallbackContext):
    resources_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    user_id = update.message.from_user.id
    if user_id in list_of_players:
        stone = cur.execute('SELECT stone FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        wood = cur.execute('SELECT wood FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        food = cur.execute('SELECT food FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        iron = cur.execute('SELECT iron FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        gold = cur.execute('SELECT gold FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        gold_ore = cur.execute('SELECT gold_ore FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        iron_ore = cur.execute('SELECT iron_ore FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        update.message.reply_text('Ваши ресурсы\n'
                                  'Еда: {}\n'
                                  'Камни: {}\n'
                                  'Дерево: {}\n'
                                  'Железо: {}\n'
                                  'Золото: {}\n'
                                  'Золотая руда: {}\n'
                                  'Железная руда: {}'.format(food, stone, wood, iron, gold, gold_ore, iron_ore),
                                  reply_markup=resources_markup)
    else:
        update.message.reply_text('Нет такого пользователя ¯\_(ツ)_/¯')
    return RESOURCES


@log
def market(update: Update, context: CallbackContext):
    market_markup = ReplyKeyboardMarkup([['Еда', 'Дерево'],
                                         ['Камни', 'Железо'],
                                         ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("Рынок", reply_markup=market_markup)
    return MARKET


def buy_food(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц еды')
    context.chat_data['material'] = 'wood'
    return WAITING_FOR_SUMM


def buy_wood(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц дерева')
    context.chat_data['material'] = 'wood'
    return WAITING_FOR_SUMM


def buy_stone(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 1 единицу камня')
    context.chat_data['material'] = 'stone'
    return WAITING_FOR_SUMM


def buy_iron(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 1 единицу железа')
    context.chat_data['material'] = 'iron'
    return WAITING_FOR_SUMM


def check_summ(update: Update, context: CallbackContext):
    gold = cur.execute('SELECT gold FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
    markup_fail = ReplyKeyboardMarkup([['Попробовать еще раз'], ['Вернуться в меню']], one_time_keyboard=False,
                                      resize_keyboard=True)
    markup_success = ReplyKeyboardMarkup([['Продолжить покупки'], ['Вернуться в меню']], one_time_keyboard=False,
                                         resize_keyboard=True)
    summ = int(update.message.text)
    try:
        if summ > gold:
            update.message.reply_text('К сожалению, у вас недостаточно золота!', reply_markup=markup_fail)
            return CHANGE_OR_GO_TO_MENU_MARKET
        elif summ <= 0:
            raise ValueError
        else:
            update.message.reply_text('Покупка прошла упешно!', reply_markup=markup_success)
            tranzaction_buy(context.chat_data['material'], summ, update.message.from_user.id)
            return SUCCESSFUL_BUYING
    except ValueError:
        update.message.reply_text('Похоже, то что вы ввели, не выглядит как натуральное число.',
                                  reply_markup=markup_fail)
        return CHANGE_OR_GO_TO_MENU_MARKET


def build_farms(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной фермы составляет: \n'
                              ' 240 дерева \n'
                              ' 120 железа \n'
                              ' 240 дерева \n'
                              ' 200 еды для рабочих')
    context.chat_data['to_build'] = 'farms'
    return WAITING_FOR_COUNT_TO_BUILD


def build_quarries(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной каменоломни составляет: \n'
                              ' 240 дерева \n'
                              ' 120 железа \n'
                              ' 240 дерева \n'
                              ' 200 еды для рабочих')
    context.chat_data['to_build'] = 'quarries'
    return WAITING_FOR_COUNT_TO_BUILD


def build_sawmills(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной лесопилки составляет: \n'
                              ' 240 дерева \n'
                              ' 120 железа \n'
                              ' 240 дерева \n'
                              ' 200 еды для рабочих')
    context.chat_data['to_build'] = 'sawmills'
    return WAITING_FOR_COUNT_TO_BUILD


def build_iron_mines(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной железной шахты составляет: \n'
                              ' 240 дерева \n'
                              ' 120 железа \n'
                              ' 240 дерева \n'
                              ' 200 еды для рабочих')
    context.chat_data['to_build'] = 'iron_mines'
    return WAITING_FOR_COUNT_TO_BUILD


def build_gold_mines(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одного золотого рудника составляет: \n'
                              ' 240 дерева \n'
                              ' 120 железа \n'
                              ' 240 дерева \n'
                              ' 200 еды для рабочих')
    context.chat_data['to_build'] = 'gold_mines'
    return WAITING_FOR_COUNT_TO_BUILD


def check_build(update: Update, context: CallbackContext):
    count_of_buildings = int(update.message.text)
    markup_fail = ReplyKeyboardMarkup([['Попробовать еще раз'], ['Вернуться в меню']], one_time_keyboard=False,
                                      resize_keyboard=True)
    markup_success = ReplyKeyboardMarkup([['Продолжить строительство'], ['Вернуться в меню']], one_time_keyboard=False,
                                         resize_keyboard=True)
    try:
        spisok = []
        if count_of_buildings <= 0:
            raise ValueError
        for i in PRICE_OF_BUILDINGS[context.chat_data['to_build']]:
            total_count_of_resources = cur.execute('SELECT {} FROM resources WHERE tg_id = {}'.format(i[0], update.message.from_user.id)).fetchone()[0]
            if i[1] * count_of_buildings > total_count_of_resources:
                update.message.reply_text('К сожалению, у вас недостаточно ресурсов!', reply_markup=markup_fail)
                return CHANGE_OR_GO_TO_MENU_BUILDINGS
            spisok.append([i[0], i[1] * count_of_buildings])
        else:
            update.message.reply_text('Вы успешно построили предприятия!', reply_markup=markup_success)
            tranzaction_build(spisok[0][0], spisok[0][1], spisok[1][0], spisok[1][1], spisok[2][0], spisok[2][1],
                              context.chat_data['to_build'], count_of_buildings, update.message.from_user.id)
            return SUCCESSFUL_BUILD
    except ValueError:
        update.message.reply_text('Похоже, то что вы ввели, не выглядит как натуральное число.',
                                  reply_markup=markup_fail)
        return CHANGE_OR_GO_TO_MENU_BUILDINGS


def tranzaction_buy(type_of_material, summ, user):
    cur.execute('UPDATE resources SET gold = (SELECT gold FROM resources WHERE tg_id = {}) - {}'.format(user, summ))
    cur.execute(
        'UPDATE resources SET {} = (SELECT {} FROM resources WHERE tg_id = {}) + 5 * {}'.format(type_of_material,
                                                                                                type_of_material, user,
                                                                                                summ))
    con.commit()


def tranzaction_build(type_1, count_1, type_2, count_2, type_3, count_3, building, count_of_buildings, user):
    print(type_1, type_1, user, count_1)
    cur.execute(
        'UPDATE resources SET {} = (SELECT {} FROM resources WHERE tg_id = {}) - {}'.format(type_1, type_1, user,
                                                                                            count_1))
    cur.execute(
        'UPDATE resources SET {} = (SELECT {} FROM resources WHERE tg_id = {}) - {}'.format(type_2, type_2, user,
                                                                                            count_2))
    cur.execute(
        'UPDATE resources SET {} = (SELECT {} FROM resources WHERE tg_id = {}) - {}'.format(type_3, type_3, user,
                                                                                            count_3))
    cur.execute(
        'UPDATE buildings SET {} = (SELECT {} FROM buildings WHERE tg_id = {}) + {}'.format(building, building, user,
                                                                                           count_of_buildings))
    con.commit()


@log
def population(update: Update, context: CallbackContext):
    population_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text("Ваше население", reply_markup=population_markup)
    return POPULATION


@log
def construction(update: Update, context: CallbackContext):
    construction_markup = ReplyKeyboardMarkup([['Ферма', 'Каменоломня', 'Лесопилка'],
                                               ['Железный рудник', 'Золотой рудник'],
                                               ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        "Каких производств желаете построить?", reply_markup=construction_markup)
    return CONSTRUCTION


@log
def foreign_policy(update: Update, context: CallbackContext):
    foreign_policy_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text(
        "Внешняя политика", reply_markup=foreign_policy_markup)
    return FOREIGN_POLICY
