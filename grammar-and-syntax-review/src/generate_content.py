from h2o_wave import on, ui
from src.wave_utils import clear_cards, missing_required_variable_dialog, long_process_dialog
from loguru import logger

from h2ogpt_client import Client

import os


def initialize_generate_content_app(q):
    logger.info("")
    q.app.generate_content_required_variables = ["Marketing Content to Review"]

    q.app.h2ogpte = {
        "address": os.getenv("H2OGPT_URL"),
        "api_key": os.getenv("H2OGPT_API_TOKEN"),
    }


@on()
async def generate_content_ui(q):
    logger.info("")

    q.page["generate_content"] = ui.form_card(
        box="body",
        items=[
            ui.text_xl(content="Specify your language preferences"),
            ui.inline(items=[
                ui.toggle(name="oxford_comma", label="Oxford Comma",
                          value=q.client.oxford_comma),
                ui.dropdown(name="case", label="Case", value=q.client.case, choices=[
                    ui.choice(c, c) for c in ["Sentence Case", "Title Case", "Upper Case", "Lower Case"]
                ])
            ],),
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
                ui.button(name="button_generate_content",
                          label="Review Content", primary=True)
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

    update_system_prompt(q)

    q.client.waiting_dialog = "H2OGPT is reviewing your content!"
    q.client.prompt = q.client.marketing_content_to_review
    await long_process_dialog(q)

    q.page["generate_content"].marketing_content_improved.value = await q.run(
        llm_query_custom, q.client.system_prompt, q.client.prompt, q.app.h2ogpte
    )


def llm_query_custom(system_prompt, prompt, connection_details):
    logger.info("")
    try:
        logger.debug(system_prompt)
        logger.debug(prompt)

        client = Client(
            connection_details["address"], h2ogpt_key=connection_details["api_key"])

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


def update_system_prompt(q):
    logger.info("")

    if q.client.oxford_comma:
        oxford_value = "Always"
    else:
        oxford_value = "Never"

    q.client.system_prompt = f"You are a helpful bot for reviewing and improving the grammar and syntax of marketing " \
                             f"content. You know you are not a content expert and you always make a few changes " \
                             f"to the meaning and context as possible. You are very good at ensuring that a brand's " \
                             f"language preferences are use:\n" \
                             f"* {oxford_value} use the oxford comma\n" \
                             f"* All text should be {q.client.case}\n" \
                             f"Do not explain yourself, just return the reviewed content."
