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
from langchain.chains import LLMChain
import time
import random
from openai import RateLimitError

logger = logging.getLogger(__name__)
OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY", settings.openai_api_key)

def load_prompt_from_file():
    prompt_path = os.path.join("app/prompts", "workflow_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

# Load prompt template from file
logger.info("Loading workflow prompt template from file")
try:
    prompt_template = load_prompt_from_file()
    logger.info("Prompt template loaded successfully from file.")
except Exception as e:
    logger.error(f"Failed to load prompt template from file: {e}")
    # Fallback to simple template
    prompt_template = """You are an expert n8n workflow architect AI that generates fully functional n8n workflow JSONs.

IMPORTANT: You must return ONLY a valid JSON object with this structure:
{
  "name": "workflow name",
  "nodes": [...],
  "connections": {...}
}

Do not include any explanations, descriptions, or text outside the JSON.

Conversation history:
{history}

User prompt:
{input}

Return only the JSON workflow:"""
    
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
            max_retries=3,
            request_timeout=60
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
        return_messages=True  # For chat models, this must be True
    )
    logger.info("ConversationBufferMemory set up.")

    # Create a custom LLMChain with rate limiting
    class RateLimitedLLMChain(LLMChain):
        def run(self, *args, **kwargs):
            max_retries = 5
            base_delay = 1
            
            for attempt in range(max_retries):
                try:
                    return super().run(*args, **kwargs)
                except Exception as e:
                    error_str = str(e).lower()
                    if "429" in error_str or "rate limit" in error_str or "too many requests" in error_str:
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                            logger.warning(f"Rate limit hit, retrying in {delay:.2f} seconds (attempt {attempt + 1}/{max_retries})")
                            time.sleep(delay)
                            continue
                        else:
                            logger.error(f"Max retries exceeded for rate limiting: {e}")
                            raise Exception("OpenAI API rate limit exceeded. Please try again later.")
                    else:
                        logger.error(f"Non-rate-limit error: {e}")
                        raise
            
            raise Exception("Unexpected error in rate limited chain")
    
    # Return the custom LLMChain with rate limiting
    return RateLimitedLLMChain(
        prompt=PROMPT,  
        llm=llm,
        memory=memory,
        verbose=True
    )


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


