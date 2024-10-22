import random
import sqlite3

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext

from compfuncs import (get_opposite_city, increment_resources,
                       transaction_build, transaction_buy, transaction_hiring,
                       transaction_remelt, upgrade_city_level)
from logger import log

img_market = open("market.jpg", 'rb')

con = sqlite3.connect("players.db", check_same_thread=False)
cur = con.cursor()
list_of_players = [i[0] for i in cur.execute('SELECT tg_id FROM cities').fetchall()]

(WAITING_FOR_CITY_NAME, MENU, RESOURCES, MARKET, POPULATION, CONSTRUCTION, FOREIGN_POLICY,
 WAITING_FOR_SUM_TO_BUY, CHANGE_OR_GO_TO_MENU_MARKET, NOT_ENOUGH_GOLD, BAD_SUMM, SUCCESSFUL_BUYING,
 WAITING_FOR_COUNT_TO_BUILD, SUCCESSFUL_BUILD, CHANGE_OR_GO_TO_MENU_BUILDINGS, WAITING_FOR_TYPE_OF_METAL,
 WAITING_FOR_COUNT_OF_METAL, SUCCESSFUL_REMELTING, CHANGE_OR_GO_TO_MENU_REMELTING, HIRE_ARMY, HIRING, 
 SUCCESSFUL_HIRING, CHANGE_OR_GO_TO_MENU_ARMY, HIRE_SPY, BACK_TO_MENU, PRODUCTIONS, WAITING_FOR_TYPE_OF_BUILDING, STORAGES, OTHERS) = range(29)

PRICE_OF_PRODUCTIONS = {
    'farms': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
    'sawmills': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
    'quarries': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
    'iron_mines': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
    'gold_mines': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]]
}
PRICE_OF_STORAGES = {'food': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
                     'wood': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
                     'stone': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
                     'iron': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
                     'gold': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
                     'iron_ore': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]],
                     'gold_ore': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]]}

PRICE_OF_OTHERS = {'houses': [['wood', 240], ['stone', 120], ['iron', 240], ['food', 200]]}
ARMY = {'infantry': [['iron', 40], ['gold', 20], ['food', 10]],
        'cavalry': [['iron', 100], ['gold', 50], ['food', 50]],
        'spy': [['iron', 100], ['gold', 300], ['food', 50]],
        'sieges': [['iron', 200], ['stone', 100], ['wood', 350]]}


@log
def get_info_about_city(update: Update, context: CallbackContext):
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
    population_support = cur.execute('SELECT population_support '
                                     'FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0]
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
        farms, quarries, sawmills, iron_mines, gold_mines), reply_markup=ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True))
    return BACK_TO_MENU


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
    population_markup = ReplyKeyboardMarkup([['Нанять армию'], ['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    population = cur.execute('SELECT population FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
    infantry = cur.execute('SELECT infantry FROM army WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
    cavalry = cur.execute('SELECT cavalry FROM army WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
    sieges = cur.execute('SELECT sieges FROM army WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
    update.message.reply_text("Ваше население {} человек\n----------\nВаша армия:\n Ваша пехота: {}\nВаша кавалерия: {}\n Ваши осадные машины: {}".format(population, infantry, cavalry, sieges), reply_markup=population_markup)
    return POPULATION


def hire_army(update: Update, context: CallbackContext):
    hire_army_markup = ReplyKeyboardMarkup([['Нанять пехоту'], ['Нанять кавалерию'], ['Нанять разведчиков'], ['Построить осадные машины'], ['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text('Каких войск вы хотите нанять?', reply_markup=hire_army_markup)
    update.message.reply_text('Помните, что армия набирается из населения. При увеличении числа военных уменьшается число населения.')
    return HIRE_ARMY


def hire_infantry(update: Update, context: CallbackContext):
    update.message.reply_text('На одного воина вы должны потратить 40 единиц железа, 20 единиц золота, а также 10 единиц еды')
    context.chat_data['to_hire'] = 'infantry'
    return HIRING


def hire_cavalry(update: Update, context: CallbackContext):
    update.message.reply_text('На одного кавалериста вы должны потратить 100 единиц железа, 50 единиц золота, а также 50 единиц еды')
    context.chat_data['to_hire'] = 'cavalry'
    return HIRING


def hire_spy(update: Update, context: CallbackContext):
    update.message.reply_text('На одного разведчика вы должны потратить 100 единиц железа, 300 единиц золота, а также 50 единиц еды')
    context.chat_data['to_hire'] = 'spy'
    return HIRING


def build_sieges(update: Update, context: CallbackContext):
    update.message.reply_text('На постройку одной осадной машины нужно 350 единиц дерева, 200 единиц железа, 100 камней')
    context.chat_data['to_hire'] = 'sieges'
    return HIRING





def chose_type_of_buildings(update: Update, context: CallbackContext):
    markup = ReplyKeyboardMarkup([['Производства'], ['Хранилища'], ['Прочие строения'], ['Вернуться в меню']],
                                 one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text('Что вы хотите построить?', reply_markup=markup)
    return WAITING_FOR_TYPE_OF_BUILDING

@log
def build_productions(update: Update, context: CallbackContext):
    construction_markup = ReplyKeyboardMarkup([['Ферма', 'Каменоломня', 'Лесопилка'],
                                               ['Железный рудник', 'Золотой рудник'],
                                               ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        "Каких производств желаете построить?", reply_markup=construction_markup)
    return PRODUCTIONS


def build_storages(update: Update, context: CallbackContext):
    storages_markup = ReplyKeyboardMarkup([['Еда', 'Камни', 'Дерево'],
                                           ['Железо', 'Золото'],
                                           ['Железная руда', 'Золотая руда'],
                                           ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Хранилища для каких ресурсов желаете построить?', reply_markup=storages_markup)
    return STORAGES


def build_others(update: Update, context: CallbackContext):
    others_markup = ReplyKeyboardMarkup([['Жилые здания'], ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Какие здания хотите построить?', reply_markup=others_markup)
    return OTHERS


def build_storages_food(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одного хранилища еды составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_STORAGES['food']]))
    context.chat_data['to_build'] = 'food_storages'
    return WAITING_FOR_COUNT_TO_BUILD

def build_storages_wood(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одного хранилища дерева составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_STORAGES['wood']]))
    context.chat_data['to_build'] = 'wood_storages'
    return WAITING_FOR_COUNT_TO_BUILD

def build_storages_stone(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одного хранилища камней составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_STORAGES['stone']]))
    context.chat_data['to_build'] = 'stone_storages'
    return WAITING_FOR_COUNT_TO_BUILD

def build_storages_iron(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одного хранилища железа составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_STORAGES['iron']]))
    context.chat_data['to_build'] = 'iron_storages'
    return WAITING_FOR_COUNT_TO_BUILD

def build_storages_gold(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одного хранилища железа составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_STORAGES['gold']]))
    context.chat_data['to_build'] = 'gold_storages'
    return WAITING_FOR_COUNT_TO_BUILD

def build_storages_iron_ore(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одного хранилища железной руды составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_STORAGES['iron_ore']]))
    context.chat_data['to_build'] = 'iron_ore_storages'
    return WAITING_FOR_COUNT_TO_BUILD

def build_storages_gold_ore(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одного хранилища золотой руды составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_STORAGES['gold_ore']]))
    context.chat_data['to_build'] = 'gold_ore_storages'
    return WAITING_FOR_COUNT_TO_BUILD

def build_houses(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одного дома составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_OTHERS['houses']]))
    context.chat_data['to_build'] = 'houses'
    return WAITING_FOR_COUNT_TO_BUILD






def check_hiring(update: Update, context: CallbackContext):
    markup_fail = ReplyKeyboardMarkup([['Попробовать еще раз'], ['Вернуться в меню']], one_time_keyboard=False,
                                      resize_keyboard=True)
    markup_success = ReplyKeyboardMarkup([['Нанять еще войска'], ['Вернуться в меню']], one_time_keyboard=False,
                                         resize_keyboard=True)
    try:
        count = int(update.message.text)
        stone = cur.execute('SELECT stone FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
        wood = cur.execute('SELECT wood FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
        food = cur.execute('SELECT food FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
        iron = cur.execute('SELECT iron FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
        gold = cur.execute('SELECT gold FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]

        needed_iron = ARMY[context.chat_data['to_hire']][0][1] * count
        needed_1 = ARMY[context.chat_data['to_hire']][1][1] * count
        needed_2 = ARMY[context.chat_data['to_hire']][2][1] * count

        if context.chat_data['to_hire'] == 'infantry' or context.chat_data['to_hire'] == 'cavalry':
            if needed_1 > gold or needed_2 > food or needed_iron > iron:
                update.message.reply_text('У вас недостаточно ресурсов!', reply_markup=markup_fail)
                return CHANGE_OR_GO_TO_MENU_ARMY
        else:
            if needed_1 > stone or needed_2 > wood or needed_iron > iron:
                update.message.reply_text('У вас недостаточно ресурсов!', reply_markup=markup_fail)
                return CHANGE_OR_GO_TO_MENU_ARMY
        update.message.reply_text('Вы успешно наняли войска', reply_markup=markup_success)
        transaction_hiring(context.chat_data['to_hire'], count, ARMY[context.chat_data['to_hire']][0][0], needed_iron,
                           ARMY[context.chat_data['to_hire']][1][0], needed_1,
                           ARMY[context.chat_data['to_hire']][2][0], needed_2, update.message.from_user.id)
        return SUCCESSFUL_HIRING
    except ValueError:
        update.message.reply_text('Похоже, то что вы ввели, не выглядит как натуральное число.',
                                  reply_markup=markup_fail)
        return CHANGE_OR_GO_TO_MENU_ARMY





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
    delta = increment_resources('stone', inc_stone * quarries, user_id)
    message = 'Заполнены следующие хранилища: '
    if delta != -1:
        inc_stone = delta
        message += 'хранилища камня, '
    delta = increment_resources('wood', inc_wood * sawmills, user_id)
    if delta != -1:
        inc_wood = delta
        message += 'хранилища дерева, '
    delta = increment_resources('food', inc_food * farms, user_id)
    if delta != -1:
        inc_food = delta
        message += 'хранилища еды, '
    delta = increment_resources('gold_ore', inc_gold_ore * gold_mines, user_id)
    if delta != -1:
        inc_gold_ore = delta
        message += 'хранилища золотой руды, '
    delta = increment_resources('iron_ore', inc_iron_ore * iron_mines, user_id)
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
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц еды. Какое количество золота Вы собираетесь потратить?')
    context.chat_data['material'] = 'food'
    return WAITING_FOR_SUM_TO_BUY


@log
def buy_wood(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц дерева. Какое количество золота Вы собираетесь потратить?')
    context.chat_data['material'] = 'wood'
    return WAITING_FOR_SUM_TO_BUY


@log
def buy_stone(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц камня. Какое количество золота Вы собираетесь потратить?')
    context.chat_data['material'] = 'stone'
    return WAITING_FOR_SUM_TO_BUY


@log
def buy_iron(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц железа. Какое количество золота Вы собираетесь потратить?')
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
                transaction_buy(context.chat_data['material'], summ, update.message.from_user.id)
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


@log
def check_build(update: Update, context: CallbackContext):
    markup_fail = ReplyKeyboardMarkup([['Попробовать еще раз'], ['Вернуться в меню']], one_time_keyboard=False,
                                      resize_keyboard=True)
    markup_success = ReplyKeyboardMarkup([['Продолжить строительство'], ['Вернуться в меню']], one_time_keyboard=False,
                                         resize_keyboard=True)
    try:
        count_of_buildings = int(update.message.text)
        spisok = []
        if count_of_buildings <= 0:
            raise ValueError
        if context.chat_data['to_build'].endswith('_storages'):
            spisok_ = PRICE_OF_STORAGES
            key = context.chat_data['to_build'][:-9]
        elif context.chat_data['to_build'] == 'houses':
            spisok_ = PRICE_OF_OTHERS
            key = 'houses'
        else:
            spisok_ = PRICE_OF_PRODUCTIONS
            key = context.chat_data['to_build']
        for i in spisok_[key]:
            total_count_of_resources = cur.execute(
                'SELECT {} FROM resources WHERE tg_id = {}'.format(i[0], update.message.from_user.id)).fetchone()[0]
            if i[1] * count_of_buildings > total_count_of_resources:
                update.message.reply_text('К сожалению, у вас недостаточно ресурсов!', reply_markup=markup_fail)
                return CHANGE_OR_GO_TO_MENU_BUILDINGS
            spisok.append([i[0], i[1] * count_of_buildings])
        else:
            update.message.reply_text('Строительство успешно завершено!', reply_markup=markup_success)
            transaction_build(spisok[0][0], spisok[0][1], spisok[1][0], spisok[1][1], spisok[2][0], spisok[2][1],
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
            transaction_remelt(context.chat_data['to_remelt'], count, update.message.from_user.id)
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
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_PRODUCTIONS['farms']]))
    context.chat_data['to_build'] = 'farms'
    return WAITING_FOR_COUNT_TO_BUILD


@log
def build_quarries(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной каменоломни составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_PRODUCTIONS['quarries']]))
    context.chat_data['to_build'] = 'quarries'
    return WAITING_FOR_COUNT_TO_BUILD


@log
def build_sawmills(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной лесопилки составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_PRODUCTIONS['sawmills']]))
    context.chat_data['to_build'] = 'sawmills'
    return WAITING_FOR_COUNT_TO_BUILD


@log
def build_iron_mines(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одной железной шахты составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_PRODUCTIONS['iron_mines']]))
    context.chat_data['to_build'] = 'iron_mines'
    return WAITING_FOR_COUNT_TO_BUILD


@log
def build_gold_mines(update: Update, context: CallbackContext):
    update.message.reply_text('Стоимость одного золотого рудника составляет: \n'
                              ' {} дерева \n'
                              ' {} железа \n'
                              ' {} дерева \n'
                              ' {} еды для рабочих'.format(*[i[1] for i in PRICE_OF_PRODUCTIONS['gold_mines']]))
    context.chat_data['to_build'] = 'gold_mines'
    return WAITING_FOR_COUNT_TO_BUILD


@log
def remelt_iron(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Введите количество железной руды, которое вы хотите переплавить. '
        'За 5 единиц железной руды вы получите 1 единицу железа.')
    context.chat_data['to_remelt'] = 'iron_ore'
    return WAITING_FOR_COUNT_OF_METAL


@log
def remelt_gold(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Введите количество золотой руды, которое вы хотите переплавить. '
        'За 10 единиц золотой руды вы получите 1 единицу золота.')
    context.chat_data['to_remelt'] = 'gold_ore'
    return WAITING_FOR_COUNT_OF_METAL


@log
def foreign_policy(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    war_level, in_spying = cur.execute('SELECT foreign_policy, in_spying FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()
    infantry, cavalry, sieges = cur.execute('SELECT * FROM army WHERE tg_id = {}'.format(user_id)).fetchone()[1:-1]
    
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


@log
def path_to_city(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    war_level = cur.execute('SELECT foreign_policy FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    opposite_city = cur.execute('SELECT * FROM npc_cities WHERE id = {}'.format(war_level)).fetchone()
    
    chance = random.random() + war_level * 0.05
    a = 'Мы можем поити в разведку, чтобы узнать более точную информацию.'
    
    if chance <= 0.1:
        cur.execute('UPDATE cities SET in_spying = -1 WHERE tg_id = {}'.format(user_id))
        legend = 'Каналья! Нас засекли... Придётся сразу идти в бой, у нас нет выхода.\n\n'
        war_markup = ReplyKeyboardMarkup([
            ['В атаку! ⚔️'],
            ['Вернуться в меню']
        ], one_time_keyboard=False, resize_keyboard=True)
        a = ''
    else:
        cur.execute('UPDATE cities SET in_spying = 1 WHERE tg_id = {}'.format(user_id))
        legend = 'Отлично! Мы смогли незаметно для противника расчистить место для разведки!\n\n'
        war_markup = ReplyKeyboardMarkup([
            ['На разведку! 🥷🏻', 'В атаку! ⚔️'],
            ['Вернуться в меню']
        ], one_time_keyboard=False, resize_keyboard=True)
    con.commit()
    
    phrase = random.choice(['Ходят слухи, что это ', 'Поговаривают, что это ', 
                            'Говорят, что это ', 'По всему миру это место известно как ',
                            'Везде ходят слухи, что это ', 'Всем кажется, что это ',
                            'Везде известно, что это ', 'По всему миру ходят слухи, что это ',
                            'Все знают, что это ', 'Всем это место известно как ']) + opposite_city[7] + '...\n\n'

    get_opposite_city(user_id, context, 0)
    
    update.message.reply_text(
        legend + phrase + 'Вот что мы смогли разведать во время расчистки пути.\n'
        '🏰 Название: {}\n'
        '💰 Из последних публичных отчётов о бюджете нам известно, что в городе {} золота.\n\n'
        'Мы посчитали стражу вокруг, но могли ошибиться. В городе:\n'
        '⠀⠀- {} жителей 👥\n'
        '⠀⠀- {} пехоты 🏹\n'
        '⠀⠀- {} кавалерии 🐎\n'
        'Скорее всего нам понадобится {} осадных машин, чтобы пробить стены 🦬\n\n'
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
        '{}'.format(
            context.chat_data['opposite.name'], context.chat_data['opposite.gold'],
            context.chat_data['opposite.fake_population'], context.chat_data['opposite.fake_infantry'],
            context.chat_data['opposite.fake_cavalry'], context.chat_data['opposite.fake_requiered_sieges'],
            context.chat_data['opposite.fake_stone'], context.chat_data['opposite.fake_wood'],
            context.chat_data['opposite.fake_food'], context.chat_data['opposite.fake_iron_ore'],
            context.chat_data['opposite.fake_gold_ore'], context.chat_data['opposite.farms'],
            context.chat_data['opposite.quarries'], context.chat_data['opposite.sawmills'], a
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
        update.message.reply_text('Каналья! Нас засекли... Придётся идти в бой, у нас нет выхода.',
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
    
    a = 'Внутри города мы пересчитали жителей, всё ещё могут быть ошибки. В городе:\n' if in_spying != 3 else 'Внутри города мы пересчитали жителей, в этот раз без ошибок. В городе:\n'
    b = ('Скорее всего нам понадобится {} осадных машин, чтобы пробить стены 🦬\n\n' if in_spying != 3 else '⠀⠀Нам точно понадобится {} осадных машин, чтобы пробить стены 🦬\n\n').format(
        context.chat_data['opposite.fake_requiered_sieges']
    )
    c = 'Более точные данные по ресурсам в хранилищах:\n' if in_spying != 3 else 'Максимально точные данные по ресурсам в хранилищах:\n'
    d = 'Мы можем продолжить разведку, чтобы узнать более точную информацию.' if in_spying != 3 else 'Вся информация на руках. Теперь мы готовы к бою!'
    update.message.reply_text(
        legend + 'Мы вернулись с разведки с новой информацией.\n{}'
        '⠀⠀- {} жителей 👥\n'
        '⠀⠀- {} пехоты 🏹\n'
        '⠀⠀- {} кавалерии 🐎\n{}{}'
        '⠀⠀- {} единиц камня 🪨\n'
        '⠀⠀- {} единиц дерева 🪵\n'
        '⠀⠀- {} единиц еды 🥩\n'
        '⠀⠀- {} единиц железной руды 🏭\n'
        '⠀⠀- {} единиц золотой руды 🏭\n\n{}'.format(
            a, context.chat_data['opposite.fake_population'], context.chat_data['opposite.fake_infantry'],
            context.chat_data['opposite.fake_cavalry'], b, c, context.chat_data['opposite.fake_stone'],
            context.chat_data['opposite.fake_wood'], context.chat_data['opposite.fake_food'], 
            context.chat_data['opposite.fake_iron_ore'], context.chat_data['opposite.fake_gold_ore'], d
        ), reply_markup=war_markup
    )
    
    return FOREIGN_POLICY

def attack(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    sieges = cur.execute('SELECT sieges FROM army WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    infantry = cur.execute('SELECT infantry FROM army WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    cavalry = cur.execute('SELECT cavalry FROM army WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    stone = cur.execute('SELECT stone FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    wood = cur.execute('SELECT wood FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    iron_ore = cur.execute('SELECT iron_ore FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    gold_ore = cur.execute('SELECT gold_ore FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    gold = cur.execute('SELECT gold FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    populate = cur.execute('SELECT population FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    farms = cur.execute('SELECT farms FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    quarries = cur.execute('SELECT quarries FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    sawmills = cur.execute('SELECT sawmills FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    war_level = cur.execute('SELECT foreign_policy FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    
    if 'opposite.name' not in context.chat_data:
        get_opposite_city(user_id, context, 3)
        
    if context.chat_data['opposite.requiered_sieges'] > sieges:
        update.message.reply_text('Наших осадных машин не хватило, чтобы пробить стену города. Наша армия уничтожена.', reply_markup=markup)
        cur.execute('UPDATE army SET infantry = 0 WHERE tg_id = {}'.format(user_id))
        cur.execute('UPDATE army SET cavalry = 0 WHERE tg_id = {}'.format(user_id))
        cur.execute('UPDATE army SET sieges = 0 WHERE tg_id = {}'.format(user_id))
        cur.execute('UPDATE cities SET in_spying = 0 WHERE tg_id = {0}'.format(user_id))
    elif context.chat_data['opposite.infantry'] + 10 * context.chat_data['opposite.cavalry'] <= infantry + 10 * cavalry:
        update.message.reply_text('Мы победили! {} присоединился к нашей растущей агломерации!\n'
                                  'Мы получили: {} еды, {} камня, {} дерева, {} железной руды, {} золотой руды, {} золота.\n'
                                  'Число наших производств увеличилось: {} ферм, {} каменоломен, {} лесопилки.\n'
                                  'Население нашей агломерации увеличилось на {} человек.'.format(
                                      context.chat_data['opposite.name'], context.chat_data['opposite.food'], context.chat_data['opposite.stone'], 
                                      context.chat_data['opposite.wood'], context.chat_data['opposite.iron_ore'], context.chat_data['opposite.gold_ore'], 
                                      context.chat_data['opposite.gold'], context.chat_data['opposite.farms'], context.chat_data['opposite.quarries'], 
                                      context.chat_data['opposite.sawmills'], context.chat_data['opposite.population']), reply_markup=markup)

        cur.execute('UPDATE army SET infantry = {} WHERE tg_id = {}'.format(round(infantry * 0.5), user_id))
        cur.execute('UPDATE army SET cavalry = {} WHERE tg_id = {}'.format(round(cavalry * 0.5), user_id))
        cur.execute('UPDATE army SET sieges = {} WHERE tg_id = {}'.format(round(sieges * 0.5), user_id))
        
        cur.execute('UPDATE resources SET stone = {2} + {1} WHERE tg_id = {0}'.format(user_id, context.chat_data['opposite.stone'], stone))
        cur.execute('UPDATE resources SET wood = {2} + {1} WHERE tg_id = {0}'.format(user_id, context.chat_data['opposite.wood'], wood))
        cur.execute('UPDATE resources SET iron_ore = {2} + {1} WHERE tg_id = {0}'.format(user_id, context.chat_data['opposite.iron_ore'], iron_ore))
        cur.execute('UPDATE resources SET gold_ore = {2} + {1} WHERE tg_id = {0}'.format(user_id, context.chat_data['opposite.gold_ore'], gold_ore))
        cur.execute('UPDATE resources SET gold = {2} + {1} WHERE tg_id = {0}'.format(user_id, context.chat_data['opposite.gold'], gold))
        cur.execute('UPDATE resources SET population = {2} + {1} WHERE tg_id = {0}'.format(user_id, context.chat_data['opposite.population'], populate))
        
        cur.execute('UPDATE buildings SET farms = {2} + {1} WHERE tg_id = {0}'.format(user_id, context.chat_data['opposite.farms'], farms))
        cur.execute('UPDATE buildings SET quarries = {2} + {1} WHERE tg_id = {0}'.format(user_id, context.chat_data['opposite.quarries'], quarries))
        cur.execute('UPDATE buildings SET sawmills = {2} + {1} WHERE tg_id = {0}'.format(user_id, context.chat_data['opposite.sawmills'], sawmills))
        
        cur.execute('UPDATE cities SET foreign_policy = {1} + 1 WHERE tg_id = {0}'.format(user_id, war_level))
        cur.execute('UPDATE cities SET in_spying = 0 WHERE tg_id = {0}'.format(user_id))
        
    else:
        update.message.reply_text('К сожалению, защитники города оказались сильнее. Наша армия уничтожена.', reply_markup=markup)
        cur.execute('UPDATE army SET infantry = 0 WHERE tg_id = {}'.format(user_id))
        cur.execute('UPDATE army SET cavalry = 0 WHERE tg_id = {}'.format(user_id))
        cur.execute('UPDATE army SET sieges = 0 WHERE tg_id = {}'.format(user_id))
        cur.execute('UPDATE cities SET in_spying = 0 WHERE tg_id = {0}'.format(user_id))
    
    con.commit()
    return BACK_TO_MENU

@log
def get_info_about_opposite(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    in_spying = cur.execute('SELECT in_spying FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0]

    if 'opposite.name' not in context.chat_data:
        get_opposite_city(user_id, context, 3)

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

    a = 'Мы можем поити в разведку, чтобы узнать более точную информацию.' if in_spying != -1 else 'Сейчас мы может только атаковать город.'
    update.message.reply_text(
        'Вот что нам известно на текущий момент.\n'
        '🏰 Название: {}\n'
        '💰 В городе точно {} золота.\n\n'
        'Вероятно, в городе:\n'
        '⠀⠀- {} жителей 👥\n'
        '⠀⠀- {} пехоты 🏹\n'
        '⠀⠀- {} кавалерии 🐎\n'
        'Скорее всего нам понадобится {} осадных машин, чтобы пробить стены 🦬\n'
        'Если осадных машин или войска не хватит, то мы потеряем их и нам придётся отступить.\n'
        'Все жители этого города станут нашими в случае победы.\n\n'
        'Предполагаемое количество ресурсов в хранилищах:\n'
        '⠀⠀- {} единиц камня 🪨\n'
        '⠀⠀- {} единиц дерева 🪵\n'
        '⠀⠀- {} единиц еды 🥩\n'
        '⠀⠀- {} единиц железной руды 🏭\n'
        '⠀⠀- {} единиц золотой руды 🏭\n'
        'Все ресурсы безоговорочно становятся нашими, если мы побеждаем.\n\n'
        'В городе стоит:\n'
        '⠀⠀- {} ферм 🧑🏻‍🌾\n'
        '⠀⠀- {} каменоломен 🪨\n'
        '⠀⠀- {} лесопилок 🪵\n'
        'В случае победы эти производства попадут к нам в сломанном состоянии, и мы сможем или восстановить их, '
        'чтобы они стали частью нашего города, или разрушить и получить 20% от стоимости производств.\n\n{}'.format(
            context.chat_data['opposite.name'], context.chat_data['opposite.gold'],
            context.chat_data['opposite.fake_population'], context.chat_data['opposite.fake_infantry'],
            context.chat_data['opposite.fake_cavalry'], context.chat_data['opposite.fake_requiered_sieges'],
            context.chat_data['opposite.fake_stone'], context.chat_data['opposite.fake_wood'],
            context.chat_data['opposite.fake_food'], context.chat_data['opposite.fake_iron_ore'],
            context.chat_data['opposite.fake_gold_ore'], context.chat_data['opposite.farms'],
            context.chat_data['opposite.quarries'], context.chat_data['opposite.sawmills'], a
        ), reply_markup=foreign_policy_markup
    )
