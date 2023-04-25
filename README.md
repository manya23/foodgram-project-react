# Foodgram-project

### Информация для ревью

Данные админа:
- email: adm@mail.ru
- password: adm_adm_in

Адрес сайта:
- http://158.160.29.94

## БД проекта:
![db_scheme.png](db_scheme.png)

## Структура приложений API

![project_scheme.png](project_scheme.png)

Проект содержит набор приложений, описаных в папке ***/api***: 
- api
- auth
- users
- recipes
- ingredients
- tags

### Приложение users
Реализует функционал:

### Приложение recipes
Реализует функционал:

### Полный список эндпоинтов проекта:
/api/users/ </br>
/api/users/{id}/ </br>

/api/users/me/ </br>
/api/users/set_password/ </br>

/api/auth/token/login/ </br>
/api/auth/token/logout/ </br>

/api/tags/ </br>
/api/tags/{id}/ </br>

/api/recipes/ </br>
/api/recipes/{id}/ </br>

/api/recipes/download_shopping_cart/ </br>
/api/recipes/{id}/shopping_cart/ </br>
/api/recipes/{id}/favorite/ </br>

/api/users/subscriptions/ </br>
/api/users/{id}/subscribe/ </br>

/api/ingredients/ </br>
/api/ingredients/{id}/ </br>