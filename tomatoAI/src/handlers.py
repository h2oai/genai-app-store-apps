from h2o_wave import Q
from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage
from loguru import logger
import os
import asyncio
from src.layout import (
    landing_page_view,
    image_view,
    waiting_dialog
)
from src.prompts import questions

async def answer_question(q: Q, prompt: str):
    q.page['chat'].data += [prompt, True]
    q.page['chat'].data += ['', False]
    await q.page.save()
    await waiting_dialog(q)

    plants = []
    if q.client.plants is not None:
        plants.extend(q.client.plants)

    if len(plants) > 0:
        selection = plants[0]
        for n in range(1, len(plants)):
            selection += ", "
            selection += plants[n]
    else:
        selection = ["tomatoes"]

    logger.info("Prompting LLM with user query.")
    if q.client.climate_subzone is None:
        context = [
            f"The user is passionate about cultivating {plants} and currently tends to "
            f"{q.client.num_beds} beds, each with a size of 2 square meters. They are seeking advice on growing vegetables "
            f"that are well-suited to their specific climate conditions and small bed size. "
            f"If the user provides their location, provide information about the climate subzone according"
            f" to the Köppen and Geiger classification."
            f"They are open to exploring alternatives if the plants do not fit "
            f"are not optimal for preventing pests and diseases."
            f"They prefer concise answers with a subtle touch of humor. "
        ]
    else:
        context = [
            f"The user is passionate about cultivating {plants} and currently tends to "
            f"{q.client.num_beds} beds, each with a size of 2 square meters. Located in the {q.client.climate_subzone} "
            f"climate subzone, they are seeking advice on growing vegetables that are well-suited "
            f"to their specific climate conditions and small bed size. "
            f"Additionally, they are curious to know if the chosen plants thrive "
            f"in this particular climate subzone according to the Köppen and Geiger classification. " 
            f"They are open to exploring alternatives if the plants do not fit "
            f"the climate subzone or are not optimal for preventing pests and diseases. "
            f"They prefer concise answers with a subtle touch of humor. "
        ]

    system_p = "Specializing in cultivating vegetables and fruits within kitchen spaces or small vegetable gardens, you provide guidance and easy-to-understand explanations in a humorous manner, assisting inexperienced gardeners in their endeavors. When discussing climate zones and subzones, you consistently refer to those defined by Köppen and Geiger. You prefer to create lists using bullet points rather than text blocks."
    syst_prompt = f"{context, system_p}"
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
        print(syst_prompt)
        print(chatbot_interaction.user_message)
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
        await answer_question(q, q.args.chatbot)
        await image_view(q)
    elif q.args["prompts"] is not None and q.args["prompts"] in list(questions.keys()):
        await answer_question(q, questions[q.args["prompts"]]["prompt"])
        await image_view(q)
    else:
        await landing_page_view(q)
