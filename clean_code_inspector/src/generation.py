from h2o_wave import Q
from h2ogpt_client import Client
from loguru import logger
from typing import Optional

from src.prompts import get_system_prompt, get_default_prompt, get_context
from src.utils import get_concatenated_str


def llm_query(q: Q, prompt: Optional[str]) -> str:
    logger.info("Prompting LLM with user query.")

    system_prompt = get_system_prompt()
    if prompt is None:
        prompt = get_default_prompt(q)

    context = get_context(q=q)

    try:
        logger.debug(prompt)
        client = Client(q.app.h2ogpt_url, h2ogpt_key=q.app.h2ogpt_key)
        llm = client.text_completion.create(
            visible_models=["gpt-3.5-turbo-0613"],
            system_prompt=system_prompt,
            text_context_list=context
        )
        response = llm.complete_sync(prompt)
        return response.strip()

    except Exception as e:
        logger.error(e)
        return ""


def get_response(q: Q, prompt: Optional[str]) -> str:
    response = llm_query(
        q=q,
        prompt=prompt
    )
    return response
