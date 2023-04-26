# Foodgram-project

![workflow status](https://github.com/manya23/foodgram-project-react/actions/workflows/main.yml/badge.svg)

### Информация для ревью

Данные админа:
- email: adm@mail.ru
- password: adm_adm_in

Адрес сайта:
- http://158.160.29.94

 ### Описание
 В репозитории представлен API для сервиса 'Продуктовый помощник'.
И фронтэнд реализация сервиса, включающая в себя веб-сервер, базу данных
и фронтэнд часть.
 ### Технологии
 - Python 3.7
 - Django 2.2
 ### Запуск
 Для запуска проекта, из директории `infra/` необходимо запустить 
 команду сборки docker-контейнеров, содержащих сервер базы данных
  Postgress, веб-сервер Nginx и django-проект API продуктового 
 помощника: 
 ```
docker compose build
 ```
Когда контейнеры будут собраны, можно запустить проект командой : 
 ```
docker-compose up
 ```
