
import streamlit as st
import requests
from n8n_client import create_workflow
from n8n_client import n8n_get_all_workflows
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("SMARTFLOW n8n Workflow Generator")

prompt = st.text_area("Enter your workflow prompt:")

if st.button("Generate Workflow"):
    with st.spinner("Generating..."):
        logger.info("Sending prompt to FastAPI backend...")
        response = requests.post(
            "http://localhost:8000/generate-workflow",
            json={"prompt": prompt}
        )
        logger.info(f"FastAPI response status: {response.status_code}")
        logger.info(f"FastAPI response text: {response.text}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Received workflow data: {data}")

            if data.get("error"):
                logger.error(f"Error from FastAPI: {data['error']}")
                st.error(f"Error: {data['error']}")
            else:
                st.success("Workflow generated successfully!")
                st.json(data)

                logger.info(
                    "Calling create_workflow to send workflow to n8n...")
                result = create_workflow(data)
                logger.info(f"create_workflow result: {result}")
                if result["success"]:
                    st.success("Workflow created in n8n successfully!")
                    st.json(result["data"])
                else:
                    logger.error(
                        f"Failed to create workflow: {result['status_code']} {result['message']}")
                    st.error(
                        f"Failed to create workflow: {result['status_code']} {result['message']}")

# --- UI for fetching all workflows ---
st.header("View All n8n Workflows")
if st.button("Get All Workflows"):
    with st.spinner("Fetching all workflows from n8n..."):
        try:
            response = requests.get("http://localhost:8000/get_all_workflows")
            logger.info(
                f"GET /get_all_workflows status: {response.status_code}")
            logger.info(f"GET /get_all_workflows response: {response.text}")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    st.success("Fetched all workflows from n8n!")
                    st.json(data.get("data"))
                else:
                    st.error(
                        f"Failed to fetch workflows: {data.get('error', data)}")
            else:
                st.error(f"API Error: {response.status_code}")
        except Exception as e:
            logger.error(f"Exception while fetching all workflows: {e}")
            st.error(f"Exception: {e}")
