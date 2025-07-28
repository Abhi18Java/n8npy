# D:\AI_Project\n8n_wf_creator\app\main.py
from fastapi import FastAPI
from app.schemas.request_response import WorkflowRequest, WorkflowResponse
from app.services.langchain_service import get_llm_chain
from app.utils.json_validator import extract_json_from_response, validate_n8n_workflow
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SMARTFLOW n8n Workflow Generator")

@app.post("/generate-workflow", response_model=WorkflowResponse)
async def generate_workflow(request: WorkflowRequest):
    logger.info(f"Received workflow generation request: {request}")
    chain = get_llm_chain()
    logger.info("LangChain conversation chain initialized.")
    response = chain.run(request.prompt)
    logger.info(f"LLM response: {response}")
    workflow_json = extract_json_from_response(response)
    logger.info(f"Extracted workflow JSON: {workflow_json}")
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
    logger.info("Workflow successfully generated.")
    return WorkflowResponse(**workflow_json)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)