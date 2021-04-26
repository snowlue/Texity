import random
import sqlite3

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext

from logger import log

img_market = open("market.jpg", 'rb')

con = sqlite3.connect("players.db", check_same_thread=False)
cur = con.cursor()
list_of_players = [i[0] for i in cur.execute('SELECT tg_id FROM cities').fetchall()]

(WAITING_FOR_CITY_NAME, MENU, RESOURCES, MARKET, POPULATION, CONSTRUCTION, FOREIGN_POLICY, INFO,
 WAITING_FOR_SUM_TO_BUY, CHANGE_OR_GO_TO_MENU_MARKET, NOT_ENOUGH_GOLD, BAD_SUMM, SUCCESSFUL_BUYING,
 WAITING_FOR_COUNT_TO_BUILD, SUCCESSFUL_BUILD, CHANGE_OR_GO_TO_MENU_BUILDINGS, WAITING_FOR_TYPE_OF_METAL,
 WAITING_FOR_COUNT_OF_METAL, SUCCESSFUL_REMELTING, CHANGE_OR_GO_TO_MENU_REMELTING) = range(20)

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
    farms = cur.execute('SELECT farms FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    quarries = cur.execute('SELECT quarries FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    sawmills = cur.execute('SELECT sawmills FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    iron_mines = cur.execute('SELECT iron_mines FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    gold_mines = cur.execute('SELECT gold_mines FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    city_name = cur.execute('SELECT city FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    x = float(cur.execute('SELECT city_level FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0])
    y = float(cur.execute('SELECT next_level FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0])
    city_level = '{}/{}'.format(int(x * 100), int(y * 100))
    population_support = \
    cur.execute('SELECT population_support FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    update.message.reply_text('Город "{}"\n'
                              'Уровень города: {}\n'
                              'Поддержка от населения: {}%'.format(city_name, '{} ({})'.format(int(x), city_level),
                                                                   int(population_support * 100)))
    update.message.reply_text('Ваши предприятия\n'
                              '🧑🏻‍🌾 Фермы: {}\n'
                              '🪨 Каменоломни: {}\n'
                              '🪵 Лесопилки: {}\n'
                              '🏭 Шахты: {}\n'
                              '💰 Золотые рудники: {}'.format(
        farms, quarries, sawmills, iron_mines, gold_mines), reply_markup=resources_markup)
    return INFO


@log
def resources(update: Update, context: CallbackContext):
    resources_markup = ReplyKeyboardMarkup([['Собрать ресурсы'],
                                            ['Переплавить руду'],
                                            ['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    user_id = update.message.from_user.id
    stone = cur.execute('SELECT stone FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    wood = cur.execute('SELECT wood FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    food = cur.execute('SELECT food FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    iron = cur.execute('SELECT iron FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    gold = cur.execute('SELECT gold FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    gold_ore = cur.execute('SELECT gold_ore FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    iron_ore = cur.execute('SELECT iron_ore FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    update.message.reply_text('Ваши ресурсы\n'
                              '🥩 Еда: {}\n🪨 Камни: {}\n'
                              '🪵 Дерево: {}\n🥈 Железо: {}\n'
                              '💰 Золото: {}\n🏭 Золотая руда: {}\n'
                              '🏭 Железная руда: {}'.format(food, stone, wood, iron, gold, gold_ore, iron_ore),
                              reply_markup=resources_markup)
    return RESOURCES


@log
def market(update: Update, context: CallbackContext):
    market_markup = ReplyKeyboardMarkup([['Еда', 'Дерево'],
                                         ['Камни', 'Железо'],
                                         ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_photo(img_market, "Рынок", reply_markup=market_markup)
    img_market.seek(0)
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
                                               ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        "Какие производства желаете построить?", reply_markup=construction_markup)
    return CONSTRUCTION


@log
def remelting(update: Update, context: CallbackContext):
    remelting_markup = ReplyKeyboardMarkup([['Железная руда', 'Золотая руда'],
                                            ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Какой тип руды хотите переплавить?', reply_markup=remelting_markup)
    return WAITING_FOR_TYPE_OF_METAL


@log
def cultivating(update: Update, context: CallbackContext):
    farms = cur.execute('SELECT farms FROM buildings WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
    quarries = cur.execute('SELECT quarries FROM buildings WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
    sawmills = cur.execute('SELECT sawmills FROM buildings WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
    iron_mines = cur.execute('SELECT iron_mines FROM buildings WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
    gold_mines = cur.execute('SELECT gold_mines FROM buildings WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
    resources_markup = ReplyKeyboardMarkup([['Собрать ресурсы'],
                                            ['Переплавить руду'],
                                            ['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    user_id = update.message.from_user.id

    last_cultivating = cur.execute('SELECT julianday(time)'
                                   'FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    timenow = cur.execute('SELECT julianday("now","localtime")').fetchone()[0]
    increment = timenow - last_cultivating
    if increment <= 1 / 144:
        update.message.reply_text('Ресурсы можно собирать не чаще, чем раз в 10 минут ¯\_(ツ)_/¯ \n'
                                  'Осталось: {} минут.'.format(round(10 - increment * 1440)))
        return RESOURCES
    inc_stone, inc_wood, inc_food, inc_gold_ore, inc_iron_ore = [round(increment * 240)] * 5
    delta = increment_resourses('stone', inc_stone * quarries, user_id)
    message = 'Заполнены следующие хранилища: '
    if delta != -1:
        inc_stone = delta
        message += 'хранилища камня, '
    delta = increment_resourses('wood', inc_wood * sawmills, user_id)
    if delta != -1:
        inc_wood = delta
        message += 'хранилища дерева, '
    delta = increment_resourses('food', inc_food * farms, user_id)
    if delta != -1:
        inc_food = delta
        message += 'хранилища еды, '
    delta = increment_resourses('gold_ore', inc_gold_ore * gold_mines, user_id)
    if delta != -1:
        inc_gold_ore = delta
        message += 'хранилища золотой руды, '
    delta = increment_resourses('iron_ore', inc_iron_ore * iron_mines, user_id)
    if delta != -1:
        inc_iron_ore = delta
        message += 'хранилища железной руды, '

    update.message.reply_text('Вы собрали: \n'
                              '🥩 Еды: {}\n🪨 Камня: {}\n'
                              '🪵 Дерева: {}\n🏭 Золотой руды: {}\n'
                              '🏭 Железной руды: {}'.format(inc_food, inc_stone, inc_wood, inc_gold_ore, inc_iron_ore),
                              reply_markup=resources_markup)
    if message != 'Заполнены следующие хранилища: ':
        update.message.reply_text('{}\nВам нужно построить больше хранилищ соответствующего типа.'.format(message[:-2]), reply_markup=resources_markup)

    cur.execute('UPDATE resources SET time = datetime({}) WHERE tg_id = {}'.format(timenow, user_id))
    con.commit()

    return RESOURCES


@log
def buy_food(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц еды')
    context.chat_data['material'] = 'food'
    return WAITING_FOR_SUM_TO_BUY


@log
def buy_wood(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц дерева')
    context.chat_data['material'] = 'wood'
    return WAITING_FOR_SUM_TO_BUY


@log
def buy_stone(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц камня')
    context.chat_data['material'] = 'stone'
    return WAITING_FOR_SUM_TO_BUY


@log
def buy_iron(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц железа')
    context.chat_data['material'] = 'iron'
    return WAITING_FOR_SUM_TO_BUY


@log
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
            d = {'food': 'Ваша еда', 'wood': 'Ваше дерево', 'stone': 'Ваши камни', 'iron': 'Ваше железо'}
            before = cur.execute('SELECT {} FROM resources WHERE tg_id = {}'.format(context.chat_data['material'], update.message.from_user.id)).fetchone()[0]
            add_resources = summ * 5
            max_resources = 1000 * cur.execute('SELECT {} FROM buildings WHERE tg_id = {}'.format('{}_storages'.format(context.chat_data['material']), update.message.from_user.id)).fetchone()[0]
            if max_resources >= before + add_resources:
                update.message.reply_text('Покупка прошла упешно!', reply_markup=markup_success)
                tranzaction_buy(context.chat_data['material'], summ, update.message.from_user.id)
                count = cur.execute('SELECT {} FROM resources WHERE tg_id = {}'
                                    .format(context.chat_data['material'], update.message.from_user.id)).fetchone()[0]
                gold = cur.execute('SELECT gold FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
                update.message.reply_text('{}: {}\nВаше золото: {}'.format(d[context.chat_data['material']], count, gold))
                return SUCCESSFUL_BUYING
            else:
                update.message.reply_text('В ваших хранилищах недостаточно места для такого количества ресурсов!', reply_markup=markup_fail)
                return CHANGE_OR_GO_TO_MENU_MARKET
    except ValueError:
        update.message.reply_text('Похоже, то что вы ввели, не выглядит как натуральное число.',
                                  reply_markup=markup_fail)
        return CHANGE_OR_GO_TO_MENU_MARKET


def upgrade_city_level(count, id):
    level_before = int(cur.execute('SELECT city_level FROM cities WHERE tg_id = {0}'.format(id, count)).fetchone()[0])
    cur.execute('UPDATE cities SET city_level = (SELECT city_level FROM cities WHERE tg_id = {0}) + {1} WHERE tg_id = {0} '
                'WHERE tg_id = {0}'.format(id, count))
    level_now = int(cur.execute('SELECT city_level FROM cities WHERE tg_id = {0}'.format(id, count)).fetchone()[0])
    if level_now > level_before:
        cur.execute('UPDATE cities SET next_level = {} + 1 WHERE tg_id = {}'.format(level_now, id))

    con.commit()


@log
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
            upgrade_city_level(0.02 * count_of_buildings, update.message.from_user.id)
            return SUCCESSFUL_BUILD
    except ValueError:
        update.message.reply_text('Похоже, то что вы ввели, не выглядит как натуральное число.',
                                  reply_markup=markup_fail)
        return CHANGE_OR_GO_TO_MENU_BUILDINGS


@log
def check_remelt(update: Update, context: CallbackContext):
    ore = cur.execute('SELECT {} FROM resources WHERE tg_id = {}'.format(context.chat_data['to_remelt'],
                                                                         update.message.from_user.id)).fetchone()[0]
    markup_fail = ReplyKeyboardMarkup([['Попробовать еще раз'], ['Вернуться в меню']], one_time_keyboard=False,
                                      resize_keyboard=True)
    markup_success = ReplyKeyboardMarkup([['Продолжить переплавку'], ['Вернуться в меню']], one_time_keyboard=False,
                                         resize_keyboard=True)
    try:
        d = {'iron_ore': 'iron', 'gold_ore': 'gold'}
        count = int(update.message.text)
        metal = cur.execute(
                    'SELECT {} FROM resources WHERE tg_id = {}'.format(d[context.chat_data['to_remelt']], update.message.from_user.id)).fetchone()[0]
        remelted_metal = count // 5 if context.chat_data['to_remelt'] == 'iron_ore' else count // 10
        max_metal = 1000 * cur.execute(
                    'SELECT {}_storages FROM buildings WHERE tg_id = {}'.format(d[context.chat_data['to_remelt']], update.message.from_user.id)).fetchone()[0]
        if max_metal < metal + remelted_metal:
            update.message.reply_text('К сожалению, в ваших хранилищах недостаточно места для такого количества переплавленного металла', reply_markup=markup_fail)
            return CHANGE_OR_GO_TO_MENU_REMELTING
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


@log
def build_farms(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной фермы составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_BUILDINGS['farms']]))
    context.chat_data['to_build'] = 'farms'
    return WAITING_FOR_COUNT_TO_BUILD


@log
def build_quarries(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной каменоломни составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_BUILDINGS['quarries']]))
    context.chat_data['to_build'] = 'quarries'
    return WAITING_FOR_COUNT_TO_BUILD


@log
def build_sawmills(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной лесопилки составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_BUILDINGS['sawmills']]))
    context.chat_data['to_build'] = 'sawmills'
    return WAITING_FOR_COUNT_TO_BUILD


@log
def build_iron_mines(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной железной шахты составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_BUILDINGS['iron_mines']]))
    context.chat_data['to_build'] = 'iron_mines'
    return WAITING_FOR_COUNT_TO_BUILD


@log
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


def increment_resourses(type_res, amount, user):
    storages = cur.execute('SELECT {} FROM buildings WHERE tg_id = {}'.format('{}_storages'.format(type_res), user)).fetchone()[0]
    resources_before = cur.execute('SELECT {} FROM resources WHERE tg_id = {}'.format(type_res, user)).fetchone()[0]
    max_count = storages * 1000
    if resources_before + amount >= max_count:
        cur.execute('UPDATE resources SET {0} = {2} WHERE tg_id = {1}'.format(type_res, user, max_count))
        con.commit()
        return max_count - resources_before if resources_before < max_count else 0
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM resources WHERE tg_id = {1}) + {2} '
                'WHERE tg_id = {1}'.format(type_res, user, amount))
    con.commit()
    return -1


def tranzaction_build(type_1, count_1, type_2, count_2, type_3, count_3, building, count_of_buildings, user):
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM resources WHERE tg_id = {1}) - {2} '
                'WHERE tg_id = {1}'.format(type_1, user, count_1))
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM resources WHERE tg_id = {1}) - {2} '
                'WHERE tg_id = {1}'.format(type_2, user, count_2))
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM resources WHERE tg_id = {1}) - {2} '
                'WHERE tg_id = {1}'.format(type_3, user, count_3))
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


@log
def remelt_iron(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Введите количество железной руды, которое вы хотите переплавить. '
        'За 5 единиц железной руды вы получите 1 единицу железа')
    context.chat_data['to_remelt'] = 'iron_ore'
    return WAITING_FOR_COUNT_OF_METAL


@log
def remelt_gold(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Введите количество золотой руды, которое вы хотите переплавить. '
        'За 10 единиц золотой руды вы получите 1 единицу золота')
    context.chat_data['to_remelt'] = 'gold_ore'
    return WAITING_FOR_COUNT_OF_METAL


@log
def foreign_policy(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    war_level, in_spying = cur.execute('SELECT foreign_policy, in_spying FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()
    infantry, cavalry, sieges = cur.execute('SELECT * FROM army WHERE tg_id = {}'.format(user_id)).fetchone()[1:]
    
    if in_spying == -1:
        foreign_policy_markup = ReplyKeyboardMarkup([
            ['В атаку! ⚔️'],
            ['Информация о противнике ℹ️'],
            ['Вернуться в меню']
        ], one_time_keyboard=False, resize_keyboard=True)
    elif in_spying != 0:
        foreign_policy_markup = ReplyKeyboardMarkup([
            ['На разведку! 🥷🏻', 'В атаку! ⚔️'],
            ['Информация о противнике ℹ️'],
            ['Вернуться в меню']
        ], one_time_keyboard=False, resize_keyboard=True)
    else:
        foreign_policy_markup = ReplyKeyboardMarkup([
            ['Расчистить путь к городу 🧭'],
            ['Вернуться в меню']
        ], one_time_keyboard=False, resize_keyboard=True)
    
    update.message.reply_text('Уровень военного дела: {} 🪖\n'
                              'Ваши войска:\n'
                              '⠀⠀🏹 Пехота — {}\n'
                              '⠀⠀🐎 Конница — {}\n'
                              '⠀⠀🦬 Осадные машины — {}'.format(war_level, infantry, 
                                                                cavalry, sieges),
                              reply_markup=foreign_policy_markup)
    return FOREIGN_POLICY


def calculate_random_shift(number, shift):
    try:
        return round(number + number * random.choice([i / 1000 for i in range(-shift*10, shift*10, 1)]))
    except IndexError:
        return number


def get_opposite_city(tg_id: int, context: CallbackContext, times):
    war_level = cur.execute('SELECT foreign_policy FROM cities WHERE tg_id = {}'.format(tg_id)).fetchone()[0]
    if 'opposite.name' not in context.chat_data:
        opposite_city = cur.execute('SELECT * FROM npc_cities WHERE id = {}'.format(war_level)).fetchone()
        
        context.chat_data['opposite.name'] = opposite_city[1]
        one_resourse = opposite_city[2] // 5
        context.chat_data['opposite.stone'] = round(one_resourse +
                                                    one_resourse *
                                                    random.choice([i / 100 for i in range(-12, 26, 1)]))
        opposite_city[2] -= context.chat_data['opposite.stone']
        context.chat_data['opposite.wood'] = round(one_resourse +
                                                   one_resourse *
                                                   random.choice([i / 100 for i in range(-12, 26, 1)]))
        opposite_city[2] -= context.chat_data['opposite.wood']
        context.chat_data['opposite.iron_ode'] = round(one_resourse +
                                                       one_resourse *
                                                       random.choice([i / 100 for i in range(-25, 16, 1)]))
        opposite_city[2] -= context.chat_data['opposite.iron_ode']
        context.chat_data['opposite.gold_ore'] = round(one_resourse +
                                                       one_resourse *
                                                       random.choice([i / 100 for i in range(-25, 16, 1)]))
        opposite_city[2] -= context.chat_data['opposite.gold_ore']
        context.chat_data['opposite.food'] = opposite_city[2]
        context.chat_data['opposite.gold'] = opposite_city[3]
        context.chat_data['opposite.infantry'] = opposite_city[4]
        context.chat_data['opposite.cavalry'] = opposite_city[5]
        context.chat_data['opposite.requiered_sieges'] = opposite_city[6]
        context.chat_data['opposite.farms'] = opposite_city[8]
        context.chat_data['opposite.quarries'] = opposite_city[9]
        context.chat_data['opposite.sawmills'] = opposite_city[10]
        context.chat_data['opposite.population'] = opposite_city[11]

    if times == 0:
        P_r, P_w = 20, 33
    elif times == 1:
        P_r, P_w = 15, 20
    elif times == 2:
        P_r, P_w = 10, 10
    elif times == 3:
        P_r, P_w = 0, 0
        
    context.chat_data['opposite.fake_stone'] = calculate_random_shift(context.chat_data['opposite.stone'],
                                                                      P_r - 0.5 * war_level)
    context.chat_data['opposite.fake_wood'] = calculate_random_shift(context.chat_data['opposite.wood'],
                                                                     P_r - 0.5 * war_level)
    context.chat_data['opposite.fake_iron_ode'] = calculate_random_shift(context.chat_data['opposite.iron_ode'],
                                                                         P_r - 0.5 * war_level)
    context.chat_data['opposite.fake_gold_ore'] = calculate_random_shift(context.chat_data['opposite.gold_ode'],
                                                                         P_r - 0.5 * war_level)
    context.chat_data['opposite.fake_food'] = calculate_random_shift(context.chat_data['opposite.food'],
                                                                     P_r - 0.5 * war_level)
    context.chat_data['opposite.fake_infantry'] = calculate_random_shift(context.chat_data['opposite.infantry'],
                                                                         P_w - 0.5 * war_level)
    context.chat_data['opposite.fake_cavalry'] = calculate_random_shift(context.chat_data['opposite.cavalry'],
                                                                        P_w - 0.5 * war_level)
    context.chat_data['opposite.fake_requiered_sieges'] = calculate_random_shift(context.chat_data['opposite.requiered_sieges'],
                                                                                 P_w - 0.5 * war_level)
    context.chat_data['opposite.fake_population'] = calculate_random_shift(context.chat_data['opposite.population'],
                                                                           P_w - 0.5 * war_level)

@log
def path_to_city(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    war_level = cur.execute('SELECT foreign_policy FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    opposite_city = cur.execute('SELECT * FROM npc_cities WHERE id = {}'.format(war_level)).fetchone()
    
    chance = random.random() + war_level * 0.05
    
    if chance <= 0.1:
        cur.execute('UPDATE cities SET in_spying = -1 WHERE tg_id = {}'.format(user_id))
        legend = 'Каналья! Нас засекли... Придётся сразу идти в бой, у нас нет выхода.\n\n'
        war_markup = ReplyKeyboardMarkup([
            ['В атаку! ⚔️'],
            ['Вернуться в меню']
        ], one_time_keyboard=False, resize_keyboard=True)
    else:
        cur.execute('UPDATE cities SET in_spying = 1 WHERE tg_id = {}'.format(user_id))
        legend = 'Отлично! Мы смогли незаметно для противника расчистить место для разведки!\n\n'
        war_markup = ReplyKeyboardMarkup([
            ['На разведку! 🥷🏻', 'В атаку! ⚔️'],
            ['Вернуться в меню']
        ], one_time_keyboard=False, resize_keyboard=True)
    con.commit()
    
    phrase = random.choice(['Ходят слухи, что это', 'Поговаривают, что это', 
                            'Говорят, что это', 'По всему миру это место известно как',
                            'Везде ходят слухи, что это', 'Всем кажется, что это',
                            'Везде известно, что это', 'По всему миру ходят слухи, что это',
                            'Все знают, что это', 'Всем это место известно как']) + opposite_city[7] + '...\n\n'

    get_opposite_city(user_id, context, 0)
    
    update.message.reply_text(
        legend + phrase + 'Вот что мы смогли разведать во время расчистки пути.\n'
        '🏰 Название: {}\n'
        '💰 Из последних публичных отчётов о бюджете нам известно, что в городе {} золота.\n\n'
        'Мы посчитали стражу вокруг, но могли ошибиться. В городе:\n'
        '⠀⠀- {} жителей 👥\n'
        '⠀⠀- {} пехоты 🏹\n'
        '⠀⠀- {} кавалерии 🐎\n'
        '⠀⠀Скорее всего нам понадобится {} осадных машин, чтобы пробить стены 🦬\n\n'
        'Очень неточные данные по ресурсам в хранилищах:\n'
        '⠀⠀- {} единиц камня 🪨\n'
        '⠀⠀- {} единиц дерева 🪵\n'
        '⠀⠀- {} единиц еды 🥩\n'
        '⠀⠀- {} единиц железной руды 🏭\n'
        '⠀⠀- {} единиц золотой руды 🏭\n\n'
        'За стенами мы разглядели производства города. В городе точно стоит:\n'
        '⠀⠀- {} ферм 🧑🏻‍🌾\n'
        '⠀⠀- {} каменоломен 🪨\n'
        '⠀⠀- {} лесопилок 🪵\n\n'
        'Мы можем поити в разведку, чтобы узнать более точную информацию.'.format(
            context.chat_data['opposite.name'], context.chat_data['opposite.gold'],
            context.chat_data['opposite.fake_population'], context.chat_data['opposite.fake_infantry'],
            context.chat_data['opposite.fake_cavalry'], context.chat_data['opposite.fake_requiered_sieges'],
            context.chat_data['opposite.fake_stone'], context.chat_data['opposite.fake_wood'],
            context.chat_data['opposite.fake_food'], context.chat_data['opposite.fake_iron_ode'],
            context.chat_data['opposite.fake_gold_ore'], context.chat_data['opposite.farms'],
            context.chat_data['opposite.quarries'], context.chat_data['opposite.sawmills']
        ), reply_markup=war_markup
    )

    return FOREIGN_POLICY


@log
def scouting(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    war_level = cur.execute('SELECT foreign_policy FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    in_spying = cur.execute('SELECT in_spying FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    chance = random.random() + war_level * 0.05
    
    if in_spying == 1:
        max_chance = 0.63
    elif in_spying == 2:
        max_chance = 0.76
    elif in_spying == 3:
        max_chance = 0.9
    
    if chance <= max_chance:
        cur.execute('UPDATE cities SET in_spying = -1 WHERE tg_id = {}'.format(user_id))
        war_markup = ReplyKeyboardMarkup([
            ['В атаку! ⚔️'],
            ['Информация о противнике ℹ️'],
            ['Вернуться в меню']
        ], one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text('! Нас засекли... Придётся идти в бой, у нас нет выхода.',
                                  reply_markup=war_markup)
        con.commit()
        return FOREIGN_POLICY
    else:
        legend = 'Отлично! Мы смогли разведать ещё больше полезной информации!\n\n'
        
        if in_spying == 3:
            cur.execute('UPDATE cities SET in_spying = -1 WHERE tg_id = {}'.format(user_id))
            war_markup = ReplyKeyboardMarkup([
                ['В атаку! ⚔️'],
                ['Вернуться в меню']
            ], one_time_keyboard=False, resize_keyboard=True)
        else:
            cur.execute('UPDATE cities SET in_spying = {} WHERE tg_id = {}'.format(in_spying + 1, user_id))
            war_markup = ReplyKeyboardMarkup([
                ['На разведку! 🥷🏻', 'В атаку! ⚔️'],
                ['Вернуться в меню']
            ], one_time_keyboard=False, resize_keyboard=True)     
        con.commit()
    
    get_opposite_city(user_id, context, in_spying)
    
    update.message.reply_text(
        legend + 'Мы вернулись с разведки с новой информацией.\n'
        'Внутри города мы пересчитали жителей, всё ещё могут быть ошибки. В городе:\n' if in_spying != 3 else 'Внутри города мы пересчитали жителей, в этот раз без ошибок. В городе:\n'
        '⠀⠀- {} жителей 👥\n'
        '⠀⠀- {} пехоты 🏹\n'
        '⠀⠀- {} кавалерии 🐎\n'
        '⠀⠀Скорее всего нам понадобится {} осадных машин, чтобы пробить стены 🦬\n\n' if in_spying != 3 else '⠀⠀Нам точно понадобится {} осадных машин, чтобы пробить стены 🦬\n\n'
        'Более точные данные по ресурсам в хранилищах:\n' if in_spying != 3 else 'Максимально точные данные по ресурсам в хранилищах:\n'
        '⠀⠀- {} единиц камня 🪨\n'
        '⠀⠀- {} единиц дерева 🪵\n'
        '⠀⠀- {} единиц еды 🥩\n'
        '⠀⠀- {} единиц железной руды 🏭\n'
        '⠀⠀- {} единиц золотой руды 🏭\n\n'
        'Мы можем продолжить разведку, чтобы узнать более точную информацию.' if in_spying != 3 else 'Вся информация на руках. Теперь мы готовы к бою!'
        ''.format(
            context.chat_data['opposite.name'], context.chat_data['opposite.gold'],
            context.chat_data['opposite.fake_population'], context.chat_data['opposite.fake_infantry'],
            context.chat_data['opposite.fake_cavalry'], context.chat_data['opposite.fake_requiered_sieges'],
            context.chat_data['opposite.fake_stone'], context.chat_data['opposite.fake_wood'],
            context.chat_data['opposite.fake_food'], context.chat_data['opposite.fake_iron_ode'],
            context.chat_data['opposite.fake_gold_ore'], context.chat_data['opposite.farms'],
            context.chat_data['opposite.quarries'], context.chat_data['opposite.sawmills']
        ), reply_markup=war_markup
    )
    
    return FOREIGN_POLICY
