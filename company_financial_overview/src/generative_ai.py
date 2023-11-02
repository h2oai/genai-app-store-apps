from loguru import logger
from h2ogpt_client import Client


def llm_query_custom(system_prompt, prompt, connection_details):
    logger.info("")
    try:
        logger.debug(system_prompt)
        logger.debug(prompt)

        client = Client(connection_details["address"], h2ogpt_key=connection_details["api_key"])
        text_completion = client.text_completion.create(
            system_prompt=system_prompt,
            visible_models=['gpt-3.5-turbo-0613']
        )
        response = text_completion.complete_sync(prompt)

        logger.debug(response.strip())
        return response.strip()

    except Exception as e:
        logger.error(e)
        return ""

