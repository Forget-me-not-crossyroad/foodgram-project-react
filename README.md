![example branch parameter](https://github.com/Forget-me-not-crossyroad/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master)

# **_Foodgram_**
Foodgram (Фудграм) — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создать список продуктов, которые нужно купить для приготовления выбранных блюд

### _Развернуть проект на удаленном сервере:_

**_Клонировать репозиторий:_**
```
git clone https://github.com/Forget-me-not-crossyroad/foodgram-project-react.git
```

**_Подготовка сервера к деплою:_**
```
1. npm cache clean --force                              - очиститка кеша npm
2. sudo apt clean                                       - очиститка кеша apt
3. sudo journalctl --vacuum-time=1d                     - удаление старых логов
```

**_Установка на сервер Docker, Docker Compose:_**
```
sudo apt update                                         - обновить apt
sudo apt install curl                                   - установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      - скачать скрипт для установки docker
sh get-docker.sh                                        - запуск скрипта для установки docker
sudo apt-get install docker-compose-plugin              - установка последней версии docker compose
```
**_Использовать утилиту SCP (secure copy) для копирования
на сервер файлов docker-compose.yml, nginx.conf из папки
infra (команды выполнять находясь в папке infra):_**
```
scp docker-compose.yml nginx.conf username@IP:/home/username/

# username - имя пользователя на сервере
# IP - публичный IP сервера
```

**_Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:_**
```
# Ключи для работы с сервером и DockerHub
SECRET_KEY              - секретный ключ Django-проекта
DOCKER_PASSWORD         - пароль от DockerHub
DOCKER_USERNAME         - логин DockerHub
HOST                    - публичный IP сервера
USER                    - имя пользователя сервера
PASSPHRASE              - пароль для ssh-key для подключения к серверу
SSH_KEY                 - приватный ssh-ключ
#Ключи для работы с телеграм-аккаунтом
TELEGRAM_TO             - ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          - токен бота, отправляющего сообщение
# Ключи подключения к БД postgres
DB_ENGINE               - django.db.backends.postgresql
POSTGRES_DB             - django
POSTGRES_USER           - django_user
POSTGRES_PASSWORD       - mysecretpassword
DB_HOST                 - db
DB_PORT                 - 5432 (порт по умолчанию)
```

**_Создать и запустить контейнеры Docker, выполнить команду на сервере
(версии команд "docker compose" или "docker-compose" отличаются в
зависимости от установленной версии Docker Compose):**_
```
sudo docker compose up -d
```
**_Выполнить миграции (следует выполнять только при
отладке, т.к. команда уже содержится в main.yml):_**
```
sudo docker compose exec backend python manage.py migrate
```
**_Собрать статику (следует выполнять только при
отладке, т.к. команда уже содержится в main.yml):_**
```
sudo docker compose exec backend python manage.py collectstatic --noinput
```
**_Создать суперпользователя (выполнять в директории сервера,
в которой содержится docker-compose.yml):_**
```
sudo docker compose exec backend python manage.py createsuperuser
```
**_Для остановки контейнеров Docker:_**
```
sudo docker compose down -v      - с их удалением
sudo docker compose stop         - без удаления
sudo docker system prune -af     - удаление всех лишних объектов
```
### После каждого push в ветку master будет происходить:

1. Сборка и доставка докер-образов frontend и backend на DockerHub
2. Pull (загрузка) образов на сервер
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram в случае успешного деплоя

### Локальный запуск проекта:

**_Склонировать репозиторий к себе_**
```
https://github.com/Forget-me-not-crossyroad/foodgram-project-react.git
```

**_Шаблон заполнения env:_**
```
# Переменные для database
SECRET_KEY=django-insecure-**************************************************
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=localhost
DB_PORT=5432
# Переменные для allowed_hosts, debug, test
DEBUG_MODE=True
ALLOWED_HOSTS='127.0.0.1 0.0.0.0 localhost app-yourappsname.3utilities.com 158.***.**.**'
```

**_Создать и запустить контейнеры Docker, как указано выше._**

**_После запуска проект будут доступен по адресу: http://127.0.0.1:8000/_**

**_Документация будет доступна по адресу: http://127.0.0.1:8000/swagger/_**

**_Для поключения локального фронтенда:_**
1. Перейти в директорию фронтенд
```
cd /frontend/
```
2. Установить зависимости
```
npm i
```
3. Запустить фронтенд
```
npm start
```
4. При возникновении проблем при установке зависимостей
следует изменить версию npm с помощью утилиты nvm,
подробнее:
https://leodev.ru/blog/node-js/%D0%BC%D0%B5%D0%BD%D0%B5%D0%B4%D0%B6%D0%B5%D1%80-%D0%B2%D0%B5%D1%80%D1%81%D0%B8%D0%B9-node-js-%D0%B8-npm/
`Python` `Django` `Django Rest Framework` `Docker` `Gunicorn` `NGINX` `PostgreSQL` `Yandex Cloud` `Continuous Integration` `Continuous Deployment`
