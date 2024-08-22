# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /usr/src/app

# Копируем файл с зависимостями
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код бота в контейнер
COPY . .

# Делаем папку с базой данных доступной для чтения и записи
RUN mkdir -p /usr/src/app/data && chmod -R 777 /usr/src/app/data

# Указываем команду, которая будет выполняться при запуске контейнера
CMD [ "python", "./bot.py" ]