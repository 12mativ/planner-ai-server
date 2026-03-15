"""
Test script for AI Planner API
Demonstrates how to use the AI planning endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

# Test data
test_data = {
    "projectDescription": """
    Создать веб-приложение для управления задачами команды.
    Требования:
    - Регистрация и авторизация пользователей
    - Создание и управление проектами
    - Создание задач с приоритетами и дедлайнами
    - Назначение задач участникам команды
    - Комментарии к задачам
    - Уведомления о новых задачах
    - Дашборд с аналитикой
    """,
    "teamMembers": [
        {
            "id": "user1",
            "name": "Иван Иванов",
            "email": "ivan@example.com",
            "role": "Full-stack разработчик"
        },
        {
            "id": "user2",
            "name": "Мария Петрова",
            "email": "maria@example.com",
            "role": "Frontend разработчик"
        },
        {
            "id": "user3",
            "name": "Алексей Сидоров",
            "email": "alexey@example.com",
            "role": "Backend разработчик"
        },
        {
            "id": "user4",
            "name": "Елена Смирнова",
            "email": "elena@example.com",
            "role": "UI/UX дизайнер"
        }
    ],
    "projectContext": {
        "projectName": "TaskMaster",
        "projectDescription": "Система управления задачами для команд",
        "shortCode": "TM",
        "teamSize": 4
    },
    "additionalContext": "Проект должен быть готов к MVP за 3 месяца. Используем React для фронтенда и Python/Flask для бэкенда."
}


def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/ai-planner/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_generate_plan():
    """Test plan generation"""
    print("\n=== Testing Plan Generation ===")
    try:
        response = requests.post(
            f"{BASE_URL}/ai-planner/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"\nSuccess: {result.get('success')}")

            plan = result.get('plan', {})
            print(f"\nРассуждение: {plan.get('reasoning')}")
            print(f"Общее время: {plan.get('estimatedTotalHours')} часов")
            print(f"\nКоличество задач: {len(plan.get('tasks', []))}")

            # Print first 3 tasks as example
            for i, task in enumerate(plan.get('tasks', [])[:3], 1):
                print(f"\n--- Задача {i} ---")
                print(f"Название: {task.get('title')}")
                print(f"Приоритет: {task.get('priority')}")
                print(f"Оценка: {task.get('estimatedHours')} часов")
                print(f"Теги: {', '.join(task.get('tags', []))}")
                print(f"Описание: {task.get('description')[:100]}...")

            if len(plan.get('tasks', [])) > 3:
                print(f"\n... и еще {len(plan.get('tasks', [])) - 3} задач")

            return result
        else:
            print(f"Error: {response.json()}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def test_refine_plan(current_plan):
    """Test plan refinement"""
    print("\n=== Testing Plan Refinement ===")

    if not current_plan:
        print("No plan to refine")
        return False

    refine_data = {
        "currentPlan": current_plan.get('plan'),
        "refinementPrompt": "Добавь больше задач по тестированию и документации. Также нужны задачи по DevOps и CI/CD.",
        "conversationHistory": [
            {
                "role": "user",
                "content": test_data["projectDescription"]
            },
            {
                "role": "assistant",
                "content": json.dumps(current_plan.get('plan'), ensure_ascii=False)
            }
        ],
        "teamMembers": test_data["teamMembers"],
        "projectContext": test_data["projectContext"]
    }

    try:
        response = requests.post(
            f"{BASE_URL}/ai-planner/refine",
            json=refine_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"\nSuccess: {result.get('success')}")

            plan = result.get('plan', {})
            print(f"\nОбновленное рассуждение: {plan.get('reasoning')}")
            print(f"Новое общее время: {plan.get('estimatedTotalHours')} часов")
            print(f"Количество задач: {len(plan.get('tasks', []))}")

            return True
        else:
            print(f"Error: {response.json()}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("AI Planner API Tests")
    print("=" * 60)

    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed. Is the server running?")
        return

    print("\n✅ Health check passed")

    # Test 2: Generate plan
    plan_result = test_generate_plan()
    if plan_result:
        print("\n✅ Plan generation passed")
    else:
        print("\n❌ Plan generation failed")
        return

    # Test 3: Refine plan
    if test_refine_plan(plan_result):
        print("\n✅ Plan refinement passed")
    else:
        print("\n❌ Plan refinement failed")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
