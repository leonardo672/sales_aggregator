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
├── main.py                  # Точка входа в приложение FastAPI
├── models/
│   ├── sale.py              # Pydantic модели для продаж
│   └── analytics.py         # Pydantic модели для ответов аналитики
├── routers/
│   ├── sales.py             # CRUD endpoints для /sales
│   └── analytics.py         # Endpoints аналитики: сводка, топ-продукты, загрузка CSV, конвертация USD
├── services/
│   ├── storage.py           # Хранилище продаж в памяти или SQLite
│   ├── aggregation.py       # Логика сводки и топ-продуктов (с использованием Pandas)
│   ├── currency.py          # Получение и кэширование курса USD/RUB
│   └── logging.py           # Структурированный лог (JSON формат)
├── tests/
│   ├── test_endpoints.py    # Тесты pytest для основных endpoints
│   └── sample_data.csv      # Пример CSV файла для тестирования загрузки
├── sales-aggregator-api-tests.zip  # ZIP файл с дополнительными тестами
├── .github/
│   └── workflows/
│       └── docker.yml       # GitHub Actions CI/CD workflow для сборки и публикации Docker
├── Dockerfile               # Определение Docker контейнера
├── requirements.txt         # Зависимости Python
├── README.md                # Инструкции по запуску, детали API
└── .gitignore               # Игнорирование venv, __pycache__, логов и др.
```

---

## Запуск сервиса

### Локальный запуск через Python

```bash
uvicorn main:app --reload
```

Сервер будет доступен по адресу `http://localhost:8000`.

---

### Запуск через Docker

Сборка образа:

```bash
docker build -t sales-aggregator .
```

Запуск контейнера:

```bash
docker run -p 8000:8000 sales-aggregator
```

Сервис будет доступен по адресу `http://localhost:8000`.

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
