# Every Day Recipe
![example workflow](https://github.com/devbkd/every_day_recipe/actions/workflows/main.yml/badge.svg)
 
### Описание
Every Day Recipe - социальная сеть для обмена рецептами. В котором можно зарегистрироватся и добавлять свой рецепты, смотреть рецепты дргуих пользователей, подписываться на пользователей, скачать список ингридиентов и т.д.   

### Используемые технологии
- Python 3.11
- Django 4.2
- Django REST Framework 3.14
- PostgreSQL 15.2
- Node.js
- React
- Gunicorn
- Nginx
- Docker
- GitHub Actions

### Как развернуть проект локально
1. Клонировать репозиторий:
    ```bash
    git clone git@github.com:devbkd/every_day_recipe.git
    cd foodgram/
    ```

2. Создать в папке foodgram/ файл `.env` с переменными окружения (см. [.env.example](.env.example)).

3. Собрать и запустить докер-контейнеры через Docker Compose:
    ```bash
    docker compose up --build
    ```
### Как развернуть проект на сервере
1. Создать папку foodgram/ с файлом `.env` в домашней директории сервера (см. [.env.example](.env.example)).
    ```bash
    cd ~
    mkdir foodgram
    nano foodgram/.env
    ```
2. Настроить в nginx перенаправление запросов на порт 10000:
    ```nginx
    server {
        server_name <указываем домен>;
        server_tokens off;

        location / {
            proxy_pass http://127.0.0.1:10000;
        }
    }
    ```
3. Добавить в GitHub Actions следующие секреты:
- DOCKER_USERNAME - логин от Docker Hub
- DOCKER_PASSWORD - пароль от Docker Hub
- SSH_KEY - закрытый ssh-ключ для подключения к серверу
- SSH_PASSPHRASE - passphrase от этого ключа
- USER - имя пользователя на сервере
- HOST - IP-адрес сервера
- TELEGRAM_TO - ID телеграм-аккаунта для оповещения об успешном деплое
- TELEGRAM_TOKEN - токен телеграм-бота

Развернутый проект можно посмотреть: 
[Every Day Recipe](https://recipes.sytes.net/)
## Автор:
Рузал Закиров [GitHub](https://github.com/devbkd/)
