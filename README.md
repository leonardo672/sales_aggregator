# API Агрегатора Продаж

## Описание

Это мини-сервис REST API для загрузки, хранения и агрегирования данных о продажах на маркетплейсах. Поддерживает загрузку CSV, аналитику и конвертацию валют.

---

## Требования

* Python 3.11+
* FastAPI
* Uvicorn
* Pandas
* Pydantic
* SQLite (необязательно, поддерживается хранение в памяти)

Установка зависимостей:

```bash
pip install -r requirements.txt
```

---

## Структура проекта

```
sales_aggregator/
├── main.py              # Точка входа FastAPI
├── models/
│   ├── sale.py          # Модели продаж Pydantic
│   └── analytics.py     # Модели ответов аналитики Pydantic
├── routers/
│   ├── sales.py         # CRUD эндпоинты для продаж
│   └── analytics.py     # Эндпоинты аналитики
├── services/
│   ├── storage.py       # Хранение в памяти / SQLite
│   ├── aggregation.py   # Логика агрегирования с Pandas
│   └── currency.py      # Интеграция с API валют
├── requirements.txt
└── README.md            # Этот файл
```

---

## Запуск сервиса

Запуск FastAPI сервера:

```bash
uvicorn main:app --reload
```

Сервер будет доступен по адресу `http://localhost:8000`.

---

## Эндпоинты

### Продажи

#### POST /sales

* Добавление одной или нескольких продаж.
* Тело запроса: список продаж.
* Возвращает: количество добавленных записей.

#### GET /sales

* Получение списка продаж.
* Необязательные параметры запроса: `marketplace`, `status`, `date_from`, `date_to`, `page`, `page_size`.

### Аналитика

#### GET /analytics/summary

* Агрегированные метрики.
* Обязательные параметры: `date_from`, `date_to`.
* Необязательные: `marketplace`, `group_by` (`marketplace` | `date` | `status`).

#### GET /analytics/top-products

* Топ продуктов за период.
* Обязательные параметры: `date_from`, `date_to`.
* Необязательные: `sort_by` (`revenue` | `quantity` | `profit`, по умолчанию=`revenue`), `limit` (по умолчанию=10).

#### GET /analytics/summary-usd

* То же, что `/summary`, но в конвертации в USD.
* Используется открытое API Центрального Банка России: `https://www.cbr-xml-daily.ru/daily_json.js`
* Кэширование курса на 1 час.

#### POST /analytics/upload-csv

* Загрузка CSV файла с продажами.
* Возвращает: `loaded` строки, `errors` и детали некорректных строк.

---

## Пример CSV

```
order_id,marketplace,product_name,quantity,price,cost_price,status,sold_at
ORD-001,ozon,Cable USB-C,3,450.00,120.00,delivered,2025-03-01
...
```

---

## Примечания

* Убедитесь, что даты `sold_at` не находятся в будущем.
* Допустимые `marketplace`: `ozon`, `wildberries`, `yandex_market`.
* `price`, `cost_price` > 0; `quantity` >= 1.
* Возвращенные или отмененные заказы учитываются в аналитике соответствующим образом.
* Хранение в памяти сбрасывается при перезапуске сервера, если SQLite не включен.

---

## Тестирование эндпоинтов

* Используйте Postman или любой HTTP-клиент.
* Пример: Загрузка CSV → Проверка `/sales` → `/analytics/summary` → `/analytics/top-products` → `/analytics/summary-usd`.
* Фильтруйте, сортируйте и пагинируйте с помощью параметров запроса, как описано выше.
