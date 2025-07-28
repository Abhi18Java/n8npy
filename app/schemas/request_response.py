# app/schemas/request_response.py

from pydantic import BaseModel
from typing import Optional

class WorkflowRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None

class WorkflowResponse(BaseModel):
    name: str
    nodes: list
    connections: dict
