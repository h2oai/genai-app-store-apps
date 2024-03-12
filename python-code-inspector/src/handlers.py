from h2o_wave import Q
from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage
from loguru import logger
from src.prompts import get_system_prompt, get_default_prompt, get_context
from src.layout import (
    landing_page_view,
    waiting_dialog
)
from src.prompts import get_default_prompt, expand_prompt
import os
import asyncio

async def add_prompt_to_chat(q: Q, prompt: str):
    q.page['chat'].data += [prompt, True]
    await q.page.save()

async def answer_question(q: Q, prompt: str):
    await waiting_dialog(q)
    logger.info("Prompting LLM with user query.")
    q.page['chat'].data += ['', False]
    system_prompt = get_system_prompt()
    if prompt is None:
        prompt = get_default_prompt(q)

    context = get_context(q=q)

    syst_prompt = f"{context, system_prompt}"
    q.client.chatbot_interaction = ChatBotInteraction(user_message=prompt)

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))
    await q.run(chat, q.client.chatbot_interaction, syst_prompt)
    await update_ui
    await q.page.save()

async def stream_updates_to_ui(q: Q):
    """
    Update the app's UI every 1/10th of a second with values from our chatbot interaction
    :param q: The query object stored by H2O Wave with information about the app and user behavior.
    """

    while q.client.chatbot_interaction.responding:
        q.page["chat"].data[-1] = [q.client.chatbot_interaction.content_to_show, False]
        await q.page.save()
        await q.sleep(0.1)

    q.page["chat"].data[-1] = [q.client.chatbot_interaction.content_to_show, False]
    await q.page.save()


def chat(chatbot_interaction, syst_prompt):
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
                system_prompt = syst_prompt,
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
        self.content_to_show = "🔵"

    def update_response(self, message):
        if isinstance(message, ChatMessage):
            self.content_to_show = message.content
            self.responding = False
        elif isinstance(message, PartialChatMessage):
            if message.content != "#### LLM Only (no RAG):\n":
                self.llm_response += message.content
                self.content_to_show = self.llm_response + " 🔵"

async def handler(q: Q):
    if q.args.chatbot:
        await add_prompt_to_chat(q, prompt=q.args.chatbot)
        await answer_question(q, prompt=q.args.chatbot)
    elif q.args.inspect_code:
        prompt = get_default_prompt(q)
        await add_prompt_to_chat(q, prompt=prompt)
        prompt = await expand_prompt(q, prompt=prompt)
        await answer_question(q, prompt=prompt)
    else:
        await landing_page_view(q)
