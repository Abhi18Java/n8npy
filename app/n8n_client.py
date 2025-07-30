# D:\AI_Project\n8n_wf_creator\app\n8n_client.py
import os
import requests
import logging
from config import settings
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
    