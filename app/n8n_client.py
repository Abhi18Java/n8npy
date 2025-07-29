# D:\AI_Project\n8n_wf_creator\app\n8n_client.py

import requests
import logging

logger = logging.getLogger(__name__)

N8N_API_BASE_URL = "http://localhost:5678/api/v1"
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjZWQ1Y2MyOC1kODAyLTQ0MWQtODQ3My0wN2YwNmE1M2QzNWQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzUzNzc1Mzc5LCJleHAiOjE3NTYzNTM2MDB9.GERS-yLaLR2Lc1EKipJJw926awMVpY6O8fIkABMWvCs"

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
    

def get_all_workflows():
    url = f"{N8N_API_BASE_URL}/workflows"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return {"success": True, "data": response.json()}
    else:
        return {
            "success": False,
            "status_code": response.status_code,
            "message": response.text
        }