import sqlite3

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext

from logger import log

img_market = open("market.jpg", 'rb')

con = sqlite3.connect("players.db", check_same_thread=False)
cur = con.cursor()
list_of_players = [i[0] for i in cur.execute('SELECT tg_id FROM cities').fetchall()]

WAITING_FOR_CITY_NAME, MENU, RESOURCES, MARKET, POPULATION, CONSTRUCTION, FOREIGN_POLICY, INFO, \
WAITING_FOR_SUM_TO_BUY, CHANGE_OR_GO_TO_MENU_MARKET, NOT_ENOUGH_GOLD, BAD_SUMM, SUCCESSFUL_BUYING, \
WAITING_FOR_COUNT_TO_BUILD, SUCCESSFUL_BUILD, CHANGE_OR_GO_TO_MENU_BUILDINGS, WAITING_FOR_TYPE_OF_METAL, \
WAITING_FOR_COUNT_OF_METAL, SUCCESSFUL_REMELTING, CHANGE_OR_GO_TO_MENU_REMELTING = range(21)

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
        resources_1, resources_2, resources_3, resources_4, resources_5), reply_markup=resources_markup)
    return INFO


@log
def resources(update: Update, context: CallbackContext):
    resources_markup = ReplyKeyboardMarkup([['Переплавить руду'], ['Вернуться в меню']], one_time_keyboard=False,
                                           resize_keyboard=True)
    user_id = update.message.from_user.id
    stone = cur.execute('SELECT stone FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    wood = cur.execute('SELECT wood FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    food = cur.execute('SELECT food FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    iron = cur.execute('SELECT iron FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    gold = cur.execute('SELECT gold FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    gold_ore = cur.execute('SELECT gold_ore FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    iron_ore = cur.execute('SELECT iron_ore FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    update.message.reply_text('Ваши ресурсы\n'
                              '🥩 Еда: {}\n'
                              '🪨 Камни: {}\n'
                              '🪵 Дерево: {}\n'
                              '🥈 Железо: {}\n'
                              '💰 Золото: {}\n'
                              '🏭 Золотая руда: {}\n'
                              '🏭 Железная руда: {}'.format(food, stone, wood, iron, gold, gold_ore, iron_ore),
                              reply_markup=resources_markup)
    return RESOURCES


def market(update: Update, context: CallbackContext):
    market_markup = ReplyKeyboardMarkup([['Еда', 'Дерево'],
                                         ['Камни', 'Железо'],
                                         ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_photo(img_market, "Рынок", reply_markup=market_markup)
    img_market.seek(0)
    return MARKET


def population(update: Update, context: CallbackContext):
    population_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text("Ваше население", reply_markup=population_markup)
    return POPULATION


def construction(update: Update, context: CallbackContext):
    construction_markup = ReplyKeyboardMarkup([['Ферма', 'Каменоломня', 'Лесопилка'],
                                               ['Железный рудник', 'Золотой рудник'],
                                               ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        "Каких производств желаете построить?", reply_markup=construction_markup)
    return CONSTRUCTION


def remelting(update: Update, context: CallbackContext):
    remelting_markup = ReplyKeyboardMarkup([['Железная руда', 'Золотая руда'],
                                            ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Какой тип руды хотите переплавить?', reply_markup=remelting_markup)
    return WAITING_FOR_TYPE_OF_METAL


def buy_food(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц еды')
    context.chat_data['material'] = 'food'
    return WAITING_FOR_SUM_TO_BUY


def buy_wood(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц дерева')
    context.chat_data['material'] = 'wood'
    return WAITING_FOR_SUM_TO_BUY


def buy_stone(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 1 единицу камня')
    context.chat_data['material'] = 'stone'
    return WAITING_FOR_SUM_TO_BUY


def buy_iron(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 1 единицу железа')
    context.chat_data['material'] = 'iron'
    return WAITING_FOR_SUM_TO_BUY


def check_buy(update: Update, context: CallbackContext):
    gold = cur.execute('SELECT gold FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
    markup_fail = ReplyKeyboardMarkup([['Попробовать еще раз'], ['Вернуться в меню']], one_time_keyboard=False,
                                      resize_keyboard=True)
    markup_success = ReplyKeyboardMarkup([['Продолжить покупки'], ['Вернуться в меню']], one_time_keyboard=False,
                                         resize_keyboard=True)
    try:
        summ = int(update.message.text)
        if summ > gold:
            update.message.reply_text('К сожалению, у вас недостаточно золота!', reply_markup=markup_fail)
            return CHANGE_OR_GO_TO_MENU_MARKET
        elif summ <= 0:
            raise ValueError
        else:
            update.message.reply_text('Покупка прошла упешно!', reply_markup=markup_success)
            tranzaction_buy(context.chat_data['material'], summ, update.message.from_user.id)
            count = cur.execute('SELECT {} FROM resources WHERE tg_id = {}'
                                .format(context.chat_data['material'], update.message.from_user.id)).fetchone()[0]
            gold = \
                cur.execute(
                    'SELECT gold FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
            if context.chat_data['material'] == 'food':
                update.message.reply_text('Ваша еда: {}\nВаше золото: {}'.format(count, gold))
            elif context.chat_data['material'] == 'wood':
                update.message.reply_text('Ваша дерево: {}\nВаше золото: {}'.format(count, gold))
            elif context.chat_data['material'] == 'stone':
                update.message.reply_text('Ваши камни: {}\nВаше золото: {}'.format(count, gold))
            elif context.chat_data['material'] == 'iron':
                update.message.reply_text('Ваши железо: {}\nВаше золото: {}'.format(count, gold))
            return SUCCESSFUL_BUYING
    except ValueError:
        update.message.reply_text('Похоже, то что вы ввели, не выглядит как натуральное число.',
                                  reply_markup=markup_fail)
        return CHANGE_OR_GO_TO_MENU_MARKET


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
            total_count_of_resources = cur.execute(
                'SELECT {} FROM resources WHERE tg_id = {}'.format(i[0], update.message.from_user.id)).fetchone()[0]
            if i[1] * count_of_buildings > total_count_of_resources:
                update.message.reply_text('К сожалению, у вас недостаточно ресурсов!', reply_markup=markup_fail)
                return CHANGE_OR_GO_TO_MENU_BUILDINGS
            spisok.append([i[0], i[1] * count_of_buildings])
        else:
            update.message.reply_text('Вы успешно построили предприятия!', reply_markup=markup_success)
            tranzaction_build(spisok[0][0], spisok[0][1], spisok[1][0], spisok[1][1], spisok[2][0], spisok[2][1],
                              context.chat_data['to_build'], count_of_buildings, update.message.from_user.id)
            buildings = cur.execute('SELECT {} FROM buildings WHERE tg_id = {}'
                                    .format(context.chat_data['to_build'], update.message.from_user.id)).fetchone()[0]
            if context.chat_data['to_build'] == 'farms':
                update.message.reply_text('Ваши фермы: {}'.format(buildings))
            elif context.chat_data['to_build'] == 'quarries':
                update.message.reply_text('Ваши каменоломни: {}'.format(buildings))
            elif context.chat_data['to_build'] == 'sawmills':
                update.message.reply_text('Ваши лесопилки: {}'.format(buildings))
            elif context.chat_data['to_build'] == 'iron_mines':
                update.message.reply_text('Ваши железные шахты: {}'.format(buildings))
            elif context.chat_data['to_build'] == 'gold_mines':
                update.message.reply_text('Ваши золотые рудники: {}'.format(buildings))
            return SUCCESSFUL_BUILD
    except ValueError:
        update.message.reply_text('Похоже, то что вы ввели, не выглядит как натуральное число.',
                                  reply_markup=markup_fail)
        return CHANGE_OR_GO_TO_MENU_BUILDINGS


def check_remelt(update: Update, context: CallbackContext):
    ore = cur.execute('SELECT {} FROM resources WHERE tg_id = {}'.format(context.chat_data['to_remelt'],
                                                                         update.message.from_user.id)).fetchone()[0]
    markup_fail = ReplyKeyboardMarkup([['Попробовать еще раз'], ['Вернуться в меню']], one_time_keyboard=False,
                                      resize_keyboard=True)
    markup_success = ReplyKeyboardMarkup([['Продолжить переплавку'], ['Вернуться в меню']], one_time_keyboard=False,
                                         resize_keyboard=True)
    try:
        count = int(update.message.text)
        if count > ore:
            update.message.reply_text('К сожалению, у вас недостаточно руды!', reply_markup=markup_fail)
            return CHANGE_OR_GO_TO_MENU_REMELTING
        elif count <= 0:
            raise ValueError
        else:
            update.message.reply_text('Переплавка прошла упешно!', reply_markup=markup_success)
            tranzaction_remelt(context.chat_data['to_remelt'], count, update.message.from_user.id)
            ore = cur.execute('SELECT {} FROM resources WHERE tg_id = {}'.format(context.chat_data['to_remelt'],
                                                                                 update.message.from_user.id)).fetchone()[
                0]
            if context.chat_data['to_remelt'] == 'iron_ore':
                iron = cur.execute(
                    'SELECT iron FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
                update.message.reply_text('Ваше железо: {}\nВаша железная руда: {}'.format(iron, ore))
            elif context.chat_data['to_remelt'] == 'gold_ore':
                gold = cur.execute(
                    'SELECT gold FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
                update.message.reply_text('Ваше золото: {}\nВаша золотая руда: {}'.format(gold, ore))
            return SUCCESSFUL_REMELTING
    except ValueError:
        update.message.reply_text('Похоже, то что вы ввели, не выглядит как натуральное число.',
                                  reply_markup=markup_fail)
        return CHANGE_OR_GO_TO_MENU_REMELTING


def build_farms(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной фермы составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_BUILDINGS['farms']]))
    context.chat_data['to_build'] = 'farms'
    return WAITING_FOR_COUNT_TO_BUILD


def build_quarries(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной каменоломни составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_BUILDINGS['quarries']]))
    context.chat_data['to_build'] = 'quarries'
    return WAITING_FOR_COUNT_TO_BUILD


def build_sawmills(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной лесопилки составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_BUILDINGS['sawmills']]))
    context.chat_data['to_build'] = 'sawmills'
    return WAITING_FOR_COUNT_TO_BUILD


def build_iron_mines(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной железной шахты составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_BUILDINGS['iron_mines']]))
    context.chat_data['to_build'] = 'iron_mines'
    return WAITING_FOR_COUNT_TO_BUILD


def build_gold_mines(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одного золотого рудника составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_BUILDINGS['gold_mines']]))
    context.chat_data['to_build'] = 'gold_mines'
    return WAITING_FOR_COUNT_TO_BUILD


def tranzaction_buy(type_of_material, summ, user):
    cur.execute('UPDATE resources SET gold = (SELECT gold FROM resources WHERE tg_id = {0}) - {1} '
                'WHERE tg_id = {0}'.format(user, summ))
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM resources WHERE tg_id = {1}) + 5 * {2} '
                'WHERE tg_id = {1}'.format(type_of_material, user, summ))
    con.commit()


def tranzaction_build(type_1, count_1, type_2, count_2, type_3, count_3, building, count_of_buildings, user):
    cur.execute('UPDATE resources SET {0} = (SELECT {1} FROM resources WHERE tg_id = {2}) - {3} '
                'WHERE tg_id = {2}'.format(type_1, type_1, user, count_1))
    cur.execute('UPDATE resources SET {0} = (SELECT {1} FROM resources WHERE tg_id = {2}) - {3} '
                'WHERE tg_id = {2}'.format(type_2, type_2, user, count_2))
    cur.execute('UPDATE resources SET {0} = (SELECT {1} FROM resources WHERE tg_id = {2}) - {3} '
                'WHERE tg_id = {2}'.format(type_3, type_3, user, count_3))
    cur.execute('UPDATE buildings SET {0} = (SELECT {0} FROM buildings WHERE tg_id = {1}) + {2} '
                'WHERE tg_id = {1}'.format(building, user, count_of_buildings))
    con.commit()


def tranzaction_remelt(type_of_metal, count, user):
    if type_of_metal == 'iron_ore':
        cur.execute('UPDATE resources SET iron = (SELECT iron FROM resources WHERE tg_id = {0}) + ({1} / 5)'
                    'WHERE tg_id = {0}'.format(user, count))
        cur.execute('UPDATE resources SET iron_ore = (SELECT iron_ore FROM resources WHERE tg_id = {0}) - ({1})'
                    'WHERE tg_id = {0}'.format(user, count))
    elif type_of_metal == 'gold_ore':
        cur.execute('UPDATE resources SET gold = (SELECT gold FROM resources WHERE tg_id = {0}) + ({1} / 10)'
                    'WHERE tg_id = {0}'.format(user, count))
        cur.execute('UPDATE resources SET gold_ore = (SELECT gold_ore FROM resources WHERE tg_id = {0}) - ({1})'
                    'WHERE tg_id = {0}'.format(user, count))
    con.commit()


def remelt_iron(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Введите количество железной руды, которое вы хотите переплавить. '
        'За 5 единиц железной руды вы получите 1 единицу железа')
    context.chat_data['to_remelt'] = 'iron_ore'
    return WAITING_FOR_COUNT_OF_METAL


def remelt_gold(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Введите количество золотой руды, которое вы хотите переплавить. '
        'За 10 единиц золотой руды вы получите 1 единицу золота')
    context.chat_data['to_remelt'] = 'gold_ore'
    return WAITING_FOR_COUNT_OF_METAL


@log
def foreign_policy(update: Update, context: CallbackContext):
    foreign_policy_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text(
        "Внешняя политика", reply_markup=foreign_policy_markup)
    return FOREIGN_POLICY
