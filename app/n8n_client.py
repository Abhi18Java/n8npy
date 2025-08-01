# D:\AI_Project\n8n_wf_creator\app\n8n_client.py
import os
import requests
import logging
try:
    from app.config import settings  # For FastAPI/package usage
except ImportError:
    from config_simple import settings  # For direct/script/Streamlit usage
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file


logger = logging.getLogger(__name__)

N8N_API_BASE_URL = os.getenv("N8N_API_BASE_URL", settings.n8n_api_base_url)
N8N_API_KEY = os.getenv("N8N_API_KEY", settings.n8n_api_key)


HEADERS = {
    "Content-Type": "application/json"
}

# Add API key only if it exists
if N8N_API_KEY:
    HEADERS["X-N8N-API-KEY"] = N8N_API_KEY

logger.info(f"Using N8N_API_BASE_URL: {N8N_API_BASE_URL}")
logger.info(f"Using N8N_API_KEY: {'Yes' if N8N_API_KEY else 'No'}")
logger.info(f"Headers: {HEADERS}")


def create_workflow(workflow_json: dict) -> dict:
    url = f"{N8N_API_BASE_URL}/workflows"
    payload = {
        "name": workflow_json.get("name", "Untitled Workflow"),
        "nodes": workflow_json.get("nodes", []),
        "connections": workflow_json.get("connections", {}),
        "settings": {}
    }
    logger.info(f"Sending workflow to n8n: {payload}")
    logger.info(f"Headers: {HEADERS}")
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        logger.info(f"n8n API response status: {response.status_code}")
        logger.info(f"n8n API response text: {response.text}")
    except Exception as e:
        logger.error(f"Exception while calling n8n API: {e}")
        return {
            "success": False,
            "status_code": None,
            "message": str(e)
        }

    if response.status_code in (200, 201):
        return {
            "success": True,
            "data": response.json()
        }
    else:
        return {
            "success": False,
            "status_code": response.status_code,
            "message": response.text
        }


def n8n_get_all_workflows() -> dict:
    url = f"{N8N_API_BASE_URL}/workflows"
    try:
        response = requests.get(url, headers=HEADERS)
        logger.info(f"n8n API response status: {response.status_code}")
        logger.info(f"n8n API response text: {response.text}")
    except Exception as e:
        logger.error(f"Exception while calling n8n API: {e}")
        return {
            "success": False,
            "error": str(e)
        }

    if response.status_code == 200:
        return {
            "success": True,
            "data": response.json()
        }
    else:
        return {
            "success": False,
            "error": response.text
        }
