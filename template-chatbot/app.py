import os
import asyncio

from h2o_wave import main, app, Q, ui, data, run_on, on
from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage
import h2o_authn

from loguru import logger


@app("/")
async def serve(q: Q):
    """Route the end user based on how they interacted with the app."""

    if not q.client.initialized:  # Setup the application for a new browser tab, if not done yet
        initialize_client(q)

    await run_on(q)  # Route user to the appropriate "on" function
    await q.page.save()  # Update the UI


def initialize_client(q):
    """Code that is needed for each new browser that visits the app"""

    if not q.app.initialized:
        q.app.system_prompt = "Hi! I am a Large Language Model, I am super friendly and here to try and answer any " \
                "question you might have with a casual and fun tone."
        q.app.initialized = True

    q.page["meta"] = ui.meta_card(
        box="",
        title="Chatbot | H2O.ai",
        layouts=[ui.layout(breakpoint="xs", width="900px", zones=[
            ui.zone(name="header"),
            ui.zone(name="main", size="1"),
            ui.zone(name="footer")
        ])],
    )

    q.page["header_card"] = ui.header_card(
        box="header",
        title="Chatbot Template",
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
                [q.app.system_prompt, False],
            ],
        ),
    )
    q.page["footer_card"] = ui.footer_card(
        box="footer",
        caption="Made with [Wave](https://wave.h2o.ai), [h2oGPTe](https://h2o.ai/platform/enterprise-h2ogpte), and "
        "💛 by the Makers at H2O.ai.<br />Find more in the [H2O GenAI App Store](https://genai.h2o.ai/).",
    )

    try:

        client = connect_to_h2ogpte(q.auth.refresh_token)
        q.client.chat_session_id = client.create_chat_session()  # Set up a single chat session ahead of time so users can look in the h2ogpte UI

    except Exception as ex:
        logger.error(ex)
        logger.error(type(ex))
        q.page["meta"].dialog = ui.dialog(
            title="Something went wrong! Please try again later.",
            items=[],
            closable=False,
            blocking=True
        )

    q.client.initialized = True


@on()
async def chatbot(q: Q):
    """Send a user's message to a Large Language Model and stream the response."""

    q.client.chatbot_interaction = ChatBotInteraction(
        user_message=q.args.chatbot, system_prompt=q.app.system_prompt, chat_session_id=q.client.chat_session_id
    )

    q.page["chatbot_card"].data += [q.args.chatbot, True]
    q.page["chatbot_card"].data += [q.client.chatbot_interaction.content_to_show, False]

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))
    await q.run(chat, q.client.chatbot_interaction, q.auth.refresh_token)
    await update_ui


async def stream_updates_to_ui(q: Q):
    """Update the app's UI every 1/10th of a second with values from our chatbot interaction"""

    while q.client.chatbot_interaction.responding:
        q.page["chatbot_card"].data[-1] = [q.client.chatbot_interaction.content_to_show, False]
        await q.page.save()
        await q.sleep(0.1)

    q.page["chatbot_card"].data[-1] = [q.client.chatbot_interaction.content_to_show, False]
    await q.page.save()


def chat(chatbot_interaction, refresh_token):
    """Interact with h2oGPTe and stream the response"""

    def stream_response(message):
        """This function is called by the blocking H2OGPTE function periodically"""
        chatbot_interaction.update_response(message)

    try:
        client = connect_to_h2ogpte(refresh_token)

        with client.connect(chatbot_interaction.chat_session_id) as session:
            session.query(
                system_prompt=chatbot_interaction.system_prompt,
                message=chatbot_interaction.user_message,

                timeout=60,
                callback=stream_response,
                rag_config={"rag_type": "llm_only"},

            )

    except Exception as ex:
        logger.error(ex)
        chatbot_interaction.content_to_show = f"Something went wrong! Please try again later."
        chatbot_interaction.responding = False


def connect_to_h2ogpte(refresh_token):

    if refresh_token is None:
        client = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))
    else:

        token_provider = h2o_authn.TokenProvider(
            refresh_token=refresh_token,
            token_endpoint_url=f"{os.getenv('H2O_WAVE_OIDC_PROVIDER_URL')}/protocol/openid-connect/token",
            client_id=os.getenv("H2O_WAVE_OIDC_CLIENT_ID"),
            client_secret=os.getenv("H2O_WAVE_OIDC_CLIENT_SECRET"),
        )
        client = H2OGPTE(address=os.getenv("H2OGPTE_URL"), token_provider=token_provider)
    return client


class ChatBotInteraction:
    def __init__(self, user_message, system_prompt, chat_session_id) -> None:
        self.system_prompt = system_prompt
        self.chat_session_id = chat_session_id
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
