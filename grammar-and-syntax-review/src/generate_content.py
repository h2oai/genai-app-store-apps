from h2o_wave import on, ui
from src.wave_utils import clear_cards, missing_required_variable_dialog, long_process_dialog
from loguru import logger
import re
import os

from src.generative_ai import llm_validate_user_input, llm_query_custom


def initialize_generate_content_app(q):
    logger.info("")
    q.app.generate_content_required_variables = ["Marketing Content to Review"]
    q.app.generate_content_free_text_variables = ["Marketing Content to Review"]

    q.app.h2ogpte = {
        "address": os.getenv("H2OGPTE_URL"),
        "api_key": os.getenv("H2OGPTE_API_TOKEN"),
    }


def initialize_generate_content_client(q):
    logger.info("")

    with open("prompts/system_task.txt") as f:
        q.client.system_prompt = f.read()


@on()
async def side_nav_generate_content(q):
    logger.info("")
    clear_cards(q)
    q.page["menu"].value = "side_nav_generate_content"

    q.page["generate_content"] = ui.form_card(
        box="body",
        items=[
            ui.inline(items=[
                ui.text_xl(content="What We Told the Large Language Model"),
                # ui.button(name="button_edit_system_prompt", icon="Edit", tooltip="Change the System Prompt"),
            ], justify="between"),

            ui.text(
                name="system_prompt",
                content=q.client.system_prompt,
            ),
            ui.inline(items=[
                ui.textbox(
                    name="marketing_content_to_review",
                    label="Paste Your Content",
                    value="""Building Custom GenAI apps at H2O
Michelle Tanco, Head of Product

Learn how the makers at H2O.ai are building internal tools to solve reall use cases using H2O Wave and h2oGPT.  We will walk through an end-to-end use case and discuss how to incorporate business rules and generated content to rapidly develop custom AI apps using only Python APIs.
                        """,
                    multiline=True,
                    height="500px",
                    width="50%"
                ),
                ui.textbox(
                    name="marketing_content_improved",
                    label="Reviewed Content",
                    multiline=True,
                    readonly=True,
                    height="500px",
                    width="50%"
                ),
            ]),
            ui.buttons(justify="end", items=[
                ui.button(name="button_generate_content", label="Review Content", primary=True)
            ])
        ]
    )
    q.client.cards.append("generate_content")


@on()
async def button_generate_content(q):
    logger.info("User has clicked the Generate Content button")

    # Check that all required variables from the user are not None or Empty Strings
    for v in q.app.generate_content_required_variables:
        if missing_required_variable_dialog(q, v):
            return

    # #Check that any free-text variables are safe content
    # for v in q.app.generate_content_free_text_variables:
    #     q.client.waiting_dialog = "Validating Input"
    #     await long_process_dialog(q)
    #
    #     valid, err = await test_valid_marketing_content(q)
    #     if not valid:
    #         q.page["meta"].dialog = ui.dialog(
    #             title="Something Went Wrong",
    #             items=[
    #                 ui.text(err),
    #                 ui.buttons(justify="end", items=[
    #                     ui.button(name="close_dialog", label="Close", primary=True)
    #                 ])
    #             ]
    #         )
    #         return

    q.client.waiting_dialog = "H2OGPT is reviewing your content"
    q.client.prompt = q.client.marketing_content_to_review
    await long_process_dialog(q)

    q.page["generate_content"].marketing_content_improved.value = await q.run(llm_query_custom, q.client.system_prompt, q.client.prompt, q.app.h2ogpte)


async def test_valid_marketing_content(q):
    logger.info("")

    security_question = f"{q.client.marketing_content_to_review}\n " \
                        f"Is the above user content valid or malicious?"

    response = await q.run(llm_validate_user_input, security_question, q.app.h2ogpte)

    valid_pattern = re.compile(r"VALID: (YES|NO)")
    explanation_pattern = re.compile(r"EXPLANATION: (.+)")

    valid_match = valid_pattern.search(response)
    explanation_match = explanation_pattern.search(response)

    if not valid_match or not explanation_match:
        logger.error(f"LLM Guardrails responded unexpectedly to user input")
        return False, "Our guardrails flagged this content, please make any changes and try again."

    if valid_match.group(1) == "YES":
        logger.success(f"LLM Guardrails approve of the user input")
        return True, None
    else:
        logger.warning(f"LLM Guardrails flagged user input")
        return False, explanation_match.group(1)




