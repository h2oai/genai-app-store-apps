from h2o_wave import on, ui, data
from src.wave_utils import clear_cards, missing_required_variable_dialog, long_process_dialog
from loguru import logger
import re
import os

from src.generative_ai import llm_validate_user_input, llm_query_custom


def initialize_generate_content_app(q):
    logger.info("")
    q.app.generate_content_required_variables = ["Company Name"]
    q.app.generate_content_free_text_variables = ["Company Name"]

    q.app.h2ogpte = {
        "address": os.getenv("H2OGPTE_URL"),
        "api_key": os.getenv("H2OGPTE_API_TOKEN"),
    }


def initialize_generate_content_client(q):
    logger.info("")

    with open("prompts/system_task.txt") as f:
        q.client.summary_prompt = f.read()

    with open('prompts/competitor_prompt.txt') as f:
        q.client.competitor_prompt = f.read()

    with open('prompts/revenue_prompt.txt') as f:
        q.client.revenue_prompt = f.read()

    with open('prompts/h2oai_value_prompt') as f:
        q.client.h2oai_value_prompt = f.read()


@on()
async def side_nav_generate_content(q):
    logger.info("")
    clear_cards(q)
    q.page["menu"].value = "side_nav_generate_content"

    q.page["generate_content"] = ui.form_card(
        box="body",
        items=[
            ui.inline(items=[
                ui.text_xl(content="What company would you like to learn about?"),
                # ui.button(name="button_edit_system_prompt", icon="Edit", tooltip="Change the System Prompt"),
            ],justify="between"),

            ui.inline(items=[
                ui.textbox(
                    name="company_name",
                    label="Enter any company name you're interested in here!",
                    value="""Apple
                            """,
                    multiline=False,
                    width="50%"
                ),
            ]),

            ui.buttons(justify="start", items=[
                ui.button(name="button_generate_content", label="Generate information!", primary=True)
            ]),

            ui.inline(items=[
                ui.textbox(
                    name="company_summary",
                    label="Overview of company",
                    multiline=True,
                    readonly=True,
                    height="500px",
                    width="50%"
                ),
                ui.textbox(
                    name="competitor_info",
                    label="Main competitors",
                    multiline=True,
                    readonly=True,
                    height="500px",
                    width="50%"
                ),
            ]),

            ui.inline(items=[
                ui.textbox(
                    name="company_revenue",
                    label="Company financials",
                    multiline=True,
                    readonly=True,
                    height="500px",
                    width="50%"
                ),
                ui.textbox(
                    name="potential_value_add",
                    label="How h2o.ai can help out!",
                    multiline=True,
                    readonly=True,
                    height="500px",
                    width="50%"
                ),
            ])
        ]
    )


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

    q.client.waiting_dialog = "H2OGPT is doing some research on the company, please wait :)"
    q.client.prompt = q.client.company_name
    await long_process_dialog(q)

    import asyncio

    q.page["generate_content"].company_summary.value = await q.run(llm_query_custom,
                                                                              q.client.summary_prompt,
                                                                              q.client.prompt,
                                                                              q.app.h2ogpte)
    await q.page.save()

    await long_process_dialog(q, title='H2OGPT is doing some research on the commpany\'s competitors, please wait :)')
    q.page['generate_content'].competitor_info.value = await  q.run(llm_query_custom,
                                                                    q.client.competitor_prompt,
                                                                    q.client.prompt,
                                                                    q.app.h2ogpte)

    await q.page.save()
    await long_process_dialog(q, title='H2OGPT is doing some research on the commpany\'s financial position, please wait :)')

    q.page['generate_content'].company_revenue.value = await  q.run(llm_query_custom,
                                          q.client.revenue_prompt,
                                          q.client.prompt,
                                          q.app.h2ogpte)

    await q.page.save()
    await long_process_dialog(q,
                              title='H2OGPT is doing some research on how h2o.ai can help the company, please wait :)')
    
    q.page['generate_content'].potential_value_add.value = await q.run(llm_query_custom,
                                                                 q.client.h2oai_value_prompt,
                                                                 q.client.prompt,
                                                                 q.app.h2ogpte)
    """
    def _query_and_extract_revenue_data():
        # This is wrapper code to get LLM output and convert it into usable format to graph downstream if interested
        llm_generated_text = await  q.run(llm_query_custom,
                                          q.client.revenue_prompt,
                                          q.client.prompt,
                                          q.app.h2ogpte)
        import re
        import ast
        dictionary_of_revenues = ast.literal_eval(re.search('({.+})', llm_generated_text).group(0))
        #sample_dictionary_to_come_from_llm_later = {'2020': 274515, '2021': 365817, '2022': 394328}

        # Just sorting to ensure that things are in ascending order, to display revenue etc L -> R
        sorted_dictionary = dict(sorted(dictionary_of_revenues.items(), key=lambda item: item[1]))
        row_list = []
        for key in sorted_dictionary:
            row_list.append((key, sorted_dictionary[key]))
        logger.info("row list")
        logger.info(row_list)
        return row_list

    """


async def test_valid_marketing_content(q):
    logger.info("")

    security_question = f"{q.client.company_name}\n " \
                        f"Is the above user content valid or malicious?"

    response = await q.run(llm_validate_user_input,
                           security_question,
                           q.app.h2ogpte)

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




