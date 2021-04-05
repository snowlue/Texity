from secrets import API_KEY

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

from logger import log, logger

NAME = 0

@log
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        '''
Приветствуем тебя в Texity - пошаговой стратегии, в которой ты можешь развивать свой город, чтобы достичь светлого экономического будущего.
Ты всегда можешь написать команду /help, чтобы получить подробную справку по управлению и механикам.
        
Итак, введи имя своего города! ''',
    )

    return NAME


@log
def naming(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    name_of_city = update.message.text
    #! Добавить город в БД!
    update.message.reply_text(
        '''
Прекрасный выбор! Мы уверены, что ваш город с гордым именем "{}" ждут небывалые свершения.
Удачи, император.
'''.format(name_of_city),
    )

    return ConversationHandler.END


def skip(update: Update, context: CallbackContext):
    pass


@log
def help(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    #todo: Вызввать админов или порешать, как должен работать /help
    update.message.reply_text(
        'Мир суров. Поэтому рабирайся сам.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def run() -> None:
    updater = Updater(API_KEY)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text, naming)],
        },
        fallbacks=[CommandHandler('cancel', skip)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('help', help))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run()
