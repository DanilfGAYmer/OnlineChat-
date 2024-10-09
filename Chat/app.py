from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import bcrypt
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Хранение пользователей (для демонстрации, в памяти)
users = {}
online_users = []  # Список для отслеживания пользователей онлайн

# Файл для хранения истории чата
CHAT_HISTORY_FILE = "chat_history.txt"

# Функция для загрузки истории чата из файла
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as file:
            return file.readlines()
    return []

# Функция для сохранения нового сообщения в файл
def save_message_to_history(message):
    with open(CHAT_HISTORY_FILE, 'a', encoding='utf-8') as file:
        file.write(message + '\n')

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Обработка регистрации
@socketio.on('register')
def handle_register(data):
    username = data['username']
    password = data['password'].encode('utf-8')

    if username in users:
        emit('login_error', 'Пользователь с таким логином уже существует!')
    else:
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        users[username] = hashed_password
        emit('login_success', username)

# Обработка входа
@socketio.on('login')
def handle_login(data):
    username = data['username']
    password = data['password'].encode('utf-8')

    if username in users:
        if bcrypt.checkpw(password, users[username]):
            emit('login_success', username)

            # Отправляем историю чата после успешного входа
            chat_history = load_chat_history()
            emit('chat_history', chat_history)

            # Добавляем пользователя в список онлайн и уведомляем о его подключении
            online_users.append(username)
            send(f'{username} присоединился к чату.', broadcast=True)
        else:
            emit('login_error', 'Неверный пароль!')
    else:
        emit('login_error', 'Пользователь не найден!')

# Обработка отключения пользователя
@socketio.on('disconnect')
def handle_disconnect():
    for user in online_users:
        online_users.remove(user)
        send(f'{user} покинул чат.', broadcast=True)

# Обработка сообщений чата
@socketio.on('message')
def handle_message(msg):
    print(f'Новое сообщение: {msg}')
    send(msg, broadcast=True)

    # Сохраняем сообщение в файл
    save_message_to_history(msg)

# Запуск сервера
if __name__ == '__main__':
    socketio.run(app, host='26.110.7.44', port=1488)

