from h2o_wave import Q
from h2ogpt_client import Client
from loguru import logger
from typing import Optional


def llm_query(q: Q, prompt: Optional[str], method_level_checks, class_level_checks) -> str:
    logger.info("Prompting LLM with user query.")

    system_prompt = ("Assume the role of a Python clean code expert, offering clear guidance and easily digestible "
                     "explanations to novice Python developers. While you can provide general advice on clean code "
                     "principles, your detailed assistance is limited to the class or method level. If presented with "
                     "code outside this scope, kindly communicate your expertise and focus on class or method level "
                     "code.")


    if prompt is None:
        if q.client.user_code == "" or q.client.user_code is None:
            prompt = ("The developer wants to get general advice on clean code principles but has forgotten to provide "
                      "a code snippet. Remind them to do so. ")
        else:
            prompt = (f"The developer want to get general advice on clean code principles for the given code snippet \n "
                      f"{q.client.user_code}. Verify whether this constitutes valid Python code. If not, kindly remind "
                      f"the developer to rectify it.\n Besides that, show the code snippet in a manner that adheres to "
                      f"clean coding principles.")

    context = []
    if method_level_checks or class_level_checks:
        context += [f"With the provided code snippet ({q.client.user_code}) from the developer, the user seeks to "
                    f"verify adherence to the following Python clean code rules, "]
        if method_level_checks:
            context += [f"on the method-level: {method_level_checks} "]
        if class_level_checks:
            context += [f"on the class-level: {class_level_checks} "]

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


def get_rules(level_checks):
    if len(level_checks) > 0:
        selection = level_checks[0]
        for n in range(1, len(level_checks)):
            selection += ", "
            selection += level_checks[n]
    else:
        selection = None
    return selection


def get_response(q: Q, prompt: Optional[str]) -> str:

    method_checks = None
    if q.client.method_level_checks is not None:
        method_checks = get_rules(q.client.method_level_checks)

    class_checks = None
    if q.client.class_level_checks is not None:
        class_checks = get_rules(q.client.class_level_checks)

    response = llm_query(
        q=q,
        prompt=prompt,
        method_level_checks=method_checks,
        class_level_checks=class_checks
    )
    return response
