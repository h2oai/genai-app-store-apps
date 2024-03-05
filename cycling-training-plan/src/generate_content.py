import os
import asyncio
from h2o_wave import on, ui, Q
from h2ogpte import H2OGPTE
from loguru import logger
from h2ogpte.types import ChatMessage, PartialChatMessage
from src.wave_utils import clear_cards, long_process_dialog

def initialize_generate_content_client(q):
    logger.info("")
    q.client.weight = '170'
    q.client.heightFt = '5'
    q.client.heightInch = '10'
    q.client.weekFreq = '4x'
    q.client.conditionLevel = 'Beginner'
    q.client.setFtp = False
    q.client.reduceWeight = False
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
                name='reduceWeight',
                label='Do you want reduce weight recommendation?',
                value=q.client.reduceWeight),

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
    if q.client.reduceWeight:
        reduceWeight = "* Recommend healthy ways to lose weight that will support my workout regimen and my goal weight"

    prompt = f'''Create an optimal cycling training program for a {q.client.conditionLevel} and an average working individual who stands at {q.client.heightFt} feet and {q.client.heightInch} inches tall and weighs {q.client.weight} pounds, utilizing the following setup:

* Training frequency per week: {q.client.weekFreq}
{timeGoal}
{setFtp}
{reduceWeight}

In response use table for week plan and make structured with markdown.
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

    q.client.chatbot_interaction = ChatBotInteraction(user_message=q.client.prompt)

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))
    await q.run(chat, q.client.chatbot_interaction)
    await update_ui

    # q.page["training_plan"].training_plan.content = await q.run(
    #     llm_query_custom, q.app.system_prompt, q.client.prompt, q.app.h2ogpt
    # )
    await q.page.save()


async def stream_updates_to_ui(q: Q):
    """
    Update the app's UI every 1/10th of a second with values from our chatbot interaction
    :param q: The query object stored by H2O Wave with information about the app and user behavior.
    """

    while q.client.chatbot_interaction.responding:
        q.page["training_plan"].training_plan.content = q.client.chatbot_interaction.content_to_show
        await q.page.save()
        await q.sleep(0.1)

    q.page["training_plan"].training_plan.content = q.client.chatbot_interaction.content_to_show
    await q.page.save()


def chat(chatbot_interaction):
    """
    Send the user's message to the LLM and save the response
    :param chatbot_interaction: Details about the interaction between the user and the LLM
    :param chat_session_id: Chat session for these messages
    """

    def stream_response(message):
        """
        This function is called by the blocking H2OGPTE function periodically for updating the UI
        :param message: response from the LLM, this is either a partial or completed response
        """
        chatbot_interaction.update_response(message)

    try:
        client = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))

        collection_id = client.create_collection("temp", "")
        chat_session_id = client.create_chat_session(collection_id)

        with client.connect(chat_session_id) as session:
            session.query(
                system_prompt = f"You are an export at quick and easy cycling training plan." \
        f"Do not explain yourself, just return the text of the cycling training plan.",
                message=chatbot_interaction.user_message,
                timeout=60,
                rag_config={"rag_type": "llm_only"},
                callback=stream_response,
            )

        client.delete_collections([collection_id])
        client.delete_chat_sessions([chat_session_id])

    except Exception as e:
        logger.error(e)
        return f""


class ChatBotInteraction:
    def __init__(self, user_message) -> None:
        self.user_message = user_message
        self.responding = True

        self.llm_response = ""
        self.content_to_show = "🟡"

    def update_response(self, message):
        if isinstance(message, ChatMessage):
            self.content_to_show = message.content
            self.responding = False
        elif isinstance(message, PartialChatMessage):
            if message.content != "#### LLM Only (no RAG):\n":
                self.llm_response += message.content
                self.content_to_show = self.llm_response + " 🟡"
