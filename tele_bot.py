from random import randint
import requests
import logging
from logging.handlers import RotatingFileHandler

from telegram.ext import (Updater,
                          Filters,
                          MessageHandler,
                          CommandHandler)
from telegram import ReplyKeyboardMarkup

from constants import (BASE_DIR,
                       DT_FORMAT,
                       KEY,
                       LOG_FORMAT,
                       TOKEN,
                       URL_CAT,
                       URL_TRANSLATE,
                       URL_WEATHER,
                       CONVERTER_PRESSURE)


log_dir = BASE_DIR / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / 'bot.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
rotating_handler = RotatingFileHandler(
    log_file, maxBytes=10 ** 6, backupCount=5, encoding='utf-8'
)
logging.basicConfig(
    datefmt=DT_FORMAT,
    format=LOG_FORMAT,
    level=logging.INFO,
    handlers=(rotating_handler, logging.StreamHandler())
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


updater = Updater(token=TOKEN)


def get_image():
    """Функция запроса к API котов."""
    try:
        response = requests.get(URL_CAT).json()
        logger.info('Запрос к эндпоинту отправлен успешно!')
    except Exception as error:
        logger.error(f'Ошибка при запросе к основному API: {error}')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)
    random_cat = response[0].get('url')
    return random_cat


def what_weather():
    """Функция запроса погоды."""
    try:
        querystring = {
            "lat": "52.320937",
            "lon": "34.088388",
            "timezone": "auto",
            "language": "en",
            "units": "auto"
        }
        headers = {
            "X-RapidAPI-Key": f"{KEY}",
            "X-RapidAPI-Host": "ai-weather-by-meteosource.p.rapidapi.com"
        }
        response = requests.get(URL_WEATHER, headers=headers, params=querystring)
        if response.ok:
            logger.info('Запрос о погоде прошёл!')
            param = response.json().get('current')
            temperature = param.get('temperature')
            wind = param.get('wind').get('speed')
            feels_like = param.get('feels_like')
            pressure = param.get('pressure')
            summary = param.get('summary')
            return (
                f'{translate_text(summary, to_language="ru")}. '
                f'Температура: {int(temperature)}°C, '
                f'По ощущениям: {feels_like}°C, '
                f'Скорость ветра: {wind}м/с, '
                f'Давление: {round(pressure * CONVERTER_PRESSURE)}мм.рт.cт. '
            )
        else:
            logger.error(f'Статус {response.status_code}')
    except Exception as er:
        logger.error(f'Ошибка {er}')
        return f'Ошибка {er}'


def where_you_leave(update, context):
    """
    Опциональная функция о городе
    (пока выводит погоду определенного города).
    """
    chat = update.effective_chat
    context.bot.send_message(chat.id, what_weather())
    logger.info('Погода успешно отправлена!')


def my_id(update, context):
    """Функция вывода id пользователя."""
    chat = update.effective_chat
    client_id = update.message.chat.id
    context.bot.send_message(chat.id, client_id)
    logger.info('Успешно вывело id пользователя!')


def digit_random(update, context):
    """Функция вывоад случайного числа(пока не знаю зачем)."""
    chat = update.effective_chat
    context.bot.send_message(chat.id, randint(1, 100))
    logger.info('Успешно вывело рандомное число!')


def new_cat(update, context):
    """Функция непосредственно отправки котов(или собак)."""
    chat = update.effective_chat
    context.bot.send_message(chat.id, get_image())
    logger.info('Фото успешно отправлено!')


def say_hi(update, context):
    """Функция приветствия бота."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(chat_id=chat.id,
                             text='Hello, {}!'.format(name))


def buttons_func(update, context):
    """Функция кнопок."""
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([['/Foto_cat🐾',
                                    '/My_ID🆔',
                                   '/Random_digit🎰',
                                    '/Weather🌦️',
                                    '/Translate🈯',
                                    '/Cancel❌',
                                    ]], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Я восстал, кожаный.',
        reply_markup=buttons
        )
    logger.info('Бот активирован!')


def translate_text(text, to_language='en'):
    """Функция преевода в режиме онлайн."""
    try:
        querystring = {"to[0]": f"{to_language}",
                       "api-version": "3.0",
                       "profanityAction": "NoAction",
                       "textType": "plain"
                       }
        payload = [{"Text": f"{text}"}]
        headers = {
            "X-RapidAPI-Key": f"{KEY}",
        }
        response = requests.post(URL_TRANSLATE, json=payload, headers=headers, params=querystring)
        translate = response.json()[0].get('translations')[0].get('text')
        if response.ok:
            logger.info('Перевод выполнен!')
            return translate.capitalize()
        else:
            logger.error(f'Статус {response.status_code}')
            return 'Не удалось подключиться к эндпоинту'
    except Exception as er:
        logger.error(f'Ошибка{er}.')
        return f'Ошибка {er}'


def start_translater(update, context):
    """Обработчик команды /translate."""
    context.user_data['state'] = 'translate'
    update.message.reply_text('Введите текст для перевода(в данной версии доступен только ru-en): ')
    logger.info('Ожидание ввода от пользователя!')


def handle_text(update, context):
    """Обработчик тестовых сообщений."""
    # Получаем текущее состояние пользователя
    state = context.user_data.get('state', 'normal')
    if state == 'translate':
        # Если состояние 'перевод', выполняем перевод
        text = update.message.text
        translated_text = translate_text(text)
        update.message.reply_text(translated_text)
        # Сброс состояния
        context.user_data['state'] = 'normal'


def cancel(update, context):
    """Сбрасываение состояния."""
    context.user_data['state'] = 'normal'
    update.message.reply_text('Отменено')
    logger.info('Состояние отменено успешно!')


def main():
    updater.dispatcher.add_handler(CommandHandler('start', buttons_func))
    updater.dispatcher.add_handler(CommandHandler('translate', start_translater))
    updater.dispatcher.add_handler(CommandHandler('weather', where_you_leave))
    updater.dispatcher.add_handler(CommandHandler('my_id', my_id))
    updater.dispatcher.add_handler(CommandHandler('foto_cat', new_cat))
    updater.dispatcher.add_handler(CommandHandler('cancel', cancel))
    updater.dispatcher.add_handler(CommandHandler('random_digit', digit_random))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_text))
    updater.start_polling()
    updater.idle()
    logger.info('Бот диактивирован!')


if __name__ == '__main__':
    logger.info('Бот начал работу')
    main()
