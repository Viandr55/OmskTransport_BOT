import telebot
import sqlite3
from telebot import types
from config import Token

bot = telebot.TeleBot(Token())
while True:
    try:
        @bot.message_handler(commands=['start'])
        def start(message):
            bot.send_message(message.chat.id, f'Привет, <b>{message.from_user.full_name}</b>\nВведи /search <em>гаражный_номер</em> или /поиск <em>гаражный_номер</em> для поиска', parse_mode='html')
            print(message.chat.id)

        @bot.message_handler(commands=['i<3u'])
        def love(message):
            bot.send_message(400436524, "Котик очень сильно любит своего воробушка")

        #@bot.message_handler(content_types=['text'])

        @bot.message_handler(commands=['search', 'поиск'])
        def search(message):
            connect = sqlite3.connect('ts.db')
            cursor = connect.cursor()
            sp = message.text.split(' ')
            poisk = sp[-1]
            if poisk == '/search' or poisk == '/поиск':
                bot.send_message(message.chat.id, 'Введи /search <em>гаражный_номер</em> или /поиск <em>гаражный_номер</em> для поиска', parse_mode='html')
            cursor.execute(f"SELECT EXISTS(SELECT * FROM bus_id where id = {int(poisk)})")
            if cursor.fetchone()[0] == 0:
                bot.send_message(message.chat.id, f'Гаражного номера <b>{poisk}</b> у меня пока нет', parse_mode='html')
            else:
                pls = cursor.execute(f"SELECT type, comment FROM bus_id WHERE id = {int(poisk)}")
                tip = pls.fetchall()[0][0]
                pls = cursor.execute(f"SELECT type, comment FROM bus_id WHERE id = {int(poisk)}")
                comm = pls.fetchall()[0][1]

                if tip == None:
                    tip = ''
                if comm == None:
                    comm = ''
                
                bot.send_message(message.chat.id, f'<b>Гаражный номер:</b> {poisk}\n<b>Тип:</b> {tip}\n<b>Комментарий:</b> {comm}', parse_mode='html')
                connect.commit()

        
        bot.polling(none_stop=True, interval=0)
    except:
        bot.stop_polling()

