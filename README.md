
# Проект YaMDb
api yamdb

![example workflow](https://github.com/timik2t/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

## Разработчики:
- [Куллина Наталья](https://github.com/Kullina-Nataly)
- [Исхаков Тимур](https://github.com/Timik2t)
- [Сергеев Андрей](https://github.com/andrey-praktikum-98)

### Описание:

Проект YaMDb собирает отзывы пользователей на произведения.
Произведения делятся на категории.
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
В каждой категории есть произведения: книги, фильмы или музыка.
Произведению может быть присвоен жанр из списка предустановленных.
Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти; из пользовательских оценок формируется усреднённая оценка произведения — рейтинг.

Реализовано: 
- регистрация пользователя и выдача токенов;
- работа с категориями, жанрами, произведениями, отзывами и комментариями;
- возможность просматривать и изменять свою учетную запись.

# Технологии:

Django 2.2.16

djangorestframework 3.12.4

PostgreSQL 13.0-alpine

Nginx 1.21.3-alpine

Gunicorn 20.0.4

Docker 20.10.17, build 100c701

Docker-compose 3.3

### Установка:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Timik2t/api_yamdb.git
```

 В директории infra создайте файл .env с переменными окружения для работы с базой данных:
```
DJANGO_KEY='your Django secret key'
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```
- Из папки ` infra/ ` разверните контейнеры в новой структуре:
- Для запуска необходимо выполнить из директории с проектом команду:
``` sudo docker-compose up -d ```
_Для пересборки команда up выполняется с параметром --build_
``` sudo docker-compose up -d --build ```
- Теперь в контейнере web нужно выполнить миграции:
``` sudo docker-compose exec web python manage.py migrate ```
- Создать суперпользователя:
``` sudo docker-compose exec web python manage.py createsuperuser ```
- Собрать статику:
``` sudo docker-compose exec web python manage.py collectstatic --no-input ```
- Вы также можете создать дамп (резервную копию) базы:
``` sudo docker-compose exec web python manage.py dumpdata > fixtures.json ```
- или, разместив, например, файл fixtures.json в папке с Dockerfile, загрузить в базу данные из дампа:
``` sudo docker-compose exec web python manage.py loaddata fixtures.json ```

### Полная документация работы с api:
- [документация](api_yamdb/static/redoc.yaml)
- [локальный сервер](http://127.0.0.1:8000/)
### Работающий сервер (IP изменить на свой)
- [сервер](http://84.201.160.48/api/v1/)
- [админ панель](http://84.201.160.48/admin)
- [документация](http://84.201.160.48/redoc)