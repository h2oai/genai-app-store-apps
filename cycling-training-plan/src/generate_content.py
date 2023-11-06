import os

from h2o_wave import on, ui, Q
from h2ogpt_client import Client
from loguru import logger

from src.wave_utils import clear_cards, long_process_dialog


def initialize_generate_content_app(q):
    logger.info("")
    q.app.h2ogpt = {"address": os.getenv(
        "H2OGPT_URL"), "api_key": os.getenv("H2OGPT_API_TOKEN")}
    q.app.system_prompt = f"You are an export at quick and easy cycling training plan." \
        f"Do not explain yourself, just return the text of the cycling training plan."


def initialize_generate_content_client(q):
    logger.info("")
    q.client.weight = '170'
    q.client.heightFt = '5'
    q.client.heightInch = '10'
    q.client.weekFreq = '4x'
    q.client.conditionLevel = 'Beginner'
    q.client.setFtp = False
    q.client.currentFTP = '150'
    q.client.targetFTP = '210'
    q.client.timeGoal = False
    q.client.weeks = '8'


async def side_input_generate_content(q):
    logger.info("")
    clear_cards(q)

    # Options for plan
    weekFreq = ['2x', '3x', '4x', '5x', '6x']
    conditionLevel = ['Beginner', 'Intermediate', 'Racer']

    # User input form
    q.page['help'] = ui.form_card(
        box='left',
        items=[
            ui.text_l("<b>Get Started</b>"),
            ui.text(
                "Give some background about yourself to create a training strategy."),
            ui.textbox(
                name='weight',
                label='Your weight in pounds',
                width='100%',
                value=q.client.weight,

            ),

            ui.label(label='How tall are you?'),

            ui.inline(justify='around',
                      items=[
                          ui.textbox(
                              name='heightFT',
                              label='Feet',
                              width='49%',
                              value=q.client.heightFt,

                          ),
                          ui.textbox(
                              name='heightInch',
                              label='Inches',
                              width='49%',
                              value=q.client.heightInch,

                          ),
                      ]),

            ui.dropdown(name='conditionLevel', label='How experienced are you?', value=q.client.conditionLevel, choices=[
                ui.choice(name=i, label=i) for i in conditionLevel]),

            ui.dropdown(name='weekFreq', label='How often do you want to get training per week?', value=q.client.weekFreq, choices=[
                ui.choice(name=i, label=i) for i in weekFreq]),

            ui.toggle(
                name='reduceWeights',
                label='Do you want reduce weight recommendation?',
                value=q.client.reduceWeights),

            ui.toggle(
                name='setFtp',
                label='Do you want improve your FTP?',
                trigger=True,
                value=q.client.setFtp),

            ui.inline(
                justify='center',
                items=[
                    ui.textbox(
                        name='currentFTP',
                        label='Your current FTP',
                        width='49%',
                        value=q.client.currentFTP,
                        visible=q.client.setFtp
                    ),
                    ui.textbox(
                        name='targetFTP',
                        label='Your target FTP',
                        width='49%',
                        value=q.client.targetFTP,
                        visible=q.client.setFtp
                    ),
                ]
            ),

            ui.toggle(
                name='timeGoal',
                trigger=True,
                label='Do you want training for a certain number of weeks?',
                value=q.client.timeGoal),

            ui.inline(
                justify='center',
                items=[
                    ui.textbox(
                        name='weeks',
                        label='How many weeks do you want a training plan?',
                        width='100%',
                        value=q.client.weeks,
                        visible=q.client.timeGoal
                    ),
                ]
            ),



            ui.inline(justify='center', items=[
                ui.button(
                      name='generate_prompt',
                      label='Generate Training Plan',
                      primary=True)
            ]),

        ]
    )


@on()
async def generate_prompt(q: Q):
    logger.info("")
    timeGoal = ""
    if q.client.timeGoal:
        timeGoal = f'''* Training weeks: {q.client.weeks}'''

    setFtp = ""
    if q.client.setFtp:
        setFtp = f'''* Improve FTP: from {q.client.currentFTP} to {q.client.targetFTP}'''

    reduceWeight = ""
    if q.client.setFtp:
        reduceWeight = "* Recommend healthy reduce weight which help with my training plan"

    prompt = f'''Create an optimal cycling training program for a {q.client.conditionLevel} and an average working individual who stands at {q.client.heightFt} feet and {q.client.heightInch} inches tall and weighs {q.client.weight} pounds, utilizing the following setup:

* Training frequency per week: {q.client.weekFreq}
{timeGoal}
{setFtp}
{reduceWeight}
'''

    q.client.prompt = prompt

    q.page["training_plan"] = ui.form_card(
        box="right",
        items=[
            ui.text(content="", name="training_plan")
        ]
    )

    q.client.waiting_dialog = "H2OGPT is creating your training plan!"
    await long_process_dialog(q)

    q.page["training_plan"].training_plan.content = await q.run(
        llm_query_custom, q.app.system_prompt, q.client.prompt, q.app.h2ogpt
    )
    await q.page.save()


def llm_query_custom(system_prompt, prompt, connection_details):
    logger.info(connection_details)
    logger.info("")
    try:
        logger.debug(system_prompt)
        logger.debug(prompt)

        client = Client(
            connection_details["address"], h2ogpt_key=connection_details["api_key"])

        text_completion = client.text_completion.create(
            system_prompt=system_prompt,
        )
        response = text_completion.complete_sync(prompt)

        logger.debug(response.strip())
        return response.strip()

    except Exception as e:
        logger.error(e)
        return ""
