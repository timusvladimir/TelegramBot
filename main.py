# тестирование БД mars_explorer
#from data3 import db_session
#from data3.jobs import Jobs
#from data3.departments import Department

# данные игрового форума
from data import db_session
from data.news import News
from data.users import User
from data.themes import Theme
from data.comments import Comment

import math
import random

from emoji.core import emojize
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram.error import BadRequest, TelegramError
import sqlite3
import logging

# моя библиотека API Yandex
from geospn import llspan, find_org, lonlat_distance

# для чтения переменных среды окружения
from dotenv import load_dotenv
from os import environ

load_dotenv("env")  # берем свой файл
# ТОКЕН бота в телеграмме @Game_wiki_bot
TOKEN = environ["TOKEN"]

# Подключение моей базы данных игр
conn = sqlite3.connect("db/game.db", check_same_thread=False)
cursor = conn.cursor()

# Создание массива категорий википедии из БД
cursor.execute('SELECT name FROM Category')
categories = [i[0] for i in cursor.fetchall()]
# cursor.execute('SELECT name FROM Menu')
# menu = [i[0] for i in cursor.fetchall()]

# Подключение БД игрового форума
# db_session.global_init("db/mars_explorer.db")
db_session.global_init("db/content.db")

# Настройка и инициализация логов для отлаживания и контроля программы
# Выводит время и дату события с описанием
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Массив для описания игр из категорий
data_db = []
message_id = 0

# Этапы/состояния разговора
# FIRST, SECOND = range(2)

# Данные обратного вызова
ONE, TWO, THREE, FOUR, FIVE = range(5)

# клавиатуры кубиков и таймеров
begin_keyboard = [['/dice', '/timer']]
dice_keyboard = [['/6', '/2x6', '/20', '/return']]
timer_keyboard = [['/30s', '/1m', '/5m', '/return']]
close_keyboard = [['/close']]

begin_markup = ReplyKeyboardMarkup(begin_keyboard, one_time_keyboard=False)
dice_markup = ReplyKeyboardMarkup(dice_keyboard, one_time_keyboard=False)
timer_markup = ReplyKeyboardMarkup(timer_keyboard, one_time_keyboard=False)
close_markup = ReplyKeyboardMarkup(close_keyboard, one_time_keyboard=False)


# функция запуска бота
def start(update, context):
    context.bot.send_photo(update.message.chat_id, photo=open('cover.jpg', 'rb'))
    logging.info("Sent to @%s a Cover Photo.", update.message.from_user.first_name)
    update.message.reply_text(emojize("Это Игровой Telegram Бот!!!:love-you_gesture_light_skin_tone:\n"
                              ":man_blond_hair:Он поможет найти тебе любую нужную информацию.\n"
                              "Для входа в бот введите команду /enter, помощь команда /help!\n"
                              "Если в процессе работы бота возникните ошибка, нажмите кнопку вернуться назад или попробуйте ввести команду /enter"        ))


# функция входа в бот
def enter(update, context):
    logger.info("User %s started the conversation.", update.message.from_user.first_name)

  # keyboard = [[InlineKeyboardButton(menu[i], callback_data=i)] for i in range(len(menu))]
    keyboard = [[InlineKeyboardButton('Новости', callback_data=str(ONE))],
                [InlineKeyboardButton('Форум', callback_data=str(TWO))],
                [InlineKeyboardButton('Википедия игр', callback_data=str(THREE))],
                [InlineKeyboardButton('Утилиты', callback_data=str(FOUR))],
                [InlineKeyboardButton('Полезные ссылки', callback_data=str(FIVE))]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Выберите один из пунктов меню:', reply_markup=reply_markup)
    logging.info("Sent to @%s Message of '/start' state.", update.message.from_user.first_name)

    return 1


# функция повторного вывода начального меню бота
def enter_query(update, context):
    query = update.callback_query
    logger.info("User %s started the conversation.", query.from_user.first_name)
    query.answer()
  # keyboard = [[InlineKeyboardButton(menu[i], callback_data=i)] for i in range(len(menu))]
    keyboard = [[InlineKeyboardButton('Новости', callback_data=str(ONE))],
                [InlineKeyboardButton('Форум', callback_data=str(TWO))],
                [InlineKeyboardButton('Википедия игр', callback_data=str(THREE))],
                [InlineKeyboardButton('Утилиты', callback_data=str(FOUR))],
                [InlineKeyboardButton('Полезные ссылки', callback_data=str(FIVE))]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text('Выберите один из пунктов меню:', reply_markup=reply_markup)
    logging.info("Sent to @%s Message of '/start' state.", query.from_user.first_name)

    return 1


# функция вывода новостей игрового форума
def news(update, context):
    global data_db, message_id

    query = update.callback_query
    logger.info("Waiting @%s's answer...", query.from_user.first_name)
    query.answer()
    print(query)
    logger.info("Got answer from @%s: '{}'.".format(query.data), query.from_user.first_name)

    keyboard = [[InlineKeyboardButton('Назад', callback_data='return')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

  #  cursor.execute("SELECT text FROM News".format(query.data))
  #  data_db = cursor.fetchall()

    db_sess = db_session.create_session()
  # data_db = db_sess.query(Theme).all()
  # data_db = db_sess.query(Jobs).all()
    data_db = db_sess.query(News).all()

    text = 'Вот список новостей c игрового форума:'
  # for pos in range(len(data_db)):
  #     text = text + f'\n{pos + 1}) {data_db[pos][0].strip()}'

    for pos in range(len(data_db)):
        text = text + f'\n{pos + 1}) {data_db[pos]}'

    message_id = query.message.message_id

    query.bot.edit_message_text(text, chat_id=query.message.chat_id,
                                message_id=query.message.message_id,
                                reply_markup=reply_markup)
    #query.edit_message_text(text=text, reply_markup=reply_markup)
    logging.info("Edited @%s Message FIRST state.", query.from_user.first_name)

    return 1


# функция вывода сообщений с форума
def forum(update, context):
    global data_db, message_id

    query = update.callback_query
    variant = query.data
    # `CallbackQueries` требует ответа, даже если
    # уведомление для пользователя не требуется, в противном
    #  случае у некоторых клиентов могут возникнуть проблемы.
    # смотри https://core.telegram.org/bots/api#callbackquery.
    query.answer()
    # редактируем сообщение, тем самым кнопки
    # в чате заменятся на этот ответ.
    query.edit_message_text(text=f"Выбранный вариант: {variant}")

    keyboard = [[InlineKeyboardButton('Назад', callback_data='return')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
 #  text = 'Здесь будет информация о сообщениях на форуме'

 #  query.bot.edit_message_text(text, chat_id=query.message.chat_id,
 #                             message_id=query.message.message_id,
 #                             reply_markup=reply_markup)
    db_sess = db_session.create_session()
 #  data_db = db_sess.query(Theme).all()
 #  data_db = db_sess.query(Department).all()
    data_db = db_sess.query(User).all()

    text = 'Вот список пользователей c игрового форума:'
 #   for pos in range(len(data_db)):
 #      text = text + f'\n{pos + 1}) {data_db[pos][0].strip()}'

    for pos in range(len(data_db)):
        text = text + f'\n{pos + 1}) {data_db[pos]}'

    message_id = query.message.message_id

    query.bot.edit_message_text(text, chat_id=query.message.chat_id,
                                message_id=query.message.message_id,
                                reply_markup=reply_markup)
    # query.edit_message_text(text=text, reply_markup=reply_markup)
    logging.info("Edited @%s Message FIRST state.", query.from_user.first_name)

    return 5


# функция вывода меню википедии
def wiki(update, context):
    query = update.callback_query
    # logger.info("Waiting user's answer...", update.message.from_user.first_name)
    query.answer()
    # logger.info("User %s started the conversation.", update.message.from_user.first_name)

    keyboard = [[InlineKeyboardButton(categories[i], callback_data=i)] for i in range(len(categories))]
 #  keyboard2 = keyboard.append[InlineKeyboardButton('Назад', callback_data='return')]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text='Выберите категорию игр:', reply_markup=reply_markup)
    # logging.info("Sent to @%s Message of '/start' state.", update.message.from_user.first_name)

    return 2


# функция запуска утилит
def util(update, context):
    query = update.callback_query
    variant = query.data
    query.answer()
    query.edit_message_text(text=f"Выбранный вариант: {variant}")

    keyboard = [[InlineKeyboardButton('Назад', callback_data='return')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
  # text = 'Здесь будут различные игровые утилиты. Такие как кубик и таймер'
  # query.edit_message_text(text="Ok", reply_markup=ReplyKeyboardRemove())
  # query.bot.edit_message_text(text, chat_id=query.message.chat_id,
  #                            message_id=query.message.message_id,
  #                            reply_markup=reply_markup)
    query.edit_message_text(text="Команда /dice кинуть кубики, /timer засечь время", reply_markup=reply_markup)
  # update.message.reply_text("Команда /dice кинуть кубики, /timer засечь время", reply_markup=begin_markup)
    return 4


# функция запуска поиска магазина
def url(update, context):
    query = update.callback_query
  # variant = query.data
    query.answer()
  # query.edit_message_text(text=f"Выбранный вариант: {variant}")
    query.edit_message_text(text="Введите адрес вашего месторасположения.")
    return 3


# функция помощи по боту
def help(update, context):
    """Send info about Telegram bot"""
    logging.info("Sent to @%s a '/help' Message.", update.message.from_user.first_name)

    update.message.reply_text("Это Игровой Telegram Бот!!!\n"
                              "Он поможет найти тебе любую нужную информацию.\n"
                              "Для входа в бот введите команду /enter\n"
                              "При возникновении ошибок работы бота, так же нажмите команду /enter и вы вернётесь в главное меню.")


# функция вывода тем выбранного пользователя
def user_number(update, context):
    global data_db, message_id

    context.user_data['user'] = update.message.text

    keyboard = [[InlineKeyboardButton('Выбрать другого пользователя', callback_data='return')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    db_sess = db_session.create_session()
 #   data_db = db_sess.query(Theme).all()
    data_db = db_sess.query(Theme).filter(Theme.user_id == context.user_data['user']).all()

    text = 'Вот список тем пользователя:'
    for pos in range(len(data_db)):
        text = text + f'\n{pos + 1}) {data_db[pos]}'

    update.message.reply_text(text)

    data_db = db_sess.query(Comment).filter(Comment.user_id == context.user_data['user']).all()

    text = 'Вот список комментариев пользователя:'
    for pos in range(len(data_db)):
        text = text + f'\n{pos + 1}) {data_db[pos]}'

    update.message.reply_text(text)

    update.message.reply_text('Введите номер пользователя:')

    return 5


# функция вывода списка категорий игр википедии
def start_category(update, context):
    global data_db, message_id

    query = update.callback_query
    logger.info("Waiting @%s's answer...", query.from_user.first_name)
    query.answer()
    logger.info("Got answer from @%s: '{}'.".format(query.data), query.from_user.first_name)

    keyboard = [[InlineKeyboardButton('Выбрать другую категорию', callback_data='return')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    cursor.execute("SELECT name FROM game WHERE id_category='{}'".format(query.data))
    data_db = cursor.fetchall()

    text = 'Вот список игр в категории {}'.format(categories[int(query.data)])
    for pos in range(len(data_db)):
        text = text + f'\n{pos + 1}) {data_db[pos][0].strip()}'
    text = text + f'\nНапишите в чат номер нужной игры или выберите другую категорию.'

    message_id = query.message.message_id

    query.bot.edit_message_text(text, chat_id=query.message.chat_id,
                                message_id=query.message.message_id,
                                reply_markup=reply_markup)

    logging.info("Edited @%s Message FIRST state.", query.from_user.first_name)
    return 2


# функция вывода информации по игре
def game_number(update, context):
    global data_db, message_id
    game_num = update.message.text
    logger.info("Got Message '{}' from @%s.".format(game_num), update.message.from_user.first_name)

    cursor.execute("SELECT name, text, image_url FROM game WHERE name=?", data_db[int(game_num) - 1])
    data_db = cursor.fetchall()[0]
    name, text, image_url = data_db

    output = f"{name}\nОписание:\n{text}\n"

    context.bot.delete_message(update.message.chat_id, message_id)
    logging.info("Deleted @%s Message SECOND state.", update.message.from_user.first_name)

  #  keyboard = [[InlineKeyboardButton('Назад', callback_data='back')]]
  #  reply_markup = InlineKeyboardMarkup(keyboard)

    text = '\n Чтобы вернутся в главное меню нажмите /enter'

    if image_url:
        #  Отправляем фото, если оно есть в базе данных
        context.bot.send_photo(update.message.chat_id, image_url, caption=output + text)
        logging.info("Sent to @%s a Photo FIRST state.", update.message.from_user.first_name)
    else:
        #  Отправляем сообщение, если фото нет в базе данных
        context.bot.send_message(update.message.chat_id, text=output + text)
        logging.info("Sent to @%s a Message FIRST state.", update.message.from_user.first_name)

   # return 2
    return ConversationHandler.END


# функция остановки бота
def stop(update, context):  # обработка выхода из диалога
    query = update.callback_query
    text = 'Остановка бота!'
    query.message.reply_text(text)
    logger.info("User %s stopped the conversation.", update.message.from_user.first_name)
    return ConversationHandler.END


# обработчик ошибок бота
def error(update, context):  # обработка ошибок
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    query = update.callback_query
    keyboard = [[InlineKeyboardButton('Вернуться назад', callback_data='error_return')]]
    markup = InlineKeyboardMarkup(keyboard)
    if query:
        query.edit_message_text('Ошибка в запросе. Повторите запрос', reply_markup=markup)
    else:
        update.message.reply_text('Ошибка в запросе. Повторите запрос', reply_markup=markup)
  # query.message.reply_text('Ошибка в запросе. Для возврата нажмите команду /enter или для остановки работы бота /stop', reply_markup=markup)


# функция обработки запроса поиска магазина
def geocoder(update, context):
    try:
        ll, spn = llspan(update.message.text)
       # toponym_lon, toponym_lat, spn = llspan(update.message.text)
       # ll = ",".join([toponym_lon, toponym_lat])
        toponym_lon, toponym_lat = ll.split(",")
        if ll and spn:
            organization = find_org(ll)
            point = organization["geometry"]["coordinates"]
            organization_lat = float(point[0])
            organization_lon = float(point[1])

            metka = f"{ll}~{organization_lat},{organization_lon},pm2dgl"
            static_api_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map&pt={metka}".format(**locals())
            context.bot.sendPhoto(update.message.chat.id,
                                  static_api_request,
                                  caption=update.message.text)

            name = organization["properties"]["CompanyMetaData"]["name"]
            address = organization["properties"]["CompanyMetaData"]["address"]
            time_work = organization["properties"]["CompanyMetaData"]["Hours"]["text"]
            url = organization["properties"]["CompanyMetaData"]["url"]
            distance = round(lonlat_distance((float(toponym_lat), float(toponym_lon)), (organization_lon, organization_lat)))

            snip = f"Название магазина:\t{name}\nАдрес магазина:\t{address}\nВремя работы магазина:\t{time_work}\nРасстояние до магазина:\t{distance}м.\nАдрес сайта магазина{url}"
            update.message.reply_text(str(snip))

        else:
            update.message.reply_text("По запросу результат отрицательный.")

    except (Exception, TelegramError):
            error(update, context)
  # except Exception as err:
  #         print(err)
  #         error(update, context)

            return 3
    return 3


# обработчик кубика
def dice(update, context):
    update.message.reply_text("Выберете какой кинуть кубик - 6 граней, 2 по 6, 20 или вернуться назад", reply_markup=dice_markup)
    return 4


# обработчик таймера
def timers(update, context):
    update.message.reply_text("Выберете время таймера - 30 сек., 1 мин., 5 мин. или вернуться назад", reply_markup=timer_markup)
    return 4


# обработчик кубика
def dice6(update, context):
    num = math.trunc(random.random() * 6) + 1
    update.message.reply_text("{0}".format(num), reply_markup=ReplyKeyboardRemove())
    return 1


# обработчик кубика
def dice2x6(update, context):
    num1 = math.trunc(random.random() * 6) + 1
    num2 = math.trunc(random.random() * 6) + 1
    update.message.reply_text("{0} {1}".format(num1, num2), reply_markup=ReplyKeyboardRemove())
    return 1


# обработчик кубика
def dice20(update, context):
    num = math.trunc(random.random() * 20) + 1
    update.message.reply_text("{0}".format(num), reply_markup=ReplyKeyboardRemove())
    return 1


# обработчик таймера
def timer30(update, context):
    begin_timer(update, context, 30)
    return 4


# обработчик таймера
def timer60(update, context):
    begin_timer(update, context, 60)
    return 4


# обработчик таймера
def timer300(update, context):
    begin_timer(update, context, 300)
    return 4


# обработчик таймера
def begin_timer(update, context, delay):
    job = context.job_queue.run_once(close_timer, delay, context=update.message.chat_id)
    context.chat_data['job'] = job
    update.message.reply_text('Засёк {0} секунд'.format(delay), reply_markup=close_markup)
    return 4


# обработчик таймера
def close_timer(context):
    job = context.job
    context.bot.send_message(job.context, text='Время истекло', reply_markup=timer_markup)
    return 4


# обработчик таймера
def unset_timer(update, context):
    if 'job' in context.chat_data:
        context.chat_data['job'].schedule_removal()
        del context.chat_data['job']
    update.message.reply_text('Хорошо, вернулся сейчас!', reply_markup=timer_markup)
    return 4

# основная функция программы
def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('enter', enter),
                      CommandHandler('start', start)],
        states={# словарь состояний разговора, возвращаемых callback функциями
            1: [CallbackQueryHandler(enter_query, pattern=r'return', pass_user_data=True),
                CallbackQueryHandler(enter_query, pattern=r'error_return', pass_user_data=True),
                CallbackQueryHandler(news, pattern='^' + str(ONE) + '$', pass_user_data=True),
                CallbackQueryHandler(forum, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(wiki, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(util, pattern='^' + str(FOUR) + '$'),
                CallbackQueryHandler(url, pattern='^' + str(FIVE) + '$'),
                CommandHandler('enter', enter_query),
                CommandHandler('stop', stop)
            ],
            2: [CommandHandler('stop', stop),
                CommandHandler('enter', enter_query),
                CallbackQueryHandler(wiki, pattern=r'return', pass_user_data=True),
                CallbackQueryHandler(enter_query, pattern=r'error_return', pass_user_data=True),
             #  CallbackQueryHandler(enter_query, pattern=r'back', pass_user_data=True),
                CallbackQueryHandler(start_category),
                MessageHandler(Filters.text, game_number)
            ],
            3: [CommandHandler('enter', enter_query),
                CallbackQueryHandler(url, pattern=r'return', pass_user_data=True),
                CallbackQueryHandler(enter_query, pattern=r'error_return', pass_user_data=True),
                CommandHandler('stop', stop, pass_user_data=True),
                MessageHandler(Filters.text & ~Filters.command, geocoder)
            ],
            4: [#CommandHandler('enter', enter_query),
                CommandHandler("return", util, pass_user_data=True),
                CallbackQueryHandler(enter_query, pattern=r'error_return', pass_user_data=True),
                CommandHandler('stop', stop, pass_user_data=True),
                CommandHandler("timer", timers),
                CommandHandler("dice", dice),
                CommandHandler("6", dice6),
                CommandHandler("2x6", dice2x6),
                CommandHandler("20", dice20),
                CommandHandler("30s", timer30, pass_job_queue=True, pass_chat_data=True),
                CommandHandler("1m", timer60, pass_job_queue=True, pass_chat_data=True),
                CommandHandler("5m", timer300, pass_job_queue=True, pass_chat_data=True),
                CommandHandler("close", unset_timer, pass_chat_data=True),
                ],
            5: [CommandHandler('stop', stop),
                CommandHandler('enter', enter_query),
                CallbackQueryHandler(enter_query, pattern=r'return', pass_user_data=True),
                CallbackQueryHandler(enter_query, pattern=r'error_return', pass_user_data=True),
                #  CallbackQueryHandler(enter_query, pattern=r'back', pass_user_data=True),
                #CallbackQueryHandler(start_category),
                MessageHandler(Filters.text, user_number, pass_user_data=True)
                ],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )
    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    print('Телега стартовала')
    updater.idle()


if __name__ == '__main__':
    main()
