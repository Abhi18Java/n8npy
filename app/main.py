# D:\AI_Project\n8n_wf_creator\app\main.py
from app.n8n_client import n8n_get_all_workflows
from fastapi import FastAPI
from app.schemas.request_response import WorkflowRequest, WorkflowResponse
from app.services.langchain_service import get_llm_chain
from app.utils.json_validator import extract_json_from_response, validate_n8n_workflow
import logging
from fastapi import Path
from app.n8n_client import update_workflow_in_n8n
from app.n8n_client import get_workflow_by_id
from app.n8n_client import create_workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SMARTFLOW n8n Workflow Generator")


@app.post("/generate-workflow", response_model=WorkflowResponse)
async def generate_workflow(request: WorkflowRequest):
    logger.info(f"Received workflow generation request: {request}")
    try:
        chain = get_llm_chain()
        logger.info("LangChain conversation chain initialized.")
        response = chain.run(request.prompt)
        logger.info(f"LLM response: {response}")
        workflow_json = extract_json_from_response(response)
    except Exception as e:
        logger.error(f"Error during LLM processing: {e}")
        return WorkflowResponse(
            name="Error Workflow",
            nodes=[],
            connections={},
            error=f"API Error: {str(e)}"
        )
   # logger.info(f"Extracted workflow JSON: {workflow_json}")
    if not workflow_json:
        logger.error("Could not extract valid JSON from LLM response.")
        return WorkflowResponse(
            name="Error Workflow",
            nodes=[],
            connections={},
            error="Could not extract valid JSON from LLM response"
        )
    is_valid, message = validate_n8n_workflow(workflow_json)
    logger.info(f"Workflow validation result: {is_valid}, message: {message}")
    if not is_valid:
        logger.error(f"Workflow validation failed: {message}")
        return WorkflowResponse(
            name="Error Workflow",
            nodes=[],
            connections={},
            error=message
        )
    logger.info("Workflow successfully generated and validated.")
    
    # Automatically create the workflow in n8n
    logger.info("Creating workflow in n8n...")
    n8n_result = create_workflow(workflow_json)
    
    if n8n_result.get("success"):
        logger.info("Workflow successfully created in n8n")
        # Add n8n creation info to the response
        workflow_response = WorkflowResponse(**workflow_json)
        return workflow_response
    else:
        logger.error(f"Failed to create workflow in n8n: {n8n_result.get('message')}")
        return WorkflowResponse(
            name=workflow_json.get("name", "Error Workflow"),
            nodes=workflow_json.get("nodes", []),
            connections=workflow_json.get("connections", {}),
            error=f"Workflow generated but failed to create in n8n: {n8n_result.get('message')}"
        )

@app.put("/workflows/{workflow_id}")
async def update_workflow(workflow_id: str = Path(...), request: WorkflowRequest = None):
    logger.info(f"Update request received for workflow ID: {workflow_id} with prompt: {request.prompt}")
    try:
        # First, get the current workflow from n8n
        current_workflow = get_workflow_by_id(workflow_id)
        
        if not current_workflow or not current_workflow.get("success"):
            return {"success": False, "error": "Could not fetch current workflow from n8n"}
        
        # Create a comprehensive prompt with the current workflow
        import json
        current_workflow_json = current_workflow.get("data", {})
        full_prompt = f"""Update this existing n8n workflow based on the user's request.
        
User request: {request.prompt}
        
Current workflow JSON:
{json.dumps(current_workflow_json, indent=2)}
        
Return the updated workflow JSON with the requested changes."""
        
        try:
            chain = get_llm_chain()
            updated_response = chain.run(full_prompt)
            workflow_json = extract_json_from_response(updated_response)
        except Exception as e:
            logger.error(f"Error during workflow update LLM processing: {e}")
            return {"success": False, "error": f"API Error: {str(e)}"}

        if not workflow_json:
            return {"success": False, "error": "Invalid updated workflow JSON from LLM."}

        update_result = update_workflow_in_n8n(workflow_id, workflow_json)

        return update_result
    except Exception as e:
        logger.error(f"Exception during workflow update: {e}")
        return {"success": False, "error": str(e)}



@app.post("/describe-workflow")
async def describe_workflow(request: WorkflowRequest):
    logger.info(f"Received workflow description request: {request.prompt}")
    try:
        chain = get_llm_chain()
        logger.info("LangChain conversation chain initialized for description.")
        response = chain.run(request.prompt)
        logger.info(f"LLM description response: {response}")
        
        # Return the raw response for descriptions
        return {"description": response}
    except Exception as e:
        logger.error(f"Error during description generation: {e}")
        error_msg = str(e)
        if "rate limit" in error_msg.lower() or "429" in error_msg:
            return {"description": "I'm currently experiencing high demand. Please try again in a few moments."}
        else:
            return {"description": "I'm here to help you with n8n workflows! Please try your request again."}

# Endpoint to get all workflows from n8n public API
@app.get("/get_all_workflows")
async def get_all_workflows_endpoint():
    try:
        result = n8n_get_all_workflows()
        return result
    except Exception as e:
        logger.error(f"Failed to fetch workflows from n8n: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
