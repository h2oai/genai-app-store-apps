from h2o_wave import on, ui, Q
from src.wave_utils import clear_cards, missing_required_variable_dialog
from loguru import logger
from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage
import asyncio
import os


def initialize_generate_content_app(q):
    logger.info("")
    q.app.generate_content_required_variables = ["Marketing Content to Review"]

@on()
async def generate_content_ui(q):
    logger.info("")

    q.page["generate_content"] = ui.form_card(
        box="body",
        items=[
            ui.text_xl(content="Specify your language preferences"),
            ui.inline(items=[
                ui.toggle(name="oxford_comma", label="Oxford Comma", value=q.client.oxford_comma),
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

Learn how the makers at H2O.ai are building internal tools to solve reall use cases using H2O Wave and h2oGPTe. We will walk through an end-to-end use case and discuss how to incorporate business rules and generated content to rapidly develop custom AI apps using only Python APIs.
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

    # update_system_prompt(q)

    q.client.prompt = q.client.marketing_content_to_review
    q.client.chatbot_interaction = ChatBotInteraction(user_message=q.client.prompt)

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))
    await q.run(chat, q.client.chatbot_interaction, update_system_prompt(q))
    await update_ui
    await q.page.save()

    # q.page["generate_content"].marketing_content_improved.value = await q.run(
    #     llm_query_custom, q.client.system_prompt, q.client.prompt, q.app.h2ogpte
    # )

# def llm_query_custom(system_prompt, prompt, connection_details):
#     logger.info("")
#     try:
#         logger.debug(system_prompt)
#         logger.debug(prompt)

#         client = Client(connection_details["address"], h2ogpt_key=connection_details["api_key"])

#         text_completion = client.text_completion.create(
#             system_prompt=system_prompt,
#             visible_models=['gpt-3.5-turbo-0613']
#         )
#         response = text_completion.complete_sync(prompt)

#         logger.debug(response.strip())
#         return response.strip()

#     except Exception as e:
#         logger.error(e)
#         return ""


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
    return q.client.system_prompt
    

async def stream_updates_to_ui(q: Q):
    """
    Update the app's UI every 1/10th of a second with values from our chatbot interaction
    :param q: The query object stored by H2O Wave with information about the app and user behavior.
    """

    while q.client.chatbot_interaction.responding:
        q.page["generate_content"].marketing_content_improved.value = q.client.chatbot_interaction.content_to_show
        await q.page.save()
        await q.sleep(0.1)

    q.page["generate_content"].marketing_content_improved.value = q.client.chatbot_interaction.content_to_show
    await q.page.save()

def chat(chatbot_interaction, customized_prompt):
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
        print(customized_prompt)
        with client.connect(chat_session_id) as session:
            session.query(
                system_prompt = customized_prompt,
                message=chatbot_interaction.user_message,
                timeout=60,
                rag_config={"rag_type": "llm_only"},
                callback=stream_response,
                llm='gpt-3.5-turbo-0613'
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
