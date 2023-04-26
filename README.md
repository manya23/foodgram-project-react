# Foodgram-project

### Информация для ревью

Данные админа:
- email: adm@mail.ru
- password: adm_adm_in

Адрес сайта:
- http://158.160.29.94

 ### Описание
 API для сервиса 'Продуктовый помощник'.
 ### Технологии
 - Python 3.7
 - Django 2.2
 ### Запуск
 Для запуска проекта : 
 ```
 pip install -r requirements.txt
 ```
 Из директории проекта, содержащей файл manage.py, выполните миграции: 
 ```
 python3 manage.py migrate
 ```
 Теперь из этой же директории можно запустить проект:
 ```
 python3 manage.py runserver
 ```

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