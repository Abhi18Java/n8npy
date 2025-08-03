import streamlit as st
import requests
from config import settings
from dotenv import load_dotenv
load_dotenv()
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
st.title("SMARTFLOW n8n Workflow Generator")

# Sidebar layout
st.sidebar.header("Menu")
create_new = st.sidebar.button("Create New Workflow")
view_all = st.sidebar.button("Your Workflows")

BASE_URL = "http://localhost:8000"

# Session State for selected workflow
if "selected_workflow" not in st.session_state:
    st.session_state.selected_workflow = None
if "workflows" not in st.session_state:
    st.session_state.workflows = []
if "show_workflows" not in st.session_state:
    st.session_state.show_workflows = False
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False
if "show_create" not in st.session_state:
    st.session_state.show_create = False

# Create New Workflow
if create_new:
    logger.info("User triggered 'Create New Workflow'")
    st.session_state.selected_workflow = None
    st.session_state.show_workflows = False
    st.session_state.show_chat = False
    st.session_state.show_create = True

# View All Workflows
if view_all:
    st.session_state.show_chat = False
    st.session_state.selected_workflow = None
    st.session_state.show_workflows = True
    st.session_state.show_create = False

# Show Create New Workflow form
if st.session_state.show_create:
    st.subheader("Create New Workflow")
    prompt = st.text_area("Enter your prompt to generate workflow:", key="create_prompt")
    if st.button("Generate", key="generate_btn"):
        if prompt.strip():
            logger.info(f"User prompt for workflow generation: {prompt}")
            with st.spinner("Generating workflow..."):
                response = requests.post(
                    f"{BASE_URL}/generate-workflow",
                    json={"prompt": prompt}
                )
                logger.info(f"API request sent to {BASE_URL}/generate-workflow")
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"API response received: {data}")
                    if data.get("error"):
                        logger.error(f"Error received from API: {data['error']}")
                        st.error(f"Error: {data['error']}")
                    else:
                        logger.info("Workflow generated successfully.")
                        st.success("Workflow generated successfully!")
                        st.json(data)
                else:
                    logger.error(f"API request failed with status code: {response.status_code}")
                    st.error(f"API Error: {response.status_code}")
        else:
            st.warning("Please enter a prompt to generate workflow.")

# Show workflows in sidebar when requested
if st.session_state.show_workflows:
    with st.sidebar:
        st.subheader("Your Workflows")
        with st.spinner("Fetching workflows..."):
            logger.info("Fetching workflows from API...")
            response = requests.get(f"{BASE_URL}/get_all_workflows")
            logger.info(f"API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"API response data: {data}")
                
                if data.get("success"):
                    workflows = data["data"]
                    logger.info(f"Found {len(workflows)} workflows")
                    st.session_state.workflows = workflows

                    if workflows:
                        st.write(f"Found {len(workflows)} workflows:")
                        # Display only workflow names as buttons
                        for i, wf in enumerate(workflows):
                            if isinstance(wf, dict):
                                wf_name = wf.get("name", "Unnamed Workflow")
                                logger.info(f"Workflow {i}: {wf_name}")
                            else:
                                wf_name = f"Workflow {i+1}"
                                logger.warning(f"Workflow {i} is not a dict: {type(wf)}")
                            
                            if st.button(wf_name, key=f"wf_{i}"):
                                logger.info(f"Selected workflow: {wf_name}")
                                st.session_state.selected_workflow = wf
                                st.session_state.show_chat = True
                                st.rerun()
                    else:
                        logger.warning("No workflows found in response")
                        st.info("No workflows found.")
                else:
                    logger.error(f"API returned error: {data.get('error')}")
                    st.error(f"Error: {data.get('error')}")
            else:
                logger.error(f"API request failed with status: {response.status_code}")
                st.error(f"API Error: {response.status_code}")

# Workflow Selected - Chat/Describe/Edit
if st.session_state.show_chat and st.session_state.selected_workflow:
    wf = st.session_state.selected_workflow
    logger.info(f"Selected workflow type: {type(wf)}")
    
    if isinstance(wf, dict):
        wf_name = wf.get('name', 'Unknown Workflow')
        wf_id = wf.get('id', None)
        logger.info(f"Selected workflow: {wf_name}, ID: {wf_id}")
        st.subheader(f"Chat with Workflow: {wf_name}")
        
        # Show workflow details in an expander
        with st.expander("View Workflow Details"):
            st.json(wf)
    else:
        logger.warning(f"Selected workflow is not a dict: {wf}")
        st.subheader(f"Chat with Workflow: {wf}")
        with st.expander("View Workflow Details"):
            st.write(wf)

    st.write("💬 **Chat with your workflow**")
    st.write("Ask questions about the workflow or request updates. Examples:")
    st.write("- What does this workflow do?")
    st.write("- How does this workflow work?")
    st.write("- Update this workflow to add email notifications")
    
    describe_prompt = st.text_area("Your message:", placeholder="What does this workflow do?", height=100)
    if st.button("Send"):
        logger.info(f"User prompt: {describe_prompt}")
        
        # Ask for info
        if "what" in describe_prompt.lower() or "describe" in describe_prompt.lower():
            with st.spinner("Asking AI to describe workflow..."):
                logger.info("Sending describe request to API")
                # Create a descriptive prompt for the AI
                full_prompt = f"Analyze this n8n workflow and {describe_prompt}. Here's the workflow: {json.dumps(wf, indent=2)}"
                response = requests.post(
                    f"{BASE_URL}/describe-workflow",
                    json={"prompt": full_prompt}
                )
                logger.info(f"Describe response status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    st.success("Workflow described successfully!")
                    st.write(data.get("description", "No description available"))
                else:
                    st.error("Failed to get description.")
        # Update workflow
        elif "update" in describe_prompt.lower() or "edit" in describe_prompt.lower():
            if isinstance(wf, dict) and wf.get('id'):
                with st.spinner("Updating workflow..."):
                    logger.info(f"Sending update request for workflow ID: {wf['id']}")
                    response = requests.put(
                        f"{BASE_URL}/workflows/{wf['id']}",
                        json={"prompt": describe_prompt}
                    )
                    logger.info(f"Update response status: {response.status_code}")
                    if response.status_code == 200:
                        st.success("Workflow updated!")
                        st.write(response.json())
                    else:
                        st.error(f"Failed to update workflow. Status code: {response.status_code}")
            else:
                logger.error("Cannot update workflow: missing ID or invalid format")
                st.error("Cannot update workflow: missing ID or invalid format")
        else:
            # For any other prompt, treat as description request
            with st.spinner("Processing your request..."):
                logger.info("Sending general request to describe API")
                full_prompt = f"{describe_prompt}. Here's the workflow: {json.dumps(wf, indent=2)}"
                response = requests.post(
                    f"{BASE_URL}/describe-workflow",
                    json={"prompt": full_prompt}
                )
                logger.info(f"General response status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    st.success("Response:")
                    st.write(data.get("description", "No response available"))
                else:
                    st.error("Failed to process request.")

# Show default message when no workflow is selected and no action is taken
if not st.session_state.show_chat and not st.session_state.show_create and not st.session_state.show_workflows:
    st.write("### Welcome to SMARTFLOW n8n Workflow Generator")
    st.write("- Click **'Create New Workflow'** to generate a new workflow")
    st.write("- Click **'Your Workflows'** to view and interact with existing workflows")