import logging

from telegram import Update
from telegram.ext import CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def log(func):  # Декоратор для логирования
    def wrapper(update: Update, context: CallbackContext) -> int:
        logger.info('{}: {}'.format(update.message.from_user.id, update.message.text))
        return func(update, context)
    return wrapper
