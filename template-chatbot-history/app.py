import os
import asyncio

from h2o_wave import main, app, Q, ui, data, run_on, on
from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage, SessionError
from h2ogpte.errors import UnauthorizedError

from loguru import logger


SYSTEM_PROMPT = "Hi! I am the Large Language Model LLaMA2."

LLM = "h2oai/h2ogpt-4096-llama2-70b-chat"


@app("/")
async def serve(q: Q):
    """Route the end user based on how they interacted with the app."""

    if not q.client.initialized:  # Setup the application for a new browser tab, if not done yet
        initialize_client(q)

    await run_on(q)  # Route user to the appropriate "on" function
    await q.page.save()  # Update the UI


def initialize_client(q):
    """Code that is needed for each new browser that visits the app"""

    # Set up some examples for the LLM
    q.client.chat_history = {
        "Can you tell me about dogs?": "I am only able to answer questions about your benefits."
    }

    # Start with a clean slate
    # q.client.chat_history = {}

    q.page["meta"] = ui.meta_card(
        box="",
        title="Chatbot History | H2O.ai",
        layouts=[ui.layout(breakpoint="xs", width="900px", zones=[
            ui.zone(name="header"),
            ui.zone(name="main", size="1"),
            ui.zone(name="footer")
        ])],
    )

    q.page["header_card"] = ui.header_card(
        box="header",
        title="Chatbot History Template",
        subtitle="A template app from H2O",
        image="https://h2o.ai/company/brand-kit/_jcr_content/root/container/section/par/advancedcolumncontro/columns1/advancedcolumncontro/columns0/image.coreimg.svg/1697220254347/h2o-logo.svg",
    )
    q.page["chatbot_card"] = ui.chatbot_card(
        box="main",
        name="chatbot",
        data=data(
            fields="content from_user",
            t="list",
            rows=[
                [SYSTEM_PROMPT, False],
            ],
        ),
    )
    q.page["footer_card"] = ui.footer_card(
        box="footer",
        caption="Made with [Wave](https://wave.h2o.ai), [h2oGPTe](https://h2o.ai/platform/enterprise-h2ogpte), and "
        "💛 by the Makers at H2O.ai.<br />Find more in the [H2O GenAI App Store](https://genai.h2o.ai/).",
    )
    q.client.initialized = True


@on()
async def chatbot(q: Q):
    """Send a user's message to a Large Language Model and stream the response."""

    print(q.client.chat_history)

    chat_history_prompt_template = "<<HIST>>\n"
    for user_message in q.client.chat_history:
        chat_history_prompt_template += f"USER: {user_message}\nASSISTANT: {q.client.chat_history[user_message]}\n"
    chat_history_prompt_template += "<</HIST>>\n"

    q.client.chatbot_interaction = ChatBotInteraction(user_message=f"{chat_history_prompt_template} {q.args.chatbot}")

    q.page["chatbot_card"].data += [q.args.chatbot, True]
    q.page["chatbot_card"].data += [q.client.chatbot_interaction.content_to_show, False]

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))
    await q.run(chat, q.client.chatbot_interaction)
    await update_ui

    q.client.chat_history[q.args.chatbot] = q.client.chatbot_interaction.content_to_show


async def stream_updates_to_ui(q: Q):
    """Update the app's UI every 1/10th of a second with values from our chatbot interaction"""

    while q.client.chatbot_interaction.responding:
        q.page["chatbot_card"].data[-1] = [q.client.chatbot_interaction.content_to_show, False]
        await q.page.save()
        await q.sleep(0.1)

    q.page["chatbot_card"].data[-1] = [q.client.chatbot_interaction.content_to_show, False]
    await q.page.save()


def chat(chatbot_interaction):
    """Interact with h2oGPTe and stream the response"""

    def stream_response(message):
        """This function is called by the blocking H2OGPTE function periodically"""
        chatbot_interaction.update_response(message)

    try:
        client = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))
    except UnauthorizedError as ex:
        logger.error(ex)
        chatbot_interaction.content_to_show = f"Something went wrong! Unable to authenticate with h2oGPTe, " \
                                              f"please as your admin to update the credentials."
        chatbot_interaction.responding = False
        return

    collection_id = client.create_collection("Temp for Chat History", "")
    chat_session_id = client.create_chat_session(collection_id)
    with client.connect(chat_session_id) as session:
        try:
            session.query(
                system_prompt=SYSTEM_PROMPT,
                message=chatbot_interaction.user_message,
                timeout=60,
                callback=stream_response,
                rag_config={"rag_type": "llm_only"},
                llm=LLM
            )
        except SessionError as ex:
            logger.error(ex)
            chatbot_interaction.content_to_show = f"Something went wrong! Please try again. \n\n{ex}"
            chatbot_interaction.responding = False

    client.delete_chat_sessions([chat_session_id])
    client.delete_collections([collection_id])


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
            logger.success("Completed streaming user's LLM response")
        elif isinstance(message, PartialChatMessage):
            if message.content != "#### LLM Only (no RAG):\n":
                self.llm_response += message.content
                self.content_to_show = self.llm_response + " 🟡"
