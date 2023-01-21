import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot("")
while True:
    try:
        @bot.message_handler(commands=['start'])
        def start(message):
            bot.send_message(message.chat.id, f'Добро пожаловать, {message.from_user.full_name}!\nВведи гаражный номер')
            print(message.chat.id)

        @bot.message_handler(commands=['stopanulsya'])
        def stop(message):
            exit()

        @bot.message_handler(func=lambda message: int(message.text) >= 1 and int(message.text) <= 9999)
        def search(message):
            connect = sqlite3.connect('ts.db')
            cursor = connect.cursor()
            cursor.execute(f"SELECT EXISTS(SELECT * FROM bus_id where id = {int(message.text)})")
            if cursor.fetchone()[0] == 0:
                bot.send_message(message.chat.id, f'Гаражного номера {message.text} у меня пока нет')
            else:
                pls = cursor.execute(f"SELECT type, comment FROM bus_id WHERE id = {int(message.text)}")
                tip = pls.fetchall()[0][0]
                pls = cursor.execute(f"SELECT type, comment FROM bus_id WHERE id = {int(message.text)}")
                comm = pls.fetchall()[0][1]

                if tip == None:
                    tip = ''
                if comm == None:
                    comm = ''
                
                bot.send_message(message.chat.id, f'Гаражный номер: {message.text}\nТип: {tip}\nКомментарий: {comm}')
                connect.commit()

        
        bot.polling(none_stop=True, interval=0)
    except:
        bot.stop_polling()

