import os

from h2o_wave import on, ui
from loguru import logger

from src.generative_ai import llm_query_custom
from src.wave_utils import missing_required_variable_dialog

import asyncio


def initialize_generate_content_app(q):
    logger.info("")
    q.app.generate_content_required_variables = ["Company Name"]

    q.app.h2ogpt = {
        "address": os.getenv("H2OGPT_URL"),
        "api_key": os.getenv("H2OGPT_API_TOKEN"),
    }

    with open("prompts/system_task.txt") as f:
        q.app.summary_prompt = f.read()

    with open('prompts/competitor_prompt.txt') as f:
        q.app.competitor_prompt = f.read()

    with open('prompts/revenue_prompt.txt') as f:
        q.app.revenue_prompt = f.read()

    with open('prompts/h2oai_value_prompt') as f:
        q.app.h2oai_value_prompt = f.read()


def initialize_generate_content_client(q):
    logger.info("")

    q.client.company_name = "Apple"
    q.client.jobs_done = 0


@on()
async def generate_content_ui(q):
    logger.info("")

    q.page["generate_content"] = ui.form_card(
        box="body",
        items=[
            ui.text_l("Enter any company name you're interested in here!"),
            ui.inline(items=[
                ui.textbox(name="company_name", label="", value=q.client.company_name, width="50%"),
                ui.button(name="button_generate_content", label="Generate information!", primary=True)
            ]),

            ui.inline(items=[
                ui.copyable_text(name="company_summary", label="Company overview", multiline=True, height="500px",
                                 value=""),
                ui.copyable_text(name="competitor_info", label="Main competitors", multiline=True, height="500px",
                                 value=""),
            ]),

            ui.inline(items=[
                ui.copyable_text(name="company_revenue", label="Company financials", multiline=True, height="500px",
                                 value=""),
                ui.copyable_text(name="potential_value_add", label="How H2O.ai can help out!", multiline=True,
                                 height="500px", value=""),
            ])
        ]
    )


async def generate_specific_content(q, card, system_prompt):
    card.value = await q.run(llm_query_custom, system_prompt,  q.client.company_name, q.app.h2ogpt)
    await q.page.save()

    q.client.jobs_done += 1
    if q.client.jobs_done == 4:
        q.page["meta"].dialog = None
        await q.page.save()


@on()
async def button_generate_content(q):
    logger.info("User has clicked the Generate Content button")

    q.page["generate_content"].company_summary.value = ""
    q.page["generate_content"].competitor_info.value = ""
    q.page["generate_content"].company_revenue.value = ""
    q.page["generate_content"].potential_value_add.value = ""

    # Check that all required variables from the user are not None or Empty Strings
    for v in q.app.generate_content_required_variables:
        if missing_required_variable_dialog(q, v):
            return

    q.client.jobs_done = 0
    q.page["meta"].dialog = ui.dialog(
        title="H2OGPT is researching the company, please wait :)",
        items=[ui.image(title="", path=q.app.load, width="550px"), ],
        blocking=True
    )
    await q.page.save()

    asyncio.gather(
        generate_specific_content(q, q.page["generate_content"].company_summary, q.app.summary_prompt),
        generate_specific_content(q, q.page["generate_content"].competitor_info, q.app.competitor_prompt),
        generate_specific_content(q, q.page["generate_content"].company_revenue, q.app.revenue_prompt),
        generate_specific_content(q, q.page["generate_content"].potential_value_add, q.app.h2oai_value_prompt)
    )


