from flask import Blueprint, request, Response
import json
from app.prompt.service import PromptClass

prompt_bp = Blueprint("prompt", __name__)

@prompt_bp.route("/prompt", methods=["POST"])
def prompt():
    try:
        data = request.get_json(force=True, silent=True)
        if not data or "prompt" not in data:
            return Response(
                json.dumps({"error": "Missing 'prompt'"}, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )

        prompt_text = data["prompt"]
        result = PromptClass.send_prompt(prompt_text)

        return Response(
            json.dumps({"result": result}, ensure_ascii=False),
            status=200,
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}, ensure_ascii=False),
            status=500,
            content_type="application/json; charset=utf-8"
        )
