# Warehouse CRM & Local AI Sommelier (RAG)

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?logo=telegram&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC244C)
![Ollama](https://img.shields.io/badge/Ollama-Qwen_2.5-000000)

Бэкенд-система автоматизации складского учёта для HoReCa (кальянного лаунжа), объединяющая REST API, асинхронного Telegram-бота и локальную RAG-систему для подбора миксов строго по актуальным остаткам на складе.

Проект решает две прикладные задачи заведения: ускоряет учёт позиций и закупок через Telegram, а также позволяет подбирать рекомендации гостям без галлюцинаций нейросети и без затрат на платные облачные LLM API.

---

## Ключевые возможности

- **Управление складом в Telegram (aiogram 3):** интерактивная панель с Inline-кнопками списания (-1) и приёмки (+5), пошаговое добавление новых товаров через машину состояний (FSM), расчёт общего бюджета склада и автоматический список позиций на закупку.
- **REST API с автодокументацией (FastAPI):** полный набор CRUD-эндпоинтов, фильтрация низких остатков, аналитика бюджета и точка интеграции для ИИ-запросов со встроенным Swagger UI (/docs).
- **Локальный ИИ-кальянщик (RAG):** семантический поиск по реальному наличию в базе (stock > 0) на базе 384-мерных эмбеддингов FastEmbed + векторной БД Qdrant и генерация ответов через локальную LLM qwen2.5:3b (Ollama).

---

## Архитектурные решения

- Единый источник данных (принцип DRY): модель Product, движок SQLite и фабрика сессий вынесены в общий модуль database.py, который переиспользуется в api.py, bot.py и rag.py.
- Неблокирующая асинхронность: синхронный пайплайн инференса LLM и векторного поиска вынесен в отдельный поток через asyncio.to_thread(), поэтому генерация ответа ИИ не замораживает event loop Telegram-бота для остальных пользователей.
- Защита от галлюцинаций и устаревших данных: перед каждым запросом в RAG выполняется синхронизация актуальных остатков из SQLite в Qdrant с фильтром Product.stock > 0 и низкой температурой генерации (temperature=0.3). Списанные в ноль позиции мгновенно исчезают из рекомендаций.
- Валидация входных данных: строгая типизация входящих JSON-запросов в FastAPI с помощью Pydantic-схем (ProductCreate, QuestionRequest).

---

## Технологический стек

| Слой | Технологии |
| :--- | :--- |
| Язык и среда | Python 3.12, python-dotenv |
| Web API | FastAPI, Uvicorn, Pydantic |
| Telegram-бот | aiogram 3 (FSM, Inline & Reply Keyboards) |
| База данных | SQLite, SQLAlchemy ORM |
| RAG & AI | Qdrant (in-memory), FastEmbed (paraphrase-multilingual-MiniLM-L12-v2), Ollama (qwen2.5:3b), OpenAI SDK |

---

## Структура проекта

.
├── api.py              # REST API на FastAPI и Pydantic-схемы
├── bot.py              # Telegram-бот на aiogram 3 (склад, FSM, кнопка ИИ)
├── database.py         # Единый модуль SQLAlchemy: модель Product и сессии
├── rag.py              # RAG-пайплайн: синхронизация с БД, Qdrant, FastEmbed, Ollama
├── requirements.txt    # Зависимости проекта
├── .env.example        # Шаблон переменных окружения
└── .gitignore          # Исключение секретов (.env), БД и кэша
---

## Эндпоинты REST API

После запуска сервера интерактивная документация доступна по адресу http://127.0.0.1:8000/docs.

| Метод | Эндпоинт | Описание |
| :--- | :--- | :--- |
| GET | / | Проверка работоспособности сервера |
| GET | /products | Получить список всех позиций склада |
| POST | /products | Добавить новый товар (name, price, stock) |
| DELETE | /products/{product_id} | Удалить товар по ID |
| GET | /budget | Рассчитать общую стоимость остатков склада |
| GET | /low-stock?limit=5 | Получить список товаров с остатком не выше limit |
| POST | /ask-ai | Задать вопрос локальному ИИ-кальянщику по базе наличия |

---

## Быстрый старт

### 1. Предварительные требования
- Python 3.12
- Установленная и запущенная [Ollama](https://ollama.com/)

Скачайте локальную языковую модель (выполняется один раз):
ollama pull qwen2.5:3b
### 2. Клонирование и установка зависимостей
git clone [https://github.com/](https://github.com/)<твой-ник>/<название-репозитория>.git
cd <название-репозитория>
pip install -r requirements.txt
### 3. Настройка окружения
Создайте файл .env в корне проекта (по образцу .env.example) и укажите токен бота от @BotFather:
BOT_TOKEN=your_telegram_bot_token_here
### 4. Запуск сервисов
Запустите REST API и Telegram-бота в двух отдельных терминалах:

# Терминал 1 — сервер FastAPI (Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs))
uvicorn api:app --reload

# Терминал 2 — Telegram-бот
python bot.py
При первом запуске FastEmbed автоматически скачает мультиязычную модель эмбеддингов (~120 МБ), а database.py создаст локальную базу warehouse_db.sqlite.

---

## Демонстрация работы

![Telegram Bot Demo](assets/bot_demo.png)
![FastAPI Swagger UI](assets/swagger_demo.png)