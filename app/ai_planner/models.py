"""
AI Planner Models
Data structures for AI-powered project planning
"""

from typing import List, Optional, Literal
from dataclasses import dataclass, asdict
from enum import Enum


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TeamMember:
    id: str
    name: str
    email: str
    role: str

    def to_dict(self):
        return asdict(self)


@dataclass
class ProjectContext:
    project_name: str
    project_description: str
    short_code: str
    team_size: int

    def to_dict(self):
        return asdict(self)


@dataclass
class GeneratedTask:
    title: str
    description: str
    priority: Literal["low", "medium", "high", "critical"]
    estimated_hours: Optional[int] = None
    suggested_assignees: List[str] = None  # User IDs
    dependencies: List[int] = None  # Task indices in the array
    tags: List[str] = None

    def __post_init__(self):
        if self.suggested_assignees is None:
            self.suggested_assignees = []
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            priority=data.get("priority", "medium"),
            estimated_hours=data.get("estimatedHours"),
            suggested_assignees=data.get("suggestedAssignees", []),
            dependencies=data.get("dependencies", []),
            tags=data.get("tags", [])
        )


@dataclass
class GeneratedPlan:
    tasks: List[GeneratedTask]
    reasoning: str
    estimated_total_hours: Optional[int] = None

    def to_dict(self):
        return {
            "tasks": [task.to_dict() for task in self.tasks],
            "reasoning": self.reasoning,
            "estimatedTotalHours": self.estimated_total_hours
        }

    @classmethod
    def from_dict(cls, data: dict):
        tasks = [GeneratedTask.from_dict(task) for task in data.get("tasks", [])]
        return cls(
            tasks=tasks,
            reasoning=data.get("reasoning", ""),
            estimated_total_hours=data.get("estimatedTotalHours")
        )


# --- Task Assignment Models ---

@dataclass
class WorkerTask:
    """A task currently assigned to a worker (represents workload)"""
    title: str
    estimated_hours: int
    priority: str = "medium"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            title=data.get("title", ""),
            estimated_hours=data.get("estimatedHours", 0),
            priority=data.get("priority", "medium")
        )


@dataclass
class Worker:
    """A worker with their current workload"""
    id: str
    name: str
    role: str
    current_tasks: List[WorkerTask] = None
    available_hours_per_week: Optional[int] = None

    def __post_init__(self):
        if self.current_tasks is None:
            self.current_tasks = []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "currentTasks": [t.to_dict() for t in self.current_tasks],
            "availableHoursPerWeek": self.available_hours_per_week
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            role=data.get("role", ""),
            current_tasks=[WorkerTask.from_dict(t) for t in data.get("currentTasks", [])],
            available_hours_per_week=data.get("availableHoursPerWeek")
        )


@dataclass
class TaskToAssign:
    """A task that needs to be assigned to a worker"""
    id: str
    title: str
    description: str
    estimated_hours: Optional[int] = None
    priority: str = "medium"
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "estimatedHours": self.estimated_hours,
            "priority": self.priority,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            estimated_hours=data.get("estimatedHours"),
            priority=data.get("priority", "medium"),
            tags=data.get("tags", [])
        )


@dataclass
class TaskAssignment:
    """AI decision: which worker is assigned to which task"""
    task_id: str
    worker_id: str
    worker_name: str
    reasoning: str

    def to_dict(self):
        return {
            "taskId": self.task_id,
            "workerId": self.worker_id,
            "workerName": self.worker_name,
            "reasoning": self.reasoning
        }


@dataclass
class AssignmentResult:
    """Full result of the AI assignment process"""
    assignments: List[TaskAssignment]
    reasoning: str

    def to_dict(self):
        return {
            "assignments": [a.to_dict() for a in self.assignments],
            "reasoning": self.reasoning
        }

    @classmethod
    def from_dict(cls, data: dict, workers_by_id: dict):
        assignments = []
        for item in data.get("assignments", []):
            worker_id = item.get("workerId", "")
            assignments.append(TaskAssignment(
                task_id=item.get("taskId", ""),
                worker_id=worker_id,
                worker_name=workers_by_id.get(worker_id, worker_id),
                reasoning=item.get("reasoning", "")
            ))
        return cls(
            assignments=assignments,
            reasoning=data.get("reasoning", "")
        )
