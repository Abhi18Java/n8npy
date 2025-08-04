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
st.title("Welcome to SMARTFLOW n8n Workflow Generator")
st.markdown("This is an AI-powered n8n workflow generator. Enter your request and let the AI do the rest!")
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
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "create_chat_messages" not in st.session_state:
    st.session_state.create_chat_messages = []

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
    
    # Display create workflow chat history
    if st.session_state.create_chat_messages:
        for message in st.session_state.create_chat_messages:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**AI:** {message['content']}")
        st.markdown("---")
    else:
        # Add vertical spacing when no chat history
        st.markdown("<div style='height: 300px;'></div>", unsafe_allow_html=True)
    with st.form("create_workflow_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            prompt = st.text_input("", key="create_prompt", placeholder="Create a workflow that...")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add space for alignment
            submitted = st.form_submit_button("Generate", use_container_width=True)
        
        if submitted and prompt.strip():
            logger.info(f"User prompt for workflow generation: {prompt}")
            
            # Add user message to create chat history
            st.session_state.create_chat_messages.append({"role": "user", "content": prompt})
            
            # Check if this is a workflow creation request or generic message
            workflow_keywords = ["create", "workflow", "generate", "build", "make", "design"]
            is_workflow_request = any(keyword in prompt.lower() for keyword in workflow_keywords)
            
            if is_workflow_request:
                # Try to generate workflow
                with st.spinner("Generating workflow..."):
                    response = requests.post(
                        f"{BASE_URL}/generate-workflow",
                        json={"prompt": prompt}
                    )
                    logger.info(f"API request sent to {BASE_URL}/generate-workflow")
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"API response received: {data}")
                        if data.get("error") or data.get("name") == "Error Workflow":
                            logger.error(f"Error received from API: {data.get('error', 'Unknown error')}")
                            ai_response = f"Error: {data.get('error', 'Could not generate workflow')}"
                            st.session_state.create_chat_messages.append({"role": "ai", "content": ai_response})
                            st.rerun()
                        else:
                            logger.info("Workflow generated successfully.")
                            ai_response = "Workflow generated successfully! Please check your n8n instance."
                            st.session_state.create_chat_messages.append({"role": "ai", "content": ai_response})
                            st.rerun()
                    else:
                        logger.error(f"API request failed with status code: {response.status_code}")
                        ai_response = f"API Error: {response.status_code}"
                        st.session_state.create_chat_messages.append({"role": "ai", "content": ai_response})
                        st.rerun()
            else:
                # Handle as generic message
                with st.spinner("Processing your message..."):
                    response = requests.post(
                        f"{BASE_URL}/describe-workflow",
                        json={"prompt": prompt}
                    )
                    logger.info(f"API request sent to {BASE_URL}/describe-workflow")
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"API response received: {data}")
                        ai_response = data.get("description", "I'm here to help you with n8n workflows!")
                        st.session_state.create_chat_messages.append({"role": "ai", "content": ai_response})
                        st.rerun()
                    else:
                        logger.error(f"API request failed with status code: {response.status_code}")
                        ai_response = "I'm here to help you with n8n workflows! Try asking me to create a workflow."
                        st.session_state.create_chat_messages.append({"role": "ai", "content": ai_response})
                        st.rerun()
        elif submitted and not prompt.strip():
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
                                st.session_state.chat_messages = []  # Clear chat history for new workflow
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
        st.subheader(f"Selected workflow: {wf_name}")
        
        # Show workflow details in an expander
        with st.expander("View Workflow Details"):
            st.json(wf)
    else:
        logger.warning(f"Selected workflow is not a dict: {wf}")
        st.subheader(f"Chat with Workflow: {wf}")
        with st.expander("View Workflow Details"):
            st.write(wf)
    
    # Display chat history
    if st.session_state.chat_messages:
       # st.write("💬 **Chat History:**")
        for message in st.session_state.chat_messages:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**AI:** {message['content']}")
        st.markdown("---")
    else:
        # Add vertical spacing when no chat history
        st.markdown("<div style='height: 300px;'></div>", unsafe_allow_html=True)
    
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            describe_prompt = st.text_input("", placeholder="Write your message", key="chat_input")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # for spacing
            send_clicked = st.form_submit_button("Send", use_container_width=True)
        
        if send_clicked and describe_prompt.strip():
            logger.info(f"User prompt: {describe_prompt}")
            
            # Add user message to chat history
            st.session_state.chat_messages.append({"role": "user", "content": describe_prompt})

            # Handle the prompt based on context
            if st.session_state.show_chat and st.session_state.selected_workflow:
                wf = st.session_state.selected_workflow
                # Your existing logic here
                if "what" in describe_prompt.lower() or "describe" in describe_prompt.lower() or "explain" in describe_prompt.lower():
                    with st.spinner("Asking AI to describe workflow..."):
                        logger.info("Sending describe request to API")
                        full_prompt = f"Analyze this n8n workflow and {describe_prompt}. Here's the workflow: {json.dumps(wf, indent=2)}"
                        response = requests.post(
                            f"{BASE_URL}/describe-workflow",
                            json={"prompt": full_prompt}
                        )
                        logger.info(f"Describe response status: {response.status_code}")
                        if response.status_code == 200:
                            data = response.json()
                            ai_response = data.get("description", "No description available")
                            st.session_state.chat_messages.append({"role": "ai", "content": ai_response})
                            st.rerun()
                        else:
                            error_msg = "Failed to get description."
                            st.session_state.chat_messages.append({"role": "ai", "content": error_msg})
                            st.rerun()
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
                                ai_response = "Workflow updated successfully, please check n8n UI!"
                                st.session_state.chat_messages.append({"role": "ai", "content": ai_response})
                                st.rerun()
                            else:
                                error_msg = f"Failed to update workflow. Status code: {response.status_code}"
                                st.session_state.chat_messages.append({"role": "ai", "content": error_msg})
                                st.rerun()
                    else:
                        error_msg = "Cannot update workflow: missing ID or invalid format"
                        st.session_state.chat_messages.append({"role": "ai", "content": error_msg})
                        st.rerun()
                else:
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
                            ai_response = data.get("description", "No response available")
                            st.session_state.chat_messages.append({"role": "ai", "content": ai_response})
                            st.rerun()
                        else:
                            error_msg = "Failed to process request."
                            st.session_state.chat_messages.append({"role": "ai", "content": error_msg})
                            st.rerun()
        
        elif send_clicked and not describe_prompt.strip():
            st.warning("Please enter a message before sending.")


# Show default message when no workflow is selected and no action is taken
if not st.session_state.show_chat and not st.session_state.show_create and not st.session_state.show_workflows:
    st.write("- Click **'Create New Workflow'** to generate a new workflow")
    st.write("- Click **'Your Workflows'** to view and interact with existing workflows")