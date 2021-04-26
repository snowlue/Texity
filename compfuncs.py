import random
import sqlite3

from telegram.ext import CallbackContext

con = sqlite3.connect("players.db", check_same_thread=False)
cur = con.cursor()


def upgrade_city_level(count, id):
    level_before = int(cur.execute('SELECT city_level FROM cities WHERE tg_id = {0}'.format(id, count)).fetchone()[0])
    cur.execute('UPDATE cities SET city_level = (SELECT city_level '
                'FROM cities WHERE tg_id = {0}) + {1} WHERE tg_id = {0}'.format(id, count))
    level_now = int(cur.execute('SELECT city_level FROM cities WHERE tg_id = {0}'.format(id, count)).fetchone()[0])
    if level_now > level_before:
        cur.execute('UPDATE cities SET next_level = {} + 1 WHERE tg_id = {}'.format(level_now, id))

    con.commit()


def transaction_hiring(type, count, res_1, count_1, res_2, count_2, res_3, count_3, user):
    cur.execute('UPDATE army SET {0} = (SELECT {0} FROM army '
                'WHERE tg_id = {2}) + {1} WHERE tg_id = {2}'.format(type, count, user))
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM '
                'resources WHERE tg_id = {2}) - {1} WHERE tg_id = {2}'.format(res_1, count_1, user))
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM '
                'resources WHERE tg_id = {2}) - {1} WHERE tg_id = {2}'.format(res_2, count_2, user))
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM '
                'resources WHERE tg_id = {2}) - {1} WHERE tg_id = {2}'.format(res_3, count_3, user))
    if type != 'sieges':
        cur.execute('UPDATE resources SET population = (SELECT population '
                    'FROM resources WHERE tg_id = {1}) - {0} WHERE tg_id = {1}'.format(count, user))
    con.commit()


def transaction_buy(type_of_material, summ, user):
    cur.execute('UPDATE resources SET gold = (SELECT gold FROM resources WHERE tg_id = {0}) - {1} '
                'WHERE tg_id = {0}'.format(user, summ))
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM resources WHERE tg_id = {1}) + 5 * {2} '
                'WHERE tg_id = {1}'.format(type_of_material, user, summ))
    con.commit()


def transaction_build(type_1, count_1, type_2, count_2, type_3, count_3, building, count_of_buildings, user):
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM resources WHERE tg_id = {1}) - {2} '
                'WHERE tg_id = {1}'.format(type_1, user, count_1))
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM resources WHERE tg_id = {1}) - {2} '
                'WHERE tg_id = {1}'.format(type_2, user, count_2))
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM resources WHERE tg_id = {1}) - {2} '
                'WHERE tg_id = {1}'.format(type_3, user, count_3))
    cur.execute('UPDATE buildings SET {0} = (SELECT {0} FROM buildings WHERE tg_id = {1}) + {2} '
                'WHERE tg_id = {1}'.format(building, user, count_of_buildings))
    con.commit()


def transaction_remelt(type_of_metal, count, user):
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


def increment_resources(type_res, amount, user):
    storages = cur.execute('SELECT {} FROM buildings '
                           'WHERE tg_id = {}'.format('{}_storages'.format(type_res), user)).fetchone()[0]
    resources_before = cur.execute('SELECT {} FROM resources WHERE tg_id = {}'.format(type_res, user)).fetchone()[0]
    max_count = storages * 1000
    if resources_before + amount >= max_count:
        cur.execute('UPDATE resources SET {0} = {2} WHERE tg_id = {1}'.format(type_res, user, max_count))
        con.commit()
        return max_count - resources_before if resources_before < max_count else 0
    cur.execute('UPDATE resources SET {0} = (SELECT {0} FROM '
                'resources WHERE tg_id = {1}) + {2} WHERE tg_id = {1}'.format(type_res, user, amount))
    con.commit()
    return -1


def calculate_random_shift(number, shift):
    try:
        return round(number + number * random.choice([i / 1000 for i in range(-int(shift*10), int(shift*10), 1)]))
    except IndexError:
        return number


def get_opposite_city(tg_id: int, context: CallbackContext, times):
    war_level = cur.execute('SELECT foreign_policy FROM cities WHERE tg_id = {}'.format(tg_id)).fetchone()[0]
    if 'opposite.name' not in context.chat_data:
        opposite_city = list(cur.execute('SELECT * FROM npc_cities WHERE id = {}'.format(war_level)).fetchone())

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
        context.chat_data['opposite.iron_ore'] = round(one_resourse +
                                                       one_resourse *
                                                       random.choice([i / 100 for i in range(-25, 10, 1)]))
        opposite_city[2] -= context.chat_data['opposite.iron_ore']
        context.chat_data['opposite.gold_ore'] = round(one_resourse +
                                                       one_resourse *
                                                       random.choice([i / 100 for i in range(-25, 10, 1)]))
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
    context.chat_data['opposite.fake_iron_ore'] = calculate_random_shift(context.chat_data['opposite.iron_ore'],
                                                                         P_r - 0.5 * war_level)
    context.chat_data['opposite.fake_gold_ore'] = calculate_random_shift(context.chat_data['opposite.gold_ore'],
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
