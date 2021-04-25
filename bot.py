from secrets import API_KEY

from datetime import datetime

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

from game import (CHANGE_OR_GO_TO_MENU_BUILDINGS, CHANGE_OR_GO_TO_MENU_MARKET,
                  CHANGE_OR_GO_TO_MENU_REMELTING, CONSTRUCTION, FOREIGN_POLICY,
                  INFO, MARKET, MENU, POPULATION, RESOURCES, SUCCESSFUL_BUILD,
                  SUCCESSFUL_BUYING, SUCCESSFUL_REMELTING,
                  WAITING_FOR_CITY_NAME, WAITING_FOR_COUNT_OF_METAL,
                  WAITING_FOR_COUNT_TO_BUILD, WAITING_FOR_SUM_TO_BUY,
                  WAITING_FOR_TYPE_OF_METAL, build_farms, build_gold_mines,
                  build_iron_mines, build_quarries, build_sawmills, buy_food,
                  buy_iron, buy_stone, buy_wood, check_build, check_buy,
                  check_remelt, con, construction, cultivating, cur,
                  foreign_policy, get_info_about_city, list_of_players, market,
                  population, remelt_gold, remelt_iron, remelting, resources)
from logger import log

img_city = open("city.jpg", 'rb')

markup = ReplyKeyboardMarkup([['Город'],
                              ['Ресурсы', 'Рынок'],
                              ['Население', 'Строительство'],
                              ['Внешняя политика']],
                             one_time_keyboard=False, resize_keyboard=True)


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
    update.message.reply_photo(img_city,
                               "Вновь добро пожаловать в {}!".format(context.chat_data['city_name']),
                               reply_markup=markup)
    img_city.seek(0)
    return MENU


@log
def set_name(update: Update, context: CallbackContext) -> int:
    name, user_id = update.message.text, update.message.from_user.id
    update.message.reply_text('''
Прекрасный выбор! Мы уверены, что ваш город с гордым именем {} ждут небывалые свершения.
Удачи, император! ✊🏻
Вы всегда можете отправить команду /help, чтобы получить подробную справку по управлению и механикам.
    '''.format(name))

    cur.execute('INSERT INTO cities VALUES ({}, "{}")'.format(user_id, name))
    cur.execute('INSERT INTO buildings VALUES ({}, 1, 1, 1, 1, 1)'.format(user_id))
    cur.execute('INSERT INTO resources '
                'VALUES ({}, 1000, 1000, 1000, 1000, 1000, 1000, 1000, "{}")'.format(user_id, datetime.now().isoformat(sep=' ')))
    list_of_players.append(user_id)
    con.commit()
    context.chat_data['city_name'] = name

    update.message.reply_photo(img_city,
                               "Добро пожаловать в {}!".format(context.chat_data['city_name']),
                               reply_markup=markup)
    img_city.seek(0)
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
    update.message.reply_photo(img_city,
                               "Добро пожаловать в {}!".format(context.chat_data['city_name']),
                               reply_markup=markup)
    img_city.seek(0)
    return MENU


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

            RESOURCES: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                        MessageHandler(Filters.regex('^(Собрать ресурсы)$'), cultivating),
                        MessageHandler(Filters.regex('^(Переплавить руду)$'), remelting)],

            MARKET: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                     MessageHandler(Filters.regex('^(Еда)$'), buy_food),
                     MessageHandler(Filters.regex('^(Дерево)$'), buy_wood),
                     MessageHandler(Filters.regex('^(Камни)$'), buy_stone),
                     MessageHandler(Filters.regex('^(Железо)$'), buy_iron)],

            POPULATION: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],

            CONSTRUCTION: [MessageHandler(Filters.regex('^(Лесопилка)$'), build_sawmills),
                           MessageHandler(Filters.regex('^(Ферма)$'), build_farms),
                           MessageHandler(Filters.regex('^(Каменоломня)$'), build_quarries),
                           MessageHandler(Filters.regex('^(Золотой рудник)$'), build_gold_mines),
                           MessageHandler(Filters.regex('^(Железный рудник)$'), build_iron_mines),
                           MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],

            FOREIGN_POLICY: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],
            INFO: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],

            WAITING_FOR_CITY_NAME: [MessageHandler(Filters.text, set_name)],
            WAITING_FOR_SUM_TO_BUY: [MessageHandler(Filters.text, check_buy)],
            WAITING_FOR_COUNT_TO_BUILD: [MessageHandler(Filters.text, check_build)],
            WAITING_FOR_TYPE_OF_METAL: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                        MessageHandler(Filters.regex('^(Железная руда)$'), remelt_iron),
                                        MessageHandler(Filters.regex('^(Золотая руда)$'), remelt_gold)],
            WAITING_FOR_COUNT_OF_METAL: [MessageHandler(Filters.text, check_remelt)],

            CHANGE_OR_GO_TO_MENU_MARKET: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                          MessageHandler(Filters.regex('^(Попробовать еще раз)$'), market)],
            CHANGE_OR_GO_TO_MENU_BUILDINGS: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                             MessageHandler(Filters.regex('^(Попробовать еще раз)$'), construction)],
            CHANGE_OR_GO_TO_MENU_REMELTING: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                             MessageHandler(Filters.regex('^(Попробовать еще раз)$'), remelting)],

            SUCCESSFUL_BUYING: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                MessageHandler(Filters.regex('^(Продолжить покупки)$'), market)],
            SUCCESSFUL_BUILD: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                               MessageHandler(Filters.regex('^(Продолжить строительство)$'), construction)],
            SUCCESSFUL_REMELTING: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                   MessageHandler(Filters.regex('^(Продолжить переплавку)$'), remelting)]


        },
        fallbacks=[CommandHandler('cancel', menu)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


run()
