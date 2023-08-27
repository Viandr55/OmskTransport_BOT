import telebot
import sqlite3
from telebot import types
from config import Token, love, allowed_users

bot = telebot.TeleBot(Token())

#Функция проверки доступа пользователя
def check_access(user_id):
    return user_id in allowed_users()


#Стартовая функция
@bot.message_handler(commands=['start', 'help'])
def start(message):
    if not check_access(message.from_user.id):
        print("https://t.me/"+message.from_user.username)
        bot.send_message(message.chat.id, 'Unauthorized access')
        return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    add = types.KeyboardButton(text="/add")
    edit = types.KeyboardButton(text="/edit")
    delete = types.KeyboardButton(text="/delete")
    kb.add(add, edit, delete)
    bot.send_message(message.chat.id, f'Привет, <b>{message.from_user.full_name}</b> 👋\n\nНажми кнопочку внизу или введи гаражный номер', parse_mode='html', reply_markup=kb)
    print("https://t.me/"+message.from_user.username)

@bot.message_handler(commands=['i<3u'])
def ilu(message):
    if not check_access(message.from_user.id):
        bot.send_message(message.chat.id, 'Unauthorized access')
        return
    love()


#Функция поиска
@bot.message_handler(commands=['search'])
def gid_request(message):
    if not check_access(message.from_user.id):
        bot.send_message(message.chat.id, 'Unauthorized access')
        return
    bot.send_message(message.chat.id, 'Введи гаражный номер для поиска')
    bot.register_next_step_handler(message, search)

def search(message):
    connect = sqlite3.connect('ts.db')
    cursor = connect.cursor()
    gid = int(message.text)
    cursor.execute(f"SELECT EXISTS(SELECT * FROM bus_id where id = {int(gid)})")
    if cursor.fetchone()[0] == 0:
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Добавить запись", callback_data=f"add_{gid}")
        markup.add(button)
        bot.send_message(message.chat.id, f'Гаражного номера <b>{gid}</b> у меня пока нет', parse_mode='html', reply_markup=markup)
    else:
        cursor.execute(f"SELECT type, comment FROM bus_id WHERE id = {int(gid)}")
        entry = cursor.fetchone()
        gtype = entry[0]
        gcomment = entry[1]
        if gcomment is None:
            gcomment = ''
        markup = types.InlineKeyboardMarkup()
        edit = types.InlineKeyboardButton(text="Редактировать", callback_data=f"edit_{gid}")
        delete = types.InlineKeyboardButton(text="Удалить", callback_data=f"delete_{gid}")
        markup.add(edit, delete)
        bot.send_message(message.chat.id, f'<b>Гаражный номер:</b> {gid}\n<b>Тип:</b> {gtype}\n<b>Комментарий:</b> {gcomment}', parse_mode='html', reply_markup=markup)
        connect.commit()

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def handle_add_callback(call):
    gid = call.data.split("_")[1]
    add_type(call.message, gid)

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
def handle_edit_callback(call):
    gid = call.data.split("_")[1]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    select_entry_to_edit(call.message, gid)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def handle_delete_callback(call):
    gid = call.data.split("_")[1]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    confirm_delete(call.message, gid)


#Функция добавления записи
@bot.message_handler(commands=['add'])
def add(message):
    if not check_access(message.from_user.id):
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
        send_added_notification(gid, gtype, gcomment, message.from_user.username)
        show_added_entry(message, gid, gtype, gcomment)

def show_added_entry(message, gid, gtype, gcomment):
    bot.send_message(message.chat.id, f'Добавленная запись\n\n<b>Гаражный номер:</b> {gid}\n<b>Тип:</b> {gtype}\n<b>Комментарий:</b> {gcomment}', parse_mode='html')
    start(message)

def send_added_notification(gid, gtype, gcomment, username):
    notification_text = f"➕ Добавление записи ➕\n\n" \
                        f"Гаражный номер: {gid}\n" \
                        f"Тип: {gtype}\n" \
                        f"Комментарий: {gcomment}\n" \
                        f"Пользователь: @{username}"
    bot.send_message('-805417506', notification_text)


#Функция редактирования записи
@bot.message_handler(commands=['edit'])
def edit(message):
    if not check_access(message.from_user.id):
        bot.send_message(message.chat.id, 'Unauthorized access')
        return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    cancel = types.KeyboardButton(text="Отмена")
    kb.add(cancel)
    bot.send_message(message.chat.id, 'Введи гаражный номер для редактирования или нажми "Отмена"', reply_markup=kb)
    bot.register_next_step_handler(message, select_entry_to_edit)

def select_entry_to_edit(message, selected_id=None):
    try:
        if selected_id is None:
            selected_id = message.text.lower()
        else:
            selected_id = selected_id
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
                kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                picktype = types.KeyboardButton(text="Тип")
                pickcomment = types.KeyboardButton(text="Комментарий")
                cancel = types.KeyboardButton(text="Отмена")
                back = types.KeyboardButton(text="Назад")
                kb.add(picktype, back, pickcomment, cancel)
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
    elif selected_field == 'назад':
        edit(message)
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
    
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    back = types.KeyboardButton(text="Назад")
    cancel = types.KeyboardButton(text="Отмена")
    kb.add(back, cancel)
    if field_display_name == "Тип":
        bot.send_message(message.chat.id, f'Текущее значение типа: {current_value}\nВведи новое значение или нажми "Назад"', reply_markup=kb)
    else:
        bot.send_message(message.chat.id, f'Текущее значение комментария: <code>{current_value}</code>\nВведи новое значение или нажми "Назад"', parse_mode='html', reply_markup=kb)
    bot.register_next_step_handler(message, update_field, gid, field_name)

def update_field(message, gid, field_name):
    new_value = message.text
    if new_value.lower() == 'назад':
        select_entry_to_edit(message, gid)
    elif new_value.lower() == 'отмена':
        start(message)
    else:
        connect = sqlite3.connect('ts.db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT {field_name} FROM bus_id WHERE id = ?", (gid,))
        previous_value = cursor.fetchone()[0]
        cursor.execute(f"UPDATE bus_id SET {field_name} = ? WHERE id = ?", (new_value, gid))
        connect.commit()
        send_edit_notification(gid, field_name, previous_value, new_value, message.from_user.username)
        show_updated_entry(message, gid)
        start(message)

def show_updated_entry(message, gid):
    connect = sqlite3.connect('ts.db')
    cursor = connect.cursor()
    cursor.execute(f"SELECT type, comment FROM bus_id WHERE id = {gid}")
    entry = cursor.fetchone()
    updated_type = entry[0]
    updated_comment = entry[1]

    bot.send_message(message.chat.id, f'<b>Измененная запись</b>\n\n<b>Гаражный номер:</b> {gid}\n<b>Тип:</b> {updated_type}\n<b>Комментарий:</b> {updated_comment}', parse_mode='html')

def send_edit_notification(gid, field_name, previous_value, new_value, username):
    notification_text = f"🔧 Изменение записи 🔧\n\n" \
                        f"Гаражный номер: {gid}\n" \
                        f"Поле: {field_name}\n" \
                        f"Старое значение: {previous_value}\n" \
                        f"Новое значение: {new_value}\n" \
                        f"Пользователь: @{username}"
    bot.send_message('-805417506', notification_text)


#Функция удаления записи
@bot.message_handler(commands=['delete'])
def delete(message):
    if not check_access(message.from_user.id):
        bot.send_message(message.chat.id, 'Unauthorized access')
        return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    cancel = types.KeyboardButton(text="Отмена")
    kb.add(cancel)
    bot.send_message(message.chat.id, 'Введи гаражный номер для удаления или нажми "Отмена"', reply_markup=kb)
    bot.register_next_step_handler(message, confirm_delete)

def confirm_delete(message, selected_id=None):
    try:
        if message.text.lower() == 'отмена':
            start(message)
        else:
            if selected_id is None:
                selected_id = int(message.text)
            else:
                selected_id = selected_id
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
        send_deleted_notification(selected_id, selected_type, selected_comment, message.from_user.username)
        bot.send_message(message.chat.id, f'Удаленная запись\n\n<b>Гаражный номер:</b> {selected_id}\n<b>Тип:</b> {selected_type}\n<b>Комментарий:</b> {selected_comment} ', parse_mode='html')
        start(message)
    elif message.text.lower() == 'назад':
        delete(message)
    else:
        start(message)

def send_deleted_notification(gid, gtype, gcomment, username):
    notification_text = f"➖ Удаление записи ➖\n\n" \
                        f"Гаражный номер: {gid}\n" \
                        f"Тип: {gtype}\n" \
                        f"Комментарий: {gcomment}\n" \
                        f"Пользователь: @{username}"
    bot.send_message('-805417506', notification_text)


#Функция вывода id пользователя
@bot.message_handler(commands=['id'])
def print_user_id(message):
    bot.send_message(message.chat.id, f'Твой ID пользователя: <code>{message.from_user.id}</code>', parse_mode='html')


#Функция распознавания введённого текста
@bot.message_handler(content_types=['text'])
def text(message):
    if not check_access(message.from_user.id):
        bot.send_message(message.chat.id, 'Unauthorized access')
        return
    if message.text.isdigit():
        search(message)
    else:
        bot.send_message(message.chat.id, 'Я не знаю что ты ввел')
        start(message)


def main():
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print("Error:", e)
            bot.stop_polling()
            
if __name__ == "__main__":
    main()