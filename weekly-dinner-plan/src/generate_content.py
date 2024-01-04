import os

from h2o_wave import on, ui, Q
from h2ogpt_client import Client
from loguru import logger

from src.wave_utils import clear_cards, long_process_dialog


def initialize_generate_content_app(q):
    logger.info("")
    q.app.h2ogpt = {"address": os.getenv("H2OGPT_URL"), "api_key": os.getenv("H2OGPT_API_TOKEN")}
    q.app.system_prompt = f"You are an export at quick and easy meal planning for dinners." \
                             f"Do not explain yourself, just return the text of the meal plan."


def initialize_generate_content_client(q):
    logger.info("")
    q.client.restrictions = []
    q.client.meals = ['Breakfast', 'Lunch', 'Snack', 'Dinner']
    q.client.cooking_instructions = True
    q.client.adults = '2'
    q.client.children = '2'


@on()
async def side_input_generate_content(q):
    logger.info("")
    clear_cards(q)

    # Options for meal plan
    adults = range(1, 10)
    children = range(1, 10)
    restrictions = ['Vegetarian', 'Vegan', 'Gluten Free', 'Halal', 'Kosher']
    meals = ['Breakfast', 'Lunch', 'Snack', 'Dinner']

    # User input form
    q.page['help'] = ui.form_card(
        box='left',
        items=[
            ui.text_l("<b>Get Started</b>"),
            ui.text("Provide information about your family's eating habits to generate a meal plan."),
            ui.inline(justify='around',
                      items=[
                          ui.dropdown(
                              name='adults',
                              label='Number of Adults',
                              width='32%',
                              value=q.client.adults,
                              choices=[ui.choice(name=str(i), label=str(i)) for i in adults]
                          ),
                          ui.dropdown(
                              name='children',
                              label='Number of Children',
                              width='32%',
                              value=q.client.children,
                              choices=[ui.choice(name=str(i), label=str(i)) for i in children]
                          ),

                          ui.toggle(
                              name='cooking_instructions',
                              label='Cooking Instructions',
                              value=q.client.cooking_instructions)
                      ]),

            ui.checklist(
                name='restrictions',
                label='Restrictions',
                inline=True,
                values=q.client.restrictions,
                choices=[ui.choice(name=i, label=i) for i in restrictions]
            ),

            ui.checklist(
                name='meals',
                label='Meals',
                inline=True,
                values=q.client.meals,
                choices=[ui.choice(name=i, label=i) for i in meals]
            ),

            ui.inline(justify='center', items=[
                ui.button(
                    name='generate_prompt',
                    label='Generate Prompt',
                    primary=True)
            ])
        ]
    )
    q.client.cards.append("help")


@on()
async def generate_prompt(q: Q):
    logger.info("")
    cooking_instructions = ""
    if q.client.cooking_instructions:
        cooking_instructions = "Include cooking instructions for each meal."

    prompt = f'''You are an average working person writing a meal plan for the week with the following restrictions:

* Meals Each Day: {q.client.meals}
* Number of Adults: {q.client.adults}
* Number of Children: {q.client.children}
* Dietary Restrictions: {q.client.restrictions}

Write a one week meal plan geared towards this family. {cooking_instructions} Format your output by using markdown to bold each day of the week.
'''

    q.page['prompt_card'] = ui.form_card(
        box='left',
        items=[
            ui.textbox(
                name='prompt',
                label="Prompt",
                value=prompt,
                multiline=True,
                height='200px'
            ),
            ui.inline(
                justify='center',
                items=[
                    ui.button(
                        name='generate_plan',
                        label='Generate Meal Plan',
                        primary=True)
                ]
            )
        ]
    )

    q.client.cards.append("prompt_card")


@on()
async def generate_plan(q: Q):
    logger.info("")

    q.page["meal_plan"] = ui.form_card(
        box="right",
        items=[
            ui.text(content="", name="meal_plan")
        ]
    )

    q.client.waiting_dialog = "H2OGPT is creating your meal plan!"
    await long_process_dialog(q)

    q.page["meal_plan"].meal_plan.content = await q.run(
        llm_query_custom, q.app.system_prompt, q.client.prompt, q.app.h2ogpt
    )
    await q.page.save()


def llm_query_custom(system_prompt, prompt, connection_details):
    logger.info("")
    try:
        logger.debug(system_prompt)
        logger.debug(prompt)

        client = Client(connection_details["address"], h2ogpt_key=connection_details["api_key"])

        text_completion = client.text_completion.create(
            system_prompt=system_prompt,
        )
        response = text_completion.complete_sync(prompt)

        logger.debug(response.strip())
        return response.strip()

    except Exception as e:
        logger.error(e)
        return ""
