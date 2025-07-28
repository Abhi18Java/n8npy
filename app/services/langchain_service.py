from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)

logger.info("Loading workflow prompt template from app/prompts/workflow_prompt.txt")
try:
    with open("app/prompts/workflow_prompt.txt", "r") as file:
        prompt_template = file.read()
    logger.info("Prompt template loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load prompt template: {e}")
    prompt_template = ""

PROMPT = PromptTemplate(
    input_variables=["history", "input"],
    template=prompt_template
)

def get_llm_chain():
    logger.info("Initializing OpenAI LLM with provided settings.")
    try:
        llm = OpenAI(
            openai_api_key=settings.openai_api_key,
            temperature=0.7
        )
        logger.info("OpenAI LLM initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI LLM: {e}")
        raise

    logger.info("Setting up ConversationBufferMemory.")
    memory = ConversationBufferMemory(
        memory_key="history",           # ✅ REQUIRED to match the prompt
        input_key="input",              # optional but good for clarity
        human_prefix="User",
        ai_prefix="Assistant",
        return_messages=False           # if you're not using ChatPromptTemplate
    )
    logger.info("ConversationBufferMemory set up.")

    logger.info("Creating ConversationChain.")
    chain = ConversationChain(
        llm=llm,
        prompt=PROMPT,
        memory=memory,
        verbose=True
    )
    logger.info("ConversationChain created and ready.")
    return chain
