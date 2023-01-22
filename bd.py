import telebot
import sqlite3
from telebot import types
from config import Token
from config import love

bot = telebot.TeleBot(Token())
while True:
    try:
        @bot.message_handler(commands=['start', 'help'])
        def start(message):
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(text="/add")
            btn2 = types.KeyboardButton(text="🚫/edit🚫")
            kb.add(btn1, btn2)
            bot.send_message(message.chat.id, f'Привет, <b>{message.from_user.full_name}</b>\nНажми на кнопку внизу или введи гаражный номер', parse_mode='html', reply_markup=kb)
            print(message.chat.id)

        @bot.message_handler(commands=['i<3u'])
        def ilu(message):
            love()

        @bot.message_handler(commands=['search', 'поиск'])
        def gid_request(message):
            gid_req = bot.reply_to(message, 'Введи гаражный номер')
            bot.register_next_step_handler(gid_req, search)

        def search(message):
            connect = sqlite3.connect('ts.db')
            cursor = connect.cursor()
            poisk = int(message.text)
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

        @bot.message_handler(commands=['add', 'добавить'])
        def add(message):
            gid_req = bot.reply_to(message, f'Через пробел введи гаражный номер, тип и комментарий\n(666 Лиаз Какой-нибудь комментарий)')
            bot.register_next_step_handler(gid_req, check_gid)
        
        def check_gid(message):
            sp = message.text.split(' ')
            if sp[0].isdigit():
                gid = int(sp[0])
                if len(sp) >= 2:
                    gtype = sp[1]
                else: 
                    bot.send_message(message.chat.id, 'Без типа создать запись нельзя.\nВведи /add для добавления новой записи')
                    pass
                if len(sp) >= 3:
                    gcomment = ' '.join(sp[2:])
                else:
                    gcomment = ''
                connect = sqlite3.connect('ts.db')
                cursor = connect.cursor()
                cursor.execute(f"SELECT EXISTS(SELECT * FROM bus_id where id = {gid})")
                if cursor.fetchone()[0] == 1:
                    bot.send_message(message.chat.id, f'Гаражный номер <b>{gid}</b> уже есть в БД.\nВведи /add для добавления новой записи', parse_mode='html')
                else:
                    sp = (gid, gtype, gcomment)
                    cursor.execute(f"INSERT INTO bus_id VALUES (?, ?, ?)", sp)
                    connect.commit()
                    bot.send_message(message.chat.id, f'Гаражный номер <b>{gid}</b> успешно добавлен\nДля проверки введи {gid}', parse_mode='html')
                    bot.send_message('-805417506', f'Добавлена запись: {gid}; {gtype}; {gcomment}')
            else:
                bot.send_message(message.chat.id, f'Ты ввёл некорректный гаражный номер.\nВведи /add для добавления новой записи')

        @bot.message_handler(commands=['edit'])
        def edit(message):
            bot.send_message(message.chat.id, 'Функция редактирования ещё в разработке')

        @bot.message_handler(content_types=['text'])
        def text(message):
            if message.text.isdigit():
                search(message)
            else:
                bot.send_message(message.chat.id, 'Я не знаю что ты ввёл')

        
        bot.polling(none_stop=True, interval=0)
    except:
        bot.stop_polling()