### Запуск
Настройте файлы .env и .env.docker как в примере
Выполните в корне проекта команду
```bash
docker-compose up --build
```
Приложение соберется и запустится автоматически, тесты тоже автоматически запустятся, если тесты запускать отдельно, надо выполнить команду
```bash
docker-compose run tests
```
После запуска приложения можно уже им пользоваться, никих миграций внутри контейнера проводить не надо, все миграции выполнятся автоматически.
Документация приложения будет на маршруте
```http
localhost:8000/docs
```
Само приложение на маршруте
```http
localhost:8000/
```
Для использования приложения, надо зарегистрировать аккаунт через запрос
```http
curl -X 'POST' \
  'http://localhost:8000/register?email=example%40example.com&name=example&password=1234' \
  -H 'accept: application/json' \
  -d ''
```
А затем авторизоваться
```http
curl -X 'POST' \
  'http://localhost:8000/login?email=example%40example.com&password=1234' \
  -H 'accept: application/json' \
  -d ''
```
Создайте нужное количество аккаунтов, затем переходите на маршрут приложения
![image](https://github.com/user-attachments/assets/1234e382-2b2c-4859-af78-c72ed7046a13)

Здесь вы и собеседник подключаетесь к 1 чату, номер которого введете и можете в режиме реального времени обмениваться сообщениями.
Маршрут получения истории собщений конкретного чата
```http
curl -X 'GET' \
  'http://localhost:8000/history/1?limit=50&offset=0' \
  -H 'accept: application/json'
```
И пример вывода
```json
[
  {
    "message_id": 1,
    "sender_id": 1,
    "text": "test",
    "timestamp": "2025-03-12T08:59:00.343435",
    "read": false
  },
  {
    "message_id": 2,
    "sender_id": 1,
    "text": "test",
    "timestamp": "2025-03-12T08:59:04.037063",
    "read": false
  },
  {
    "message_id": 3,
    "sender_id": 1,
    "text": "message 3",
    "timestamp": "2025-03-12T08:59:06.848707",
    "read": false
  },
  {
    "message_id": 4,
    "sender_id": 1,
    "text": "message 4",
    "timestamp": "2025-03-12T08:59:09.541231",
    "read": false
  }
]
```
