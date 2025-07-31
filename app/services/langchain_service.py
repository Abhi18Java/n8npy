#D:\AI_Project\n8n_wf_creator\app\services\langchain_service.py

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.config import settings
import logging
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
import os

logger = logging.getLogger(__name__)
OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY", settings.openai_api_key)

logger.info("Loading workflow prompt template from app/prompts/workflow_prompt.txt")
try:
    with open("app/prompts/workflow_prompt.txt", "r" , encoding="utf-8") as file:
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
    logger.info("Initializing OpenAI Chat LLM with provided settings.")
    try:
        llm = ChatOpenAI(
            model_name="gpt-4o",
            openai_api_key=settings.openai_api_key,
            temperature=0.7,
            max_tokens=16384,
        )
        logger.info("OpenAI Chat LLM initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI Chat LLM: {e}")
        raise

    logger.info("Setting up ConversationBufferMemory.")
    memory = ConversationBufferMemory(
        memory_key="history",
        input_key="input",
        human_prefix="User",
        ai_prefix="Assistant",
        return_messages=True  # ✅ For chat models, this must be True
    )
    logger.info("ConversationBufferMemory set up.")

    class TokenUsageConversationChain(ConversationChain):
        def run(self, *args, **kwargs):
            # Get messages before running the LLM
            messages_before = memory.chat_memory.messages.copy() if hasattr(memory, 'chat_memory') else []
            num_tokens_input = 0
            if hasattr(self.llm, 'get_num_tokens_from_messages'):
                try:
                    num_tokens_input = self.llm.get_num_tokens_from_messages(messages_before)
                except Exception as e:
                    logger.warning(f"Could not calculate input token usage: {e}")
            result = super().run(*args, **kwargs)
            # Get messages after running the LLM
            messages_after = memory.chat_memory.messages if hasattr(memory, 'chat_memory') else []
            num_tokens_output = 0
            if hasattr(self.llm, 'get_num_tokens_from_messages'):
                try:
                    num_tokens_output = self.llm.get_num_tokens_from_messages(messages_after)
                except Exception as e:
                    logger.warning(f"Could not calculate output token usage: {e}")
                logger.info(f"Input tokens: {num_tokens_input}, Output tokens: {num_tokens_output - num_tokens_input}, Total tokens: {num_tokens_output}")
                print(f"Input tokens: {num_tokens_input}, Output tokens: {num_tokens_output - num_tokens_input}, Total tokens: {num_tokens_output}")
            else:
                logger.warning("LLM does not support token counting.")
            return result

    logger.info("Creating ConversationChain with token usage logging.")
    chain = TokenUsageConversationChain(
        llm=llm,
        prompt=PROMPT,
        memory=memory,
        verbose=True
    )
    logger.info(f"ConversationChain created successfully with chain:{chain}")
    return chain


