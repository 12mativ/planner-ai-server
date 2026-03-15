# AI Planner API Documentation

## Обзор

AI Planner - это модуль для автоматической генерации и уточнения планов проектов с использованием искусственного интеллекта. Модуль интегрирован с Yandex GPT API и предоставляет REST API для работы с планированием проектов.

## Структура модуля

```
app/ai_planner/
├── __init__.py       # Экспорт моделей
├── models.py         # Модели данных (TeamMember, ProjectContext, GeneratedTask, GeneratedPlan)
├── service.py        # Бизнес-логика и взаимодействие с AI API
└── controller.py     # REST API endpoints
```

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /api/ai-planner/health`

**Описание:** Проверка работоспособности сервиса

**Ответ:**
```json
{
  "status": "healthy",
  "service": "AI Planner"
}
```

---

### 2. Генерация плана проекта

**Endpoint:** `POST /api/ai-planner/generate`

**Описание:** Генерирует детальный план задач на основе описания проекта

**Тело запроса:**
```json
{
  "projectDescription": "Детальное описание проекта и требований",
  "teamMembers": [
    {
      "id": "user1",
      "name": "Иван Иванов",
      "email": "ivan@example.com",
      "role": "Full-stack разработчик"
    }
  ],
  "projectContext": {
    "projectName": "Название проекта",
    "projectDescription": "Краткое описание",
    "shortCode": "PROJ",
    "teamSize": 4
  },
  "additionalContext": "Дополнительная информация (опционально)"
}
```

**Ответ:**
```json
{
  "success": true,
  "plan": {
    "tasks": [
      {
        "title": "Название задачи",
        "description": "Детальное описание с критериями приемки",
        "priority": "medium",
        "estimatedHours": 8,
        "suggestedAssignees": ["user1"],
        "dependencies": [],
        "tags": ["backend", "api"]
      }
    ],
    "reasoning": "Объяснение логики декомпозиции",
    "estimatedTotalHours": 120
  }
}
```

**Приоритеты задач:**
- `low` - низкий
- `medium` - средний
- `high` - высокий
- `critical` - критичный

---

### 3. Уточнение плана проекта

**Endpoint:** `POST /api/ai-planner/refine`

**Описание:** Уточняет существующий план на основе обратной связи

**Тело запроса:**
```json
{
  "currentPlan": {
    "tasks": [...],
    "reasoning": "...",
    "estimatedTotalHours": 120
  },
  "refinementPrompt": "Добавь больше задач по тестированию",
  "conversationHistory": [
    {
      "role": "user",
      "content": "Исходное описание проекта"
    },
    {
      "role": "assistant",
      "content": "JSON предыдущего плана"
    }
  ],
  "teamMembers": [...],
  "projectContext": {...}
}
```

**Ответ:**
```json
{
  "success": true,
  "plan": {
    "tasks": [...],
    "reasoning": "Обновленное объяснение",
    "estimatedTotalHours": 150
  }
}
```

---

## Модели данных

### TeamMember
```python
{
  "id": str,          # Уникальный идентификатор
  "name": str,        # Имя участника
  "email": str,       # Email
  "role": str         # Роль в команде
}
```

### ProjectContext
```python
{
  "projectName": str,         # Название проекта
  "projectDescription": str,  # Описание проекта
  "shortCode": str,          # Короткий код (например, "TM")
  "teamSize": int            # Размер команды
}
```

### GeneratedTask
```python
{
  "title": str,                    # Название задачи
  "description": str,              # Детальное описание
  "priority": str,                 # low | medium | high | critical
  "estimatedHours": int,           # Оценка в часах (опционально)
  "suggestedAssignees": [str],     # ID участников
  "dependencies": [int],           # Индексы зависимых задач
  "tags": [str]                    # Теги для категоризации
}
```

### GeneratedPlan
```python
{
  "tasks": [GeneratedTask],        # Список задач
  "reasoning": str,                # Объяснение логики
  "estimatedTotalHours": int       # Общая оценка (опционально)
}
```

---

## Использование

### Запуск сервера

```bash
python server.py
```

Сервер запустится на `http://localhost:5000`

### Тестирование

Запустите тестовый скрипт:

```bash
python test_ai_planner.py
```

Этот скрипт:
1. Проверит работоспособность API
2. Сгенерирует план для тестового проекта
3. Уточнит план с дополнительными требованиями

### Пример использования с curl

**Генерация плана:**
```bash
curl -X POST http://localhost:5000/api/ai-planner/generate \
  -H "Content-Type: application/json" \
  -d '{
    "projectDescription": "Создать веб-приложение для управления задачами",
    "teamMembers": [
      {
        "id": "user1",
        "name": "Иван Иванов",
        "email": "ivan@example.com",
        "role": "Full-stack разработчик"
      }
    ],
    "projectContext": {
      "projectName": "TaskMaster",
      "projectDescription": "Система управления задачами",
      "shortCode": "TM",
      "teamSize": 1
    }
  }'
```

### Пример использования с Python

```python
import requests

response = requests.post(
    "http://localhost:5000/api/ai-planner/generate",
    json={
        "projectDescription": "Описание проекта",
        "teamMembers": [...],
        "projectContext": {...}
    }
)

if response.status_code == 200:
    plan = response.json()["plan"]
    print(f"Создано задач: {len(plan['tasks'])}")
    print(f"Общее время: {plan['estimatedTotalHours']} часов")
```

---

## Конфигурация

Убедитесь, что в файле `.env` настроен токен для Yandex API:

```env
SOY_TOKEN=your_yandex_oauth_token_here
```

---

## Особенности AI планирования

AI анализирует:
- Описание проекта и требования
- Роли и навыки участников команды
- Размер команды и контекст проекта
- Дополнительный контекст (сроки, технологии и т.д.)

AI создает:
- Задачи оптимального размера (1-40 часов)
- Зависимости между задачами
- Равномерное распределение по участникам
- Приоритизацию задач
- Категоризацию через теги
- Оценки времени выполнения

---

## Обработка ошибок

Все endpoints возвращают ошибки в формате:

```json
{
  "error": "Описание ошибки"
}
```

**Коды ошибок:**
- `400` - Некорректные данные запроса
- `500` - Внутренняя ошибка сервера или ошибка AI API

---

## Интеграция с Next.js

Модуль полностью совместим с вашим Next.js проектом. Используйте те же структуры данных для бесшовной интеграции между фронтендом и бэкендом.

**Пример интеграции:**

```typescript
// В Next.js приложении
const response = await fetch('http://localhost:5000/api/ai-planner/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    projectDescription,
    teamMembers,
    projectContext,
    additionalContext
  })
});

const { plan } = await response.json();
```

---

## Лицензия

Этот модуль является частью вашего дипломного проекта.
