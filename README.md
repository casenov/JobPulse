Окей, тогда давай без упрощений — полноценное ТЗ уровня “можно отдать команде и строить продукт”. Без MVP, сразу с расчётом на масштабирование и нормальную эксплуатацию.

---

# 📄 Техническое задание

## Проект: **JobScout Backend (Vacancy Aggregation Platform)**

---

# 1. 🎯 Цель системы

Разработать масштабируемый backend-сервис для:

* агрегации вакансий из множества источников
* нормализации и очистки данных
* интеллектуальной фильтрации
* предоставления API для клиентов (web / mobile / bot)

Система должна выдерживать рост:

* источников (10 → 100+)
* вакансий (10k → 10M+)
* пользователей

---

# 2. 🏗 Архитектура (High-Level)

## Подход: **Modular Monolith → Microservices-ready**

На старте:

* Django + DRF (ядро)
* Celery (асинхронка)
* Redis (broker/cache)
* PostgreSQL (основная БД)

С возможностью выделения:

* parsing-service
* notification-service
* recommendation-service

---

# 3. 🧩 Доменные области

Система делится на bounded contexts:

### 1. Users

* пользователи системы
* настройки и фильтры

### 2. Vacancies

* хранение вакансий
* поиск и фильтрация

### 3. Sources

* источники данных
* конфигурация парсинга

### 4. Parsing

* логика сбора данных
* нормализация

### 5. Matching (ключевая часть)

* сопоставление вакансий и фильтров

### 6. Notifications (в будущем)

* очередь уведомлений

---

# 4. 🗄️ Модель данных (расширенная)

## User

* id
* email (optional)
* is_active
* created_at

---

## Source

* id
* name
* type (api / scraping / telegram)
* base_url
* rate_limit
* is_active
* last_parsed_at

---

## Vacancy (оптимизированная)

* id (UUID)

* external_id (из источника)

* source_id

* title

* description (text)

* short_description (preprocessed)

* company_name

* company_meta (JSON)

* location_raw

* location_normalized

* salary_from

* salary_to

* currency

* employment_type (full-time, part-time)

* work_format (remote / onsite / hybrid)

* experience_level (junior/middle/senior)

* skills (JSON / ARRAY)

* url (unique constraint)

* published_at

* parsed_at

* updated_at

* is_active

* is_deleted (soft delete)

---

## VacancyContent (опционально — для оптимизации)

(если хочешь вынести тяжёлый текст)

* vacancy_id
* full_text

---

## Filter

* id
* user_id
* keywords (ARRAY / JSON)
* excluded_keywords
* locations
* work_format
* salary_min
* experience_level
* is_active

---

## VacancyMatch

(очень важно для производительности)

* id
* vacancy_id
* filter_id
* score (float)
* matched_at

---

## ParsingLog

* source_id
* status
* parsed_count
* error_message
* started_at
* finished_at

---

# 5. ⚙️ Парсинг (Production уровень)

## Требования:

* Асинхронность
* Расширяемость (плагинная система)
* Fault-tolerance

---

## Архитектура парсинга:

### 1. Parser Registry

```python
PARSERS = {
    "hh": HHParser,
    "linkedin": LinkedInParser,
}
```

---

### 2. Pipeline

1. Fetch
2. Validate
3. Normalize
4. Deduplicate
5. Save

---

## Нормализация (обязательно)

* Очистка HTML
* Приведение валют
* Определение:

  * уровня (junior/middle)
  * формата работы
* NLP (опционально):

  * извлечение навыков

---

## Дедупликация

Стратегии:

* по `url`
* по `external_id`
* fuzzy matching (title + company)

---

# 6. 🔍 Поиск и фильтрация

## Требования:

* Быстрый поиск (<200ms)
* Полнотекстовый поиск

---

## Реализация:

### PostgreSQL:

* `GIN index` для текста
* `Trigram similarity`

ИЛИ:

### Elasticsearch (опционально, лучше):

* полнотекстовый поиск
* ранжирование

---

## Фильтрация:

* по зарплате
* по location
* по ключевым словам
* по типу работы

---

# 7. 🧠 Matching Engine (ключевая часть)

Система должна:

* автоматически сопоставлять вакансии и фильтры

---

## Алгоритм:

Score =

* keyword match (вес 0.5)
* location match (0.2)
* salary match (0.2)
* experience match (0.1)

---

## Результат:

* сохраняется в VacancyMatch
* используется для уведомлений

---

# 8. 🔄 Асинхронные задачи

Celery задачи:

* parse_source
* normalize_vacancies
* match_vacancies
* cleanup_old_data

---

## Планировщик:

* Celery Beat

---

# 9. 🔌 API (DRF)

## Основные endpoints:

### Vacancies

* GET /vacancies/
* GET /vacancies/{id}

### Filters

* CRUD

### Sources (admin only)

---

## Дополнительно:

* пагинация
* сортировка
* search

---

# 10. 🧑‍💼 Админка (важно)

Требования:

* удобный просмотр вакансий
* фильтрация
* просмотр логов парсинга

---

# 11. ⚡ Производительность

* bulk_create (обязательно)
* select_related / prefetch_related
* кэширование (Redis)
* индексы:

  * published_at
  * source
  * salary

---

# 12. 🔐 Безопасность

* rate limiting
* защита API
* валидация входных данных

---

# 13. 📊 Логирование и мониторинг

* Sentry (ошибки)
* Prometheus / Grafana (метрики)
* логирование парсинга

---

# 14. 🚀 Деплой

* Docker
* Nginx
* Gunicorn
* PostgreSQL
* Redis

---

# 15. 📈 Расширения

* AI анализ вакансий
* рекомендации
* Telegram интеграция
* Web UI

---

# 💬 Честно

Вот это уже не “проект для портфолио”, а
👉 **реальная система уровня продукта**

Если ты реально это реализуешь:

* с нормальным парсингом
* matching engine
* индексами
* асинхронкой

👉 ты спокойно проходишь на **middle+/senior backend**

---

Если хочешь следующий шаг — я тебе разложу:
👉 **как именно реализовать matching engine и парсинг без узких мест** (там как раз чаще всего все ломаются)


