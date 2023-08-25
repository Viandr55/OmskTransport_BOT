import telebot
import sqlite3
from telebot import types
from config import Token
from config import love
from config import allowed_users

bot = telebot.TeleBot(Token())
while True:
    try:
        @bot.message_handler(commands=['start', 'help'])
        def start(message):
            if message.from_user.id not in allowed_users():
               bot.send_message(message.chat.id, 'Unauthorized access')
               return
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            btn1 = types.KeyboardButton(text="/add")
            btn2 = types.KeyboardButton(text="/edit")
            btn3 = types.KeyboardButton(text="/delete")
            kb.add(btn1, btn2, btn3)
            bot.send_message(message.chat.id, f'Привет, <b>{message.from_user.full_name}</b> 👋\n\nНажми кнопку внизу или введи гаражный номер', parse_mode='html', reply_markup=kb)
            print(message.chat.id)

        @bot.message_handler(commands=['i<3u'])
        def ilu(message):
            if message.from_user.id not in allowed_users():
               bot.send_message(message.chat.id, 'Unauthorized access')
               return
            love()

        
        @bot.message_handler(commands=['search'])
        def gid_request(message):
            bot.send_message(message.chat.id, 'Введи гаражный номер для поиска')
            bot.register_next_step_handler(message, search)

        def search(message):
            connect = sqlite3.connect('ts.db')
            cursor = connect.cursor()
            poisk = int(message.text)
            cursor.execute(f"SELECT EXISTS(SELECT * FROM bus_id where id = {int(poisk)})")
            if cursor.fetchone()[0] == 0:
                bot.send_message(message.chat.id, f'Гаражного номера <b>{poisk}</b> у меня пока нет', parse_mode='html')
                start(message)
            else:
                pls = cursor.execute(f"SELECT type, comment FROM bus_id WHERE id = {int(poisk)}")
                tip = pls.fetchall()[0][0]
                pls = cursor.execute(f"SELECT type, comment FROM bus_id WHERE id = {int(poisk)}")
                comm = pls.fetchall()[0][1]

                if tip is None:
                    tip = ''
                if comm is None:
                    comm = ''
                
                bot.send_message(message.chat.id, f'<b>Гаражный номер:</b> {poisk}\n<b>Тип:</b> {tip}\n<b>Комментарий:</b> {comm}', parse_mode='html')
                connect.commit()

        @bot.message_handler(commands=['add'])
        def add(message):
            if message.from_user.id not in allowed_users():
               bot.send_message(message.chat.id, 'Unauthorized access')
               return
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            cancel = types.KeyboardButton(text="Отмена")
            kb.add(cancel)
            bot.send_message(message.chat.id, f'Через пробел введи гаражный номер, тип и комментарий\n\nПример: 666 Лиаз Какой-нибудь комментарий', parse_mode='html', reply_markup=kb)
            bot.register_next_step_handler(message, check_gid)
        
        def check_gid(message):
            added_id = message.text.lower()
            if added_id == 'отмена':
                start(message)
            else:
                sp = message.text.split(' ')
                if sp[0].isdigit():
                    gid = int(sp[0])
                    if len(sp) >= 2:
                        gtype = sp[1]
                    else: 
                        bot.send_message(message.chat.id, 'Без типа создать запись нельзя\n\nВведи /add для добавления новой записи')
                        start(message)
                    if len(sp) >= 3:
                        gcomment = ' '.join(sp[2:])
                    else:
                        gcomment = ''
                    connect = sqlite3.connect('ts.db')
                    cursor = connect.cursor()
                    cursor.execute(f"SELECT EXISTS(SELECT * FROM bus_id where id = {gid})")
                    if cursor.fetchone()[0] == 1:
                        bot.send_message(message.chat.id, f'Гаражный номер <b>{gid}</b> уже есть в БД', parse_mode='html')
                        start(message)
                    else:
                        sp = (gid, gtype, gcomment)
                        cursor.execute(f"INSERT INTO bus_id VALUES (?, ?, ?)", sp)
                        connect.commit()
                        bot.send_message('-805417506', f'Добавлена запись: {gid}; {gtype}; {gcomment}\n@{message.from_user.username}')
                        show_added_entry(message, gid, gtype, gcomment)
                else:
                    bot.send_message(message.chat.id, f'Ты ввёл некорректный гаражный номер')
                    start(message)

        def show_added_entry(message, gid, gtype, gcomment):
            bot.send_message(message.chat.id, f'<b>Добавленная запись</b>\n\n<b>Гаражный номер:</b> {gid}\n<b>Тип:</b> {gtype}\n<b>Комментарий:</b> {gcomment}', parse_mode='html')
            start(message)

        @bot.message_handler(commands=['edit'])
        def edit(message):
            if message.from_user.id not in allowed_users():
               bot.send_message(message.chat.id, 'Unauthorized access')
               return
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            cancel = types.KeyboardButton(text="Отмена")
            kb.add(cancel)
            bot.send_message(message.chat.id, 'Введи гаражный номер для редактирования или нажми "Отмена"', reply_markup=kb)
            bot.register_next_step_handler(message, select_entry_to_edit)

        def select_entry_to_edit(message):
            try:
                selected_id = message.text.lower()
                if selected_id == 'отмена':
                    start(message)
                else:
                    connect = sqlite3.connect('ts.db')
                    cursor = connect.cursor()
                    cursor.execute(f"SELECT * FROM bus_id where id = {selected_id}")
                    entry = cursor.fetchone()
                    if not entry:
                        bot.send_message(message.chat.id, f'Гаражного номера <b>{selected_id}</b> у меня пока нет', parse_mode='html')
                        start(message)
                    else:
                        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                        btn1 = types.KeyboardButton(text="Тип")
                        btn2 = types.KeyboardButton(text="Комментарий")
                        btn3 = types.KeyboardButton(text="Отмена")
                        kb.add(btn1, btn2, btn3)
                        selected_type = entry[1]
                        selected_comment = entry[2]
                        bot.send_message(message.chat.id, f'Выбери поле для редактирования\n\n<b>Гаражный номер:</b> {selected_id}\n<b>Тип:</b> {selected_type}\n<b>Комментарий:</b> {selected_comment}', parse_mode='html', reply_markup=kb)
                        bot.register_next_step_handler(message, edit_field, selected_id)
            except ValueError:
                bot.send_message(message.chat.id, 'Некорректный гаражный номер\nПопробуй снова')

        def edit_field(message, gid):
            selected_field = message.text.lower()

            if selected_field == 'отмена':
                start(message)
            elif selected_field == 'тип':
                show_current_value_and_request_new_value(message, gid, 'type', 'Тип')
            elif selected_field == 'комментарий':
                show_current_value_and_request_new_value(message, gid, 'comment', 'Комментарий')
            else:
                bot.send_message(message.chat.id, 'Выбор некорректный\nПопробуй снова')

        def show_current_value_and_request_new_value(message, gid, field_name, field_display_name):
            connect = sqlite3.connect('ts.db')
            cursor = connect.cursor()
            cursor.execute(f"SELECT {field_name} FROM bus_id WHERE id = {gid}")
            current_value = cursor.fetchone()[0]
            
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(text="Назад")
            kb.add(btn1)
            if field_display_name == "Тип":
                bot.send_message(message.chat.id, f'Текущее значение типа: {current_value}\nВведи новое значение или нажми "Назад"', reply_markup=kb)
            else:
                bot.send_message(message.chat.id, f'Текущее значение комментария: <code>{current_value}</code>\nВведи новое значение или нажми "Назад"', parse_mode='html', reply_markup=kb)
            bot.register_next_step_handler(message, update_field, gid, field_name)

        def update_field(message, gid, field_name):
            new_value = message.text

            if new_value.lower() == 'назад':
                kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                btn1 = types.KeyboardButton(text="Тип")
                btn2 = types.KeyboardButton(text="Комментарий")
                btn3 = types.KeyboardButton(text="Отмена")
                kb.add(btn1, btn2, btn3)
                bot.send_message(message.chat.id, 'Выбери поле для редактирования', reply_markup=kb)
                bot.register_next_step_handler(message, edit_field, gid)
            else:
                connect = sqlite3.connect('ts.db')
                cursor = connect.cursor()
                cursor.execute(f"UPDATE bus_id SET {field_name} = ? WHERE id = ?", (new_value, gid))
                connect.commit()
                show_updated_entry(message, gid)
                start(message)

        def show_updated_entry(message, gid):
            connect = sqlite3.connect('ts.db')
            cursor = connect.cursor()
            cursor.execute(f"SELECT type, comment FROM bus_id WHERE id = {gid}")
            entry = cursor.fetchone()
            updated_type = entry[0]
            updated_comment = entry[1]

            bot.send_message(message.chat.id, f'<b>Обновленная запись</b>\n\n<b>Гаражный номер:</b> {gid}\n<b>Тип:</b> {updated_type}\n<b>Комментарий:</b> {updated_comment}', parse_mode='html')


        @bot.message_handler(commands=['delete'])
        def delete(message):
            if message.from_user.id not in allowed_users():
                bot.send_message(message.chat.id, 'Unauthorized access')
                return
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            cancel = types.KeyboardButton(text="Отмена")
            kb.add(cancel)
            bot.send_message(message.chat.id, 'Введи гаражный номер для удаления или нажми "Отмена"', reply_markup=kb)
            bot.register_next_step_handler(message, confirm_delete)

        def confirm_delete(message):
            try:
                if message.text.lower() == 'отмена':
                    start(message)
                else:
                    selected_id = int(message.text)
                    connect = sqlite3.connect('ts.db')
                    cursor = connect.cursor()
                    cursor.execute(f"SELECT * FROM bus_id where id = {selected_id}")
                    entry = cursor.fetchone()
                    if not entry:
                        bot.send_message(message.chat.id, f'Гаражного номера <b>{selected_id}</b> у меня пока нет', parse_mode='html')
                        start(message)
                    else:
                        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                        confirm_btn = types.KeyboardButton(text="Удалить")
                        back_btn = types.KeyboardButton(text="Назад")
                        cancel_btn = types.KeyboardButton(text="Отмена")
                        kb.add(confirm_btn, back_btn, cancel_btn)
                        selected_type = entry[1]
                        selected_comment = entry[2]
                        bot.send_message(message.chat.id, f'Точно хочешь удалить запись?\n\n<b>Гаражный номер:</b> {selected_id}\n<b>Тип:</b> {selected_type}\n<b>Комментарий:</b> {selected_comment}', parse_mode='html', reply_markup=kb)
                        bot.register_next_step_handler(message, execute_delete, selected_id)
            except ValueError:
                bot.send_message(message.chat.id, 'Некорректный гаражный номер')

        def execute_delete(message, selected_id):
            if message.text.lower() == 'удалить':
                connect = sqlite3.connect('ts.db')
                cursor = connect.cursor()
                cursor.execute(f"SELECT type, comment FROM bus_id WHERE id = {selected_id}")
                entry = cursor.fetchone()
                selected_type = entry[0]
                selected_comment = entry[1]

                cursor.execute(f"DELETE FROM bus_id WHERE id = ?", (selected_id,))
                connect.commit()
                bot.send_message('-805417506', f'Удалена запись: {selected_id}; {selected_type}; {selected_comment}\n@{message.from_user.username}')
                bot.send_message(message.chat.id, f'Гаражный номер <b>{selected_id}</b> успешно удален', parse_mode='html')
                start(message)
            elif message.text.lower() == 'назад':
                delete(message)
            else:
                start(message)


        @bot.message_handler(commands=['id'])
        def print_user_id(message):
            bot.send_message(message.chat.id, f'{message.from_user.id}')

        @bot.message_handler(content_types=['text'])
        def text(message):
            if message.from_user.id not in allowed_users():
               bot.send_message(message.chat.id, 'Unauthorized access')
               return
            if message.text.isdigit():
                search(message)
            else:
                bot.send_message(message.chat.id, 'Я не знаю что ты ввел')
                start(message)

        
        bot.polling(none_stop=True, interval=0)
    except:
        bot.stop_polling()
