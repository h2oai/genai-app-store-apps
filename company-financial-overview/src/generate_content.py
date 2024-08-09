import os
from h2o_wave import on, ui, Q
from loguru import logger
from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage
from src.wave_utils import missing_required_variable_dialog
import asyncio


def initialize_generate_content_app(q):
    logger.info("")
    q.app.generate_content_required_variables = ["Company Name"]

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


@on()
async def generate_content_ui(q):
    logger.info("")

    q.page["generate_content"] = ui.form_card(
        box="body",
        items=[
            ui.text_l("Enter any company name you're interested in here!"),
            ui.inline(items=[
                ui.textbox(name="company_name", label="", value=q.client.company_name, width="82%"),
                ui.button(name="button_generate_content", label="Generate information!", primary=True)
            ]),

            ui.inline(items=[
                ui.copyable_text(name="company_summary", label="Company overview", multiline=True, height="400px",
                                 value="", width="50%"),
                ui.copyable_text(name="competitor_info", label="Main competitors", multiline=True, height="400px",
                                 value="", width="50%"),
            ]),

            ui.inline(items=[
                ui.copyable_text(name="company_revenue", label="Company financials", multiline=True, height="400px",
                                 value="", width="50%"),
                ui.copyable_text(name="potential_value_add", label="How H2O.ai can help out!", multiline=True,
                                 height="400px", value="", width="50%"),
            ])
        ]
    )


@on()
async def button_generate_content(q):
    logger.info("User has clicked the Generate Content button")

    q.page["generate_content"].company_summary.value= ""
    q.page["generate_content"].competitor_info.value = ""
    q.page["generate_content"].company_revenue.value = ""
    q.page["generate_content"].potential_value_add.value = ""

    # Check that all required variables from the user are not None or Empty Strings
    for v in q.app.generate_content_required_variables:
        if missing_required_variable_dialog(q, v):
            return

    asyncio.gather(
        generate_specific_content(q, q.page["generate_content"].company_summary, q.app.summary_prompt, "summary"),
        generate_specific_content(q, q.page["generate_content"].competitor_info, q.app.competitor_prompt, "competitor"),
        generate_specific_content(q, q.page["generate_content"].company_revenue, q.app.revenue_prompt, "revenue"),
        generate_specific_content(q, q.page["generate_content"].potential_value_add, q.app.h2oai_value_prompt, "value")
    )


async def generate_specific_content(q, textbox, questions, topic):
    prompt = f'''Answer the following question about {q.client.company_name}: {questions} '''
    q.client[f"chatbot_interaction_{topic}"] = ChatBotInteraction(user_message=prompt)

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q, textbox, topic))
    await q.run(chat, q.client[f"chatbot_interaction_{topic}"])
    await update_ui


async def stream_updates_to_ui(q: Q, textbox, topic):
    """
    Update the app's UI every 1/10th of a second with values from our chatbot interaction
    :param q: The query object stored by H2O Wave with information about the app and user behavior.
    """

    while q.client[f"chatbot_interaction_{topic}"].responding:
        textbox.value = q.client[f"chatbot_interaction_{topic}"].content_to_show
        await q.page.save()
        await q.sleep(0.1)

    textbox.value = q.client[f"chatbot_interaction_{topic}"].content_to_show
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

        collection_id = client.create_collection("Temp for Company Financial Overview", "")
        chat_session_id = client.create_chat_session(collection_id=collection_id)
        print("USER MESSSAGEEEEE", chatbot_interaction.user_message)
        with client.connect(chat_session_id) as session:
            session.query(
                system_prompt="You are h2oGPTe, an expert question-answering AI system created by H2O.ai that "
                              "performs like GPT-4 by OpenAI. I will give you a $200 tip if you answer the question "
                              "correctly to the best of your capabilities.",
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
