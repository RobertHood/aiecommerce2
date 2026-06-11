import importlib
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .catalog_qa import answer_catalog_question
from .models import ChatLog


rag_chain = None
rag_module = None


def parse_json(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON format"}, status=400)


def get_chain():
    global rag_chain, rag_module
    if rag_chain is None:
        rag_module = importlib.import_module("rag_chat")
        rag_chain = rag_module.setup_rag()
    return rag_chain


def health(request):
    return JsonResponse({"service": "ai", "status": "ok", "catalog_fallback": True})


@csrf_exempt
def chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    message = data.get("message", "").strip()
    if not message:
        return JsonResponse({"error": "Message cannot be empty"}, status=400)

    try:
        response_text, source = answer_catalog_question(message)
        ChatLog.objects.create(question=message, answer=response_text or "")
        return JsonResponse({"response": response_text, "source": source})
    except Exception as catalog_exc:
        catalog_error = str(catalog_exc)

    try:
        chain = get_chain()
        if not chain:
            raise RuntimeError("RAG system is not initialized. Ensure GROQ_API_KEY is configured and Neo4j is running.")
        response_text = rag_module.ask_question(chain, message)
        ChatLog.objects.create(question=message, answer=response_text or "")
        return JsonResponse({"response": response_text, "source": "rag"})
    except Exception as exc:
        error = f"Catalog QA failed: {catalog_error}; RAG failed: {exc}"
        ChatLog.objects.create(question=message, error=error)
        return JsonResponse({"error": error}, status=500)
