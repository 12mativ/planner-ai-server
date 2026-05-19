"""
AI Planner Service
Handles communication with OpenAI API for intelligent project planning
"""

import os
import json
import requests
from typing import List, Optional, Dict, Any
from app.ai_planner.models import (
    TeamMember,
    ProjectContext,
    GeneratedTask,
    GeneratedPlan,
    Worker,
    TaskToAssign,
    AssignmentResult,
)


SYSTEM_PROMPT = """Ты - опытный проектный менеджер и архитектор программного обеспечения. Твоя задача - разбить описание проекта на конкретные, выполнимые задачи.

ВАЖНЫЕ ПРАВИЛА:
1. Создавай задачи, которые можно выполнить за 1-40 часов
2. Разбивай большие задачи на подзадачи
3. Учитывай зависимости между задачами
4. Распределяй задачи равномерно между участниками команды
5. Учитывай роли и навыки участников команды
6. Используй приоритеты: critical (критично), high (высокий), medium (средний), low (низкий)
7. Добавляй теги для категоризации задач (frontend, backend, database, testing, documentation, design, etc.)

ФОРМАТ ОТВЕТА (строго JSON):
{
  "tasks": [
    {
      "title": "Краткое название задачи",
      "description": "Детальное описание того, что нужно сделать. Включи критерии приемки.",
      "priority": "medium",
      "estimatedHours": 8,
      "suggestedAssignees": ["userId1"],
      "dependencies": [],
      "tags": ["backend", "api"]
    }
  ],
  "reasoning": "Объяснение логики декомпозиции проекта и распределения задач",
  "estimatedTotalHours": 120
}"""


class AIPlannerService:
    """Service for AI-powered project planning"""

    def __init__(self):
        self.api_url = os.getenv("API_URL")
        self.api_key = os.getenv("SOY_TOKEN")

        if not self.api_key or not self.api_url:
            raise ValueError("SOY_TOKEN или API_URL не настроен в переменных окружения")

    def _build_user_prompt(
        self,
        project_description: str,
        team_members: List[TeamMember],
        project_context: ProjectContext,
        additional_context: Optional[str] = None
    ) -> str:
        """Build user prompt for project planning"""

        members_info = "\n".join([
            f"- {m.name} (ID: {m.id}, Email: {m.email}, Роль: {m.role})"
            for m in team_members
        ])

        prompt = f"""ОПИСАНИЕ ПРОЕКТА:
{project_description}

КОНТЕКСТ ПРОЕКТА:
- Название: {project_context.project_name}
- Короткий код: {project_context.short_code}
- Описание: {project_context.project_description or "Не указано"}
- Размер команды: {project_context.team_size} человек

УЧАСТНИКИ КОМАНДЫ:
{members_info}
"""

        if additional_context:
            prompt += f"\nДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ:\n{additional_context}\n"

        prompt += "\nПроанализируй проект и создай детальный план задач. Учти навыки и роли участников команды при распределении задач."

        return prompt

    def _make_api_request(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """Make request to OpenAI API"""

        headers = {
            "Authorization": f"OAuth {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "gpt-4.1-nano",
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(self.api_url, json=payload, headers=headers)

        if not response.ok:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", response.text)
            raise Exception(f"OpenAI API error: {error_message}")

        return response.json()

    def _validate_and_parse_plan(self, content: str) -> GeneratedPlan:
        """Validate and parse the generated plan"""

        if not content:
            raise ValueError("Пустой ответ от OpenAI API")

        plan_data = json.loads(content)

        # Валидация структуры плана
        if "tasks" not in plan_data or not isinstance(plan_data["tasks"], list):
            raise ValueError("Некорректная структура плана: отсутствует массив задач")

        # Валидация и нормализация каждой задачи
        for task_data in plan_data["tasks"]:
            if "title" not in task_data or "description" not in task_data:
                raise ValueError("Некорректная задача: отсутствует title или description")

            # Нормализация приоритета
            if task_data.get("priority") not in ["low", "medium", "high", "critical"]:
                task_data["priority"] = "medium"

            # Обеспечение наличия массивов
            if "suggestedAssignees" not in task_data:
                task_data["suggestedAssignees"] = []
            if "dependencies" not in task_data:
                task_data["dependencies"] = []
            if "tags" not in task_data:
                task_data["tags"] = []

        return GeneratedPlan.from_dict(plan_data)

    def generate_project_plan(
        self,
        project_description: str,
        team_members: List[TeamMember],
        project_context: ProjectContext,
        additional_context: Optional[str] = None
    ) -> GeneratedPlan:
        """
        Generate a project plan based on description and team context

        Args:
            project_description: Description of the project to plan
            team_members: List of team members with their roles
            project_context: Project metadata and context
            additional_context: Optional additional context for planning

        Returns:
            GeneratedPlan with tasks, reasoning, and estimates
        """

        user_prompt = self._build_user_prompt(
            project_description,
            team_members,
            project_context,
            additional_context
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response_data = self._make_api_request(messages)

            # Debug logging
            print(f"API Response keys: {response_data.keys()}")

            # Try both response formats (Yandex and OpenAI)
            if "response" in response_data:
                # Yandex format
                content = response_data["response"]["choices"][0]["message"]["content"]
            else:
                # OpenAI format
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content")

            print(f"Content received: {content[:200] if content else 'None'}...")

            return self._validate_and_parse_plan(content)

        except Exception as e:
            print(f"Error generating project plan: {e}")
            print(f"Response data: {response_data if 'response_data' in locals() else 'No response'}")
            raise

    def refine_project_plan(
        self,
        current_plan: GeneratedPlan,
        refinement_prompt: str,
        conversation_history: List[Dict[str, str]],
        team_members: List[TeamMember],
        project_context: ProjectContext
    ) -> GeneratedPlan:
        """
        Refine an existing project plan based on user feedback

        Args:
            current_plan: The current plan to refine
            refinement_prompt: User's refinement request
            conversation_history: Previous conversation messages
            team_members: List of team members
            project_context: Project metadata

        Returns:
            Updated GeneratedPlan
        """

        members_info = "\n".join([
            f"- {m.name} (ID: {m.id}, Роль: {m.role})"
            for m in team_members
        ])

        context_message = f"""ТЕКУЩИЙ ПЛАН:
{json.dumps(current_plan.to_dict(), ensure_ascii=False, indent=2)}

УЧАСТНИКИ КОМАНДЫ:
{members_info}

КОНТЕКСТ ПРОЕКТА:
- Название: {project_context.project_name}
- Короткий код: {project_context.short_code}

ЗАПРОС НА УТОЧНЕНИЕ:
{refinement_prompt}

Обнови план задач согласно запросу. Верни полный обновленный план в том же JSON формате."""

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversation_history,
            {"role": "user", "content": context_message}
        ]

        try:
            response_data = self._make_api_request(messages)

            # Try both response formats (Yandex and OpenAI)
            if "response" in response_data:
                # Yandex format
                content = response_data["response"]["choices"][0]["message"]["content"]
            else:
                # OpenAI format
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content")

            return self._validate_and_parse_plan(content)

        except Exception as e:
            print(f"Error refining project plan: {e}")
            raise

    def assign_tasks(
        self,
        workers: List[Worker],
        tasks: List[TaskToAssign]
    ) -> AssignmentResult:
        """
        Assign tasks to workers based on their roles, skills, and current workload.

        Args:
            workers: List of workers with their current task lists
            tasks: List of tasks that need to be assigned

        Returns:
            AssignmentResult with one assignment per task and overall reasoning
        """

        workers_info = []
        for w in workers:
            busy_hours = sum(t.estimated_hours for t in w.current_tasks)
            task_lines = "\n".join(
                f"    • {t.title} ({t.estimated_hours}ч, {t.priority})"
                for t in w.current_tasks
            ) or "    (нет текущих задач)"
            capacity = (
                f"{w.available_hours_per_week}ч/нед доступно"
                if w.available_hours_per_week is not None
                else "доступность не указана"
            )
            workers_info.append(
                f"Работник: {w.name} (ID: {w.id})\n"
                f"  Роль: {w.role}\n"
                f"  Текущая нагрузка: {busy_hours}ч\n"
                f"  Доступность: {capacity}\n"
                f"  Текущие задачи:\n{task_lines}"
            )

        tasks_info = []
        for t in tasks:
            tags = ", ".join(t.tags) if t.tags else "—"
            hours = f"{t.estimated_hours}ч" if t.estimated_hours else "не указано"
            tasks_info.append(
                f"Задача ID: {t.id}\n"
                f"  Название: {t.title}\n"
                f"  Описание: {t.description}\n"
                f"  Приоритет: {t.priority}\n"
                f"  Оценка: {hours}\n"
                f"  Теги: {tags}"
            )

        assignment_system_prompt = (
            "Ты — опытный тимлид. Твоя задача — распределить задачи между работниками "
            "с учётом их ролей, навыков и текущей загруженности.\n\n"
            "ПРАВИЛА:\n"
            "1. Назначай задачу тому, чья роль/навыки наиболее подходят\n"
            "2. Учитывай текущую нагрузку: не перегружай занятых работников\n"
            "3. Каждая задача должна быть назначена ровно одному работнику\n"
            "4. Используй только ID работников из списка\n\n"
            "ФОРМАТ ОТВЕТА (строго JSON):\n"
            "{\n"
            '  "assignments": [\n'
            "    {\n"
            '      "taskId": "id задачи",\n'
            '      "workerId": "id работника",\n'
            '      "reasoning": "краткое обоснование выбора"\n'
            "    }\n"
            "  ],\n"
            '  "reasoning": "общая стратегия распределения задач"\n'
            "}"
        )

        user_prompt = (
            "РАБОТНИКИ:\n"
            + "\n\n".join(workers_info)
            + "\n\nЗАДАЧИ ДЛЯ РАСПРЕДЕЛЕНИЯ:\n"
            + "\n\n".join(tasks_info)
            + "\n\nРаспредели задачи между работниками."
        )

        messages = [
            {"role": "system", "content": assignment_system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response_data = self._make_api_request(messages)

            if "response" in response_data:
                content = response_data["response"]["choices"][0]["message"]["content"]
            else:
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content")

            if not content:
                raise ValueError("Пустой ответ от API")

            data = json.loads(content)
            workers_by_id = {w.id: w.name for w in workers}
            return AssignmentResult.from_dict(data, workers_by_id)

        except Exception as e:
            print(f"Error assigning tasks: {e}")
            raise
