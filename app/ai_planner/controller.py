"""
AI Planner Controller
API endpoints for AI-powered project planning
"""

from flask import Blueprint, request, Response
import json
from typing import List, Dict, Any
from app.ai_planner.service import AIPlannerService
from app.ai_planner.models import TeamMember, ProjectContext, GeneratedPlan, Worker, TaskToAssign


ai_planner_bp = Blueprint("ai_planner", __name__)


def _get_planner_service():
    """Lazy initialization of planner service"""
    return AIPlannerService()


def _create_response(data: Any, status: int = 200) -> Response:
    """Helper to create JSON response with proper encoding"""
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=status,
        content_type="application/json; charset=utf-8"
    )


def _parse_team_members(data: List[Dict]) -> List[TeamMember]:
    """Parse team members from request data"""
    return [
        TeamMember(
            id=member.get("id", ""),
            name=member.get("name", ""),
            email=member.get("email", ""),
            role=member.get("role", "")
        )
        for member in data
    ]


def _parse_project_context(data: Dict) -> ProjectContext:
    """Parse project context from request data"""
    return ProjectContext(
        project_name=data.get("projectName", ""),
        project_description=data.get("projectDescription", ""),
        short_code=data.get("shortCode", ""),
        team_size=data.get("teamSize", 0)
    )


@ai_planner_bp.route("/ai-planner/generate", methods=["POST"])
def generate_plan():
    """
    Generate a new project plan

    Expected JSON body:
    {
        "projectDescription": "string",
        "teamMembers": [
            {
                "id": "string",
                "name": "string",
                "email": "string",
                "role": "string"
            }
        ],
        "projectContext": {
            "projectName": "string",
            "projectDescription": "string",
            "shortCode": "string",
            "teamSize": number
        },
        "additionalContext": "string" (optional)
    }
    """
    try:
        data = request.get_json(force=True, silent=True)

        if not data:
            return _create_response(
                {"error": "Invalid JSON body"},
                status=400
            )

        # Validate required fields
        if "projectDescription" not in data:
            return _create_response(
                {"error": "Missing 'projectDescription'"},
                status=400
            )

        if "teamMembers" not in data or not isinstance(data["teamMembers"], list):
            return _create_response(
                {"error": "Missing or invalid 'teamMembers'"},
                status=400
            )

        if "projectContext" not in data:
            return _create_response(
                {"error": "Missing 'projectContext'"},
                status=400
            )

        # Parse request data
        project_description = data["projectDescription"]
        team_members = _parse_team_members(data["teamMembers"])
        project_context = _parse_project_context(data["projectContext"])
        additional_context = data.get("additionalContext")

        # Generate plan
        plan = _get_planner_service().generate_project_plan(
            project_description=project_description,
            team_members=team_members,
            project_context=project_context,
            additional_context=additional_context
        )

        return _create_response({
            "success": True,
            "plan": plan.to_dict()
        })

    except ValueError as e:
        return _create_response(
            {"error": f"Validation error: {str(e)}"},
            status=400
        )
    except Exception as e:
        return _create_response(
            {"error": f"Internal error: {str(e)}"},
            status=500
        )


@ai_planner_bp.route("/ai-planner/refine", methods=["POST"])
def refine_plan():
    """
    Refine an existing project plan

    Expected JSON body:
    {
        "currentPlan": {
            "tasks": [...],
            "reasoning": "string",
            "estimatedTotalHours": number
        },
        "refinementPrompt": "string",
        "conversationHistory": [
            {
                "role": "string",
                "content": "string"
            }
        ],
        "teamMembers": [...],
        "projectContext": {...}
    }
    """
    try:
        data = request.get_json(force=True, silent=True)

        if not data:
            return _create_response(
                {"error": "Invalid JSON body"},
                status=400
            )

        # Validate required fields
        required_fields = [
            "currentPlan",
            "refinementPrompt",
            "conversationHistory",
            "teamMembers",
            "projectContext"
        ]

        for field in required_fields:
            if field not in data:
                return _create_response(
                    {"error": f"Missing '{field}'"},
                    status=400
                )

        # Parse request data
        current_plan = GeneratedPlan.from_dict(data["currentPlan"])
        refinement_prompt = data["refinementPrompt"]
        conversation_history = data["conversationHistory"]
        team_members = _parse_team_members(data["teamMembers"])
        project_context = _parse_project_context(data["projectContext"])

        # Refine plan
        refined_plan = _get_planner_service().refine_project_plan(
            current_plan=current_plan,
            refinement_prompt=refinement_prompt,
            conversation_history=conversation_history,
            team_members=team_members,
            project_context=project_context
        )

        return _create_response({
            "success": True,
            "plan": refined_plan.to_dict()
        })

    except ValueError as e:
        return _create_response(
            {"error": f"Validation error: {str(e)}"},
            status=400
        )
    except Exception as e:
        return _create_response(
            {"error": f"Internal error: {str(e)}"},
            status=500
        )


@ai_planner_bp.route("/ai-planner/assign", methods=["POST"])
def assign_tasks():
    """
    Assign tasks to workers based on roles and current workload.

    Expected JSON body:
    {
        "workers": [
            {
                "id": "string",
                "name": "string",
                "role": "string",
                "availableHoursPerWeek": number (optional),
                "currentTasks": [
                    {
                        "title": "string",
                        "estimatedHours": number,
                        "priority": "low|medium|high|critical"
                    }
                ]
            }
        ],
        "tasksToAssign": [
            {
                "id": "string",
                "title": "string",
                "description": "string",
                "estimatedHours": number (optional),
                "priority": "low|medium|high|critical",
                "tags": ["string"]
            }
        ]
    }
    """
    try:
        data = request.get_json(force=True, silent=True)

        if not data:
            return _create_response({"error": "Invalid JSON body"}, status=400)

        if "workers" not in data or not isinstance(data["workers"], list):
            return _create_response({"error": "Missing or invalid 'workers'"}, status=400)

        if "tasksToAssign" not in data or not isinstance(data["tasksToAssign"], list):
            return _create_response({"error": "Missing or invalid 'tasksToAssign'"}, status=400)

        if not data["tasksToAssign"]:
            return _create_response({"error": "'tasksToAssign' must not be empty"}, status=400)

        if not data["workers"]:
            return _create_response({"error": "'workers' must not be empty"}, status=400)

        workers = [Worker.from_dict(w) for w in data["workers"]]
        tasks = [TaskToAssign.from_dict(t) for t in data["tasksToAssign"]]

        result = _get_planner_service().assign_tasks(workers=workers, tasks=tasks)

        return _create_response({"success": True, "result": result.to_dict()})

    except ValueError as e:
        return _create_response({"error": f"Validation error: {str(e)}"}, status=400)
    except Exception as e:
        return _create_response({"error": f"Internal error: {str(e)}"}, status=500)


@ai_planner_bp.route("/ai-planner/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return _create_response({
        "status": "healthy",
        "service": "AI Planner"
    })
