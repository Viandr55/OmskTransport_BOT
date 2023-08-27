import telebot
import sqlite3
from telebot import types
from config import Token
from config import love
from config import allowed_users

bot = telebot.TeleBot(Token())
while True:
    try:
        #Стартовая функция
        @bot.message_handler(commands=['start', 'help'])
        def start(message):
            if message.from_user.id not in allowed_users():
               bot.send_message(message.chat.id, 'Unauthorized access')
               return
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            add = types.KeyboardButton(text="/add")
            edit = types.KeyboardButton(text="/edit")
            delete = types.KeyboardButton(text="/delete")
            kb.add(add, edit, delete)
            bot.send_message(message.chat.id, f'Привет, <b>{message.from_user.full_name}</b> 👋\n\nНажми кнопку внизу или введи гаражный номер', parse_mode='html', reply_markup=kb)
            print(message.chat.id)


        @bot.message_handler(commands=['i<3u'])
        def ilu(message):
            if message.from_user.id not in allowed_users():
               bot.send_message(message.chat.id, 'Unauthorized access')
               return
            love()

        #Функция поиска
        @bot.message_handler(commands=['search'])
        def gid_request(message):
            bot.send_message(message.chat.id, 'Введи гаражный номер для поиска')
            bot.register_next_step_handler(message, search)

        def search(message):
            connect = sqlite3.connect('ts.db')
            cursor = connect.cursor()
            gid = int(message.text)
            cursor.execute(f"SELECT EXISTS(SELECT * FROM bus_id where id = {int(gid)})")
            if cursor.fetchone()[0] == 0:
                bot.send_message(message.chat.id, f'Гаражного номера <b>{gid}</b> у меня пока нет', parse_mode='html')
                start(message)
            else:
                cursor.execute(f"SELECT type, comment FROM bus_id WHERE id = {int(gid)}")
                entry = cursor.fetchone()
                gtype = entry[0]
                gcomment = entry[1]

                if gtype is None:
                    gtype = ''
                if gcomment is None:
                    gcomment = ''
                
                bot.send_message(message.chat.id, f'<b>Гаражный номер:</b> {gid}\n<b>Тип:</b> {gtype}\n<b>Комментарий:</b> {gcomment}', parse_mode='html')
                connect.commit()

        #Функция добавления записи
        @bot.message_handler(commands=['add'])
        def add(message):
            if message.from_user.id not in allowed_users():
                bot.send_message(message.chat.id, 'Unauthorized access')
                return
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            cancel = types.KeyboardButton(text="Отмена")
            kb.add(cancel)
            bot.send_message(message.chat.id, 'Введи гаражный номер для добавления', reply_markup=kb)
            bot.register_next_step_handler(message, add_type)

        def add_type(message, gid=None):
            if gid is None:
                if message.text.lower() == 'отмена':
                    start(message)
                    return
                if message.text.isdigit():
                    gid = int(message.text)
                    connect = sqlite3.connect('ts.db')
                    cursor = connect.cursor()
                    cursor.execute(f"SELECT EXISTS(SELECT * FROM bus_id where id = {gid})")
                    if cursor.fetchone()[0] == 1:
                        cursor.execute(f"SELECT type, comment FROM bus_id WHERE id = {gid}")
                        entry = cursor.fetchone()
                        gtype = entry[0]
                        gcomment = entry[1]
                        bot.send_message(message.chat.id, f'Гаражный номер <b>{gid}</b> уже есть в БД\n\n<b>Гаражный номер:</b> {gid}\n<b>Тип:</b> {gtype}\n<b>Комментарий:</b> {gcomment}', parse_mode='html')
                        start(message)
                        return
                    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                    back = types.KeyboardButton(text="Назад")
                    cancel = types.KeyboardButton(text="Отмена")
                    kb.add(back, cancel)
                    bot.send_message(message.chat.id, f'<b>Гаражный номер:</b> {gid}\n\nВведи тип', parse_mode='html', reply_markup=kb)
                    bot.register_next_step_handler(message, add_comment, gid=gid)
                else:
                    bot.send_message(message.chat.id, 'Некорректный гаражный номер')
                    add(message)
            else:
                kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                back = types.KeyboardButton(text="Назад")
                cancel = types.KeyboardButton(text="Отмена")
                kb.add(back, cancel)
                bot.send_message(message.chat.id, f'<b>Гаражный номер:</b> {gid}\n\nВведи тип', parse_mode='html', reply_markup=kb)
                bot.register_next_step_handler(message, add_comment, gid=gid)

        def add_comment(message, gid):
            if message.text.lower() == 'назад':
                add(message)
            elif message.text.lower() == 'отмена':
                start(message)
            else:
                gtype = message.text
                kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                back = types.KeyboardButton(text="Назад")
                skip = types.KeyboardButton(text="Пропустить")
                cancel = types.KeyboardButton(text="Отмена")
                kb.add(skip, back, cancel)
                bot.send_message(message.chat.id, f'<b>Гаражный номер:</b> {gid}\n<b>Тип:</b> {gtype}\n\nВведи комментарий или нажми "Пропустить"', parse_mode='html', reply_markup=kb)
                bot.register_next_step_handler(message, save_entry, gid=gid, gtype=gtype)

        def save_entry(message, gid, gtype):
            if message.text.lower() == 'назад':
                add_type(message, gid)
            elif message.text.lower() == 'отмена':
                start(message)
            else:
                gcomment = message.text
                if message.text.lower() == 'пропустить':
                    gcomment = ''
                connect = sqlite3.connect('ts.db')
                cursor = connect.cursor()
                cursor.execute("INSERT INTO bus_id VALUES (?, ?, ?)", (gid, gtype, gcomment))
                connect.commit()
                bot.send_message('-805417506', f'Добавлена запись: {gid}; {gtype}; {gcomment}\n@{message.from_user.username}')
                show_added_entry(message, gid, gtype, gcomment)

        def show_added_entry(message, gid, gtype, gcomment):
            bot.send_message(message.chat.id, f'Запись успешно добавлена\n\n<b>Гаражный номер:</b> {gid}\n<b>Тип:</b> {gtype}\n<b>Комментарий:</b> {gcomment}', parse_mode='html')
            start(message)

        #Функция редактирования записи
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

        #Функция удаления записи
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

        #Функция вывода id пользователя
        @bot.message_handler(commands=['id'])
        def print_user_id(message):
            bot.send_message(message.chat.id, f'{message.from_user.id}')

        #Функция распознавания введённого текста
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