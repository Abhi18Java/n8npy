# D:\AI_Project\n8n_wf_creator\app\n8n_client.py
import os
import requests
import logging
try:
    from app.config import settings  # For FastAPI/package usage
except ImportError:
    try:
        from config import settings  # For direct/script/Streamlit usage
    except ImportError:
        # Fallback to environment variables only
        class Settings:
            def __init__(self):
                self.openai_api_key = os.getenv("OPENAI_API_KEY")
                self.n8n_api_base_url = os.getenv("N8N_API_BASE_URL")
                self.n8n_api_key = os.getenv("N8N_API_KEY")
        settings = Settings()
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file


logger = logging.getLogger(__name__)

N8N_API_BASE_URL = os.getenv("N8N_API_BASE_URL", settings.n8n_api_base_url)
N8N_API_KEY = os.getenv("N8N_API_KEY", settings.n8n_api_key)


HEADERS = {
    "Content-Type": "application/json",
    "X-N8N-API-KEY": N8N_API_KEY
}


def create_workflow(workflow_json: dict) -> dict:
    url = f"{N8N_API_BASE_URL}/workflows"
    payload = {
        "name": workflow_json.get("name", "Untitled Workflow"),
        "nodes": workflow_json.get("nodes", []),
        "connections": workflow_json.get("connections", {}),
        "settings": {}
    }
    logger.info(f"Sending workflow to n8n: {payload}")
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
        workflows = response.json().get("data", [])
        return {
            "success": True,
            "data": workflows
        }
    else:
        return {
            "success": False,
            "error": response.text
        }
    

def get_workflow_by_id(workflow_id: str) -> dict:
    url = f"{N8N_API_BASE_URL}/workflows/{workflow_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        logger.info(f"n8n GET workflow response status: {response.status_code}")
        logger.info(f"n8n GET workflow response body: {response.text}")
    except Exception as e:
        logger.error(f"Exception during GET request to n8n: {e}")
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


def update_workflow_in_n8n(workflow_id: str, workflow_json: dict) -> dict:
    url = f"{N8N_API_BASE_URL}/workflows/{workflow_id}"
    payload = {
        "name": workflow_json.get("name", "Updated Workflow"),
        "nodes": workflow_json.get("nodes", []),
        "connections": workflow_json.get("connections", {}),
        "settings": {}
    }

    logger.info(f"Updating workflow ID {workflow_id} in n8n: {payload}")
    try:
        response = requests.put(url, headers=HEADERS, json=payload)
        logger.info(f"n8n PUT response status: {response.status_code}")
        logger.info(f"n8n PUT response body: {response.text}")
    except Exception as e:
        logger.error(f"Exception during PUT request to n8n: {e}")
        return {
            "success": False,
            "status_code": None,
            "message": str(e)
        }

    if response.status_code in (200, 204):
        return {
            "success": True,
            "data": workflow_json
        }
    else:
        return {
            "success": False,
            "status_code": response.status_code,
            "message": response.text
        }

