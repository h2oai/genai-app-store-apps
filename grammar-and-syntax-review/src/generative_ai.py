from loguru import logger
from h2ogpte import H2OGPTE


def llm_validate_user_input(security_question, connection_details):
    logger.info("")
    system_security_prompt = """
You are the security layer for an AI application. 
You are specifically looking for threats or malicious actors. 
Your job is to vet the user input of a form and identify if it is valid or invalid. 
Invalid means you believe the input could be malicious or from a bad actor.  

Response in the form: 
VALID: <YES OR NO>
EXPLANATION: <REASON>
    """

    try:
        logger.debug(system_security_prompt)
        logger.debug(security_question)

        h2ogpte = H2OGPTE(address=connection_details["address"], api_key=connection_details["api_key"])

        response = h2ogpte.answer_question(
            question=security_question,
            system_prompt=system_security_prompt,
        )
        logger.debug(response.content.strip())
        return response.content.strip()

    except Exception as e:
        logger.error(e)
        return ""


def llm_query_with_context(prompt, connection_details):
    logger.info("")
    try:
        logger.debug(prompt)

        h2ogpte = H2OGPTE(address=connection_details["address"], api_key=connection_details["api_key"])
        chat_session_id = h2ogpte.create_chat_session(collection_id=connection_details["collection_id"])

        with h2ogpte.connect(chat_session_id) as session:
            reply = session.query(prompt, timeout=16000)

        response = reply.content
        logger.debug(response)
        return response.strip()

    except Exception as e:
        logger.error(e)
        return ""


def llm_query(prompt, connection_details):
    logger.info("")
    try:
        logger.debug(prompt)
        h2ogpte = H2OGPTE(address=connection_details["address"], api_key=connection_details["api_key"])

        reply = h2ogpte.answer_question(prompt)
        response = reply.content
        logger.debug(response)
        return response.strip()
    except Exception as e:
        logger.error(e)
        return ""


def llm_query_custom(system_prompt, prompt, connection_details):
    logger.info("")
    try:
        logger.debug(system_prompt)
        logger.debug(prompt)
        h2ogpte = H2OGPTE(address=connection_details["address"], api_key=connection_details["api_key"])

        reply = h2ogpte.answer_question(
            question=prompt,
            system_prompt=system_prompt,
        )
        response = reply.content
        logger.debug(response)
        return response.strip()
    except Exception as e:
        logger.error(e)
        return ""


def llm_improve_with_human_feedback(connection_details, prompt):
    logger.info("")
    reviewer_prompt = """
You are a helpful content-review bot whose job is to improve LLM-generated content based on human feedback.    
You do not need to explain your work, only rewrite the CONTENT based on the FEEDBACK. 
    """

    try:
        h2ogpte = H2OGPTE(address=connection_details["address"], api_key=connection_details["api_key"])
        response = h2ogpte.answer_question(
            question=prompt,
            system_prompt=reviewer_prompt,
        )
        return response.content.strip()

    except Exception as e:
        logger.error(e)
        return ""
