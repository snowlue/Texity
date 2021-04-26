from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext

from logger import log

(ABOUT_RESOURCES, ABOUT_MARKET, ABOUT_POPULATION,
 ABOUT_CONSTRUCTION, ABOUT_FOREIGN_POLICY, ABOUT_CITY, HELP) = range(-7, 0)

help_markup = ReplyKeyboardMarkup([['Про город'],
                                   ['Про ресурсы', 'Про рынок'],
                                   ['Про население', 'Про строительство'],
                                   ['Про внешнюю политику'],
                                   ['Вернуться в меню']],
                                  one_time_keyboard=False, resize_keyboard=True)

@log
def help_(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Постройте свой город и реализуйте его действия, '
        'нажмите на кнопки, чтобы узнать больше информации',
        reply_markup=help_markup)
    return HELP


@log
def about_market(update: Update, context: CallbackContext):
    update.message.reply_text(
        'На рынке Вы можете покупать ресурсы за золото')
    return HELP


@log
def about_city(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Повышайте уровень своего города для увеличения '
        'производства. В городе вы можете узнать количество производств')
    return HELP


@log
def about_resources(update: Update, context: CallbackContext):
    update.message.reply_text(
        'В ресурсах можно узнать количество определенного '
        'вида ресурсов и переплавить различные виды руды')
    return HELP


@log
def about_population(update: Update, context: CallbackContext):
    update.message.reply_text(
        'В население вы можете узнать свое население и '
        'про вашу армию')
    return HELP


@log
def about_constrution(update: Update, context: CallbackContext):
    update.message.reply_text(
        'В строительстве вы можете строить новые здания')
    return HELP


@log
def about_foreign_policy(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Во внешней политике вы можете узнать уровень '
        'своего города, а также про ваше войско')
    return HELP
