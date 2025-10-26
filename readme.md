# Интернет-магазин книг Книжкин

Веб-приложение для продажи книг для ДПП Клиент-серверные приложения: проектирование и разработка

## Требования

- Docker
- Docker Compose

## Запуск

1) git clone https://github.com/kinraku/bookstore.git

2) cd bookstore

3) docker compose up --build

4) открыть http://localhost:5002/

админ: http://localhost:5002/admin  
- логин: admin  
- пароль: admin123

## Структура

app.py - основное Flask приложение

config.py - конфигурация

requirements.txt - зависимости Python

Dockerfile - конфигурация для образа Flask

docker-compose.yml - оркестрация

database/init.sql - инициализация бд и тестовые книги

static/css/ - стили

static/uploads/ - обложки тестовых книг

templates/*.html - шаблоны страниц