import json
import logging

logger = logging.getLogger(__name__)

def extract_json_from_response(response_text):
    """
    Extract JSON from LLM response text
    """
    logger.info(f"Extracting JSON from response text: {response_text}")
    # Remove code block markers if present
    response_text = response_text.replace("```json", "").replace("```", "")
    # Find the first '{' and last '}' and extract the substring
    start = response_text.find('{')
    end = response_text.rfind('}')
    if start != -1 and end != -1 and end > start:
        json_str = response_text[start:end+1]
        try:
            logger.info(f"Trying to parse JSON string: {json_str}")
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e} for string: {json_str}")
    else:
        logger.warning("No JSON-like structure found in response text.")
    return None

def validate_n8n_workflow(workflow_json):
    """
    Basic validation for n8n workflow structure
    """
    logger.info(f"Validating workflow JSON: {workflow_json}")
    required_fields = ["name", "nodes", "connections"]
    for field in required_fields:
        if field not in workflow_json:
            logger.error(f"Missing required field: {field}")
            return False, f"Missing required field: {field}"
    if not isinstance(workflow_json["nodes"], list):
        logger.error("Nodes should be a list")
        return False, "Nodes should be a list"
    if not isinstance(workflow_json["connections"], dict):
        logger.error("Connections should be a dictionary")
        return False, "Connections should be a dictionary"
    logger.info("Workflow JSON is valid.")
    return True, "Valid n8n workflow structure"