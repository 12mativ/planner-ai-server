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
