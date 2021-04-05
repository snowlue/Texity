import logging
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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

NAME = 0


def start(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        '''
Приветствуем тебя в Texity - пошаговой стратегии, в которой ты можешь развивать свой город, чтобы достичь светлого экономического будущего.
Ты всегда можешь написать команду /help, чтобы получить подробную справку по управлению и механикам.
        
Итак, введи имя своего города: ''',
    )

    return NAME


def naming(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    name_of_city = update.message.text
    logger.info("Имя города пользователя %s: %s", user.first_name, name_of_city)
    update.message.reply_text(
        '''
    Прекрасный выбор! Мы уверены, что ваш город с гордым именем "{}" ждут небывалые свершения.
Удачи, император.
'''.format(name_of_city),
    )

    return ConversationHandler.END


def skip(update: Update, _: CallbackContext):
    pass


def help(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s попросил помощь.", user.first_name)
    update.message.reply_text(
        'Мир суров. Поэтому рабирайся сам.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
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
    main()
