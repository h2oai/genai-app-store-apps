import asyncio
import os

from h2o_wave import Q, app, data, main, on, run_on, ui
from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage

from loguru import logger


@app("/")
async def serve(q: Q):
    """Route the end user based on how they interacted with the app."""

    if not q.client.initialized:  # Setup the application for a new browser tab, if not done yet

        q.app.example_system_prompts = [
            "You only know about house plants.",
            "You only talk about house plants.",
            "You are an overworked plant store owner from the midwest who is feeling dispassionate about your "
            "profession. You are currently at work and if you are asked about something that doesn't make sense to "
            "ask a plant store owner, you will redirect the conversation.",
            "Welcome! You can Ask Me Anything about owning a plant store!",
            "Plants are really cool and I like them",
            "~Write your own~",
        ]

        q.client.system_prompt_default = ""
        q.client.system_prompt_customized = q.app.example_system_prompts[0]

        setup_app_ui(q)

        q.client.initialized = True
        add_custom_system_prompt(q)
        await chatbot(q, "Who are you?")

    await run_on(q)  # Route user to the appropriate "on" function
    await q.page.save()  # Update the UI


def setup_app_ui(q):
    q.page["meta"] = ui.meta_card(
        box="",
        title="Learning LLMs: System Prompts",
        stylesheet=ui.inline_stylesheet("""
        [data-test="footer"] a {color: #0000EE !important;}
        [data-test="source_code"], [data-test="app_store"],[data-test="support"]  {color: #000000 !important; background-color: #FFE600 !important}
        """),
        script=heap_analytics(userid=q.auth.subject),
        layouts=[
            ui.layout(
                breakpoint="xs",
                zones=[
                    ui.zone("header"),
                    ui.zone("mobile_warning"),
                    ui.zone(
                        "details",
                        direction="row",
                        zones=[
                            ui.zone("details_customized"),
                        ],
                    ),
                    ui.zone(
                        "chats",
                        size="1",
                        direction="row",
                        zones=[
                            ui.zone("chats_customized"),
                        ],
                    ),
                    ui.zone("footer"),
                ],
            ),
            ui.layout(
                breakpoint="m",
                width="1200px",
                zones=[
                    ui.zone("header"),
                    ui.zone(
                        "details",
                        direction="row",
                        zones=[
                            ui.zone("details_default", size="50%"),
                            ui.zone("details_customized", size="50%"),
                        ],
                    ),
                    ui.zone(
                        "chats",
                        size="1",
                        direction="row",
                        zones=[
                            ui.zone("chats_default"),
                            ui.zone("chats_customized"),
                        ],
                    ),
                    ui.zone("footer"),
                ],
            ),
        ],
    )

    q.page["header"] = ui.header_card(
        box="header",
        title="Learning LLMs: System Prompts",
        subtitle="Explore the power of personalized language models by comparing how changing the System Prompt changes the response.",
        image="https://h2o.ai/company/brand-kit/_jcr_content/root/container/section/par/advancedcolumncontro/columns1/advancedcolumncontro/columns0/image.coreimg.svg/1697220254347/h2o-logo.svg",
        items=[
            ui.button(
                name="source_code",
                icon="Code",
                path="https://github.com/h2oai/genai-app-store-apps/tree/main/system-prompt",
                tooltip="View the source code",
            ),
            ui.button(
                name="app_store",
                icon="Shop",
                path="https://genai.h2o.ai",
                tooltip="Visit the App Store",
            ),
            ui.button(
                name="support",
                icon="Help",
                path="https://support.h2o.ai/support/tickets/new",
                tooltip="Get help",
            ),

        ],
    )

    q.page["mobile_warning"] = ui.section_card(
        box="mobile_warning",
        title="",
        subtitle="",
        items=[
            ui.message_bar(
                type="info",
                text="For the best experience, use a larger device to compare default "
                     "and customized responses.",
            )
        ],
    )

    q.page["header_default"] = ui.form_card(
        box="details_default",
        items=[
            ui.textbox(
                name="system_prompt_default",
                label="Default System Prompt",
                multiline=True,
                disabled=True,
                value=q.client.system_prompt_default,
            )
        ],
    )

    q.page["header_customized"] = ui.form_card(
        box="details_customized",
        items=[
            ui.dropdown(
                name="existing_prompts",
                label="Choose an example System Prompt",
                choices=[
                    ui.choice(str(i), q.app.example_system_prompts[i])
                    for i in range(len(q.app.example_system_prompts))
                ],
                value="0",  # TODO how to look up the index of my option
                trigger=True,
            ),
        ],
    )

    q.page["chatbot_default"] = ui.chatbot_card(
        box="chats_default",
        name="chatbot_default",
        data=data(
            fields="content from_user",
            t="list",
            rows=[],
        ),
    )

    q.page["chatbot_customized"] = ui.chatbot_card(
        box="chats_customized",
        name="chatbot_customized",
        data=data(
            fields="content from_user",
            t="list",
            rows=[],
        ),
    )

    q.page["footer"] = ui.footer_card(
        box="footer",
        caption="Made with [Wave](https://wave.h2o.ai), [h2oGPTe](https://h2o.ai/platform/enterprise-h2ogpte), and "
                "💛 by the Makers at H2O.ai.<br />Find more in the [H2O GenAI App Store](https://genai.h2o.ai/).",
    )


def add_custom_system_prompt(q):
    q.page["chatbot_customized"].data += [f"<b>System Prompt:</b> {q.client.system_prompt_customized}", False]


@on()
async def existing_prompts(q):
    selected_prompt_index = int(q.args.existing_prompts)

    if q.app.example_system_prompts[selected_prompt_index] == "~Write your own~":
        q.page["header_customized"].items = [
            ui.dropdown(
                name="existing_prompts",
                label="Choose an example System Prompt",
                choices=[
                    ui.choice(str(i), q.app.example_system_prompts[i])
                    for i in range(len(q.app.example_system_prompts))
                ],
                value=q.args.existing_prompts,
                trigger=True,
            ),
            ui.textbox(
                name="system_prompt_customized",
                label="Custom System Prompt",
                multiline=True,
                disabled=False,
                value=q.client.system_prompt_customized,
                height="150px",
            ),
            ui.buttons(
                items=[ui.button(name="update_system_prompt", label="Save")],
                justify="end",
            ),
        ]
    else:
        q.page["header_customized"].items = [
            ui.dropdown(
                name="existing_prompts",
                label="Choose an example System Prompt",
                choices=[
                    ui.choice(str(i), q.app.example_system_prompts[i])
                    for i in range(len(q.app.example_system_prompts))
                ],
                value=q.args.existing_prompts,
                trigger=True,
            )
        ]

        q.client.system_prompt_customized = q.app.example_system_prompts[
            selected_prompt_index
        ]

        q.page["chatbot_customized"].data += ["User has changed the prompt.", True]
        add_custom_system_prompt(q)
        await chatbot(q, "Who are you?")


@on()
async def update_system_prompt(q):
    q.client.system_prompt_customized = q.args.system_prompt_customized
    q.page["chatbot_customized"].data += ["User has changed the prompt.", True]
    add_custom_system_prompt(q)
    await chatbot(q, "Who are you?")


@on()
async def chatbot_default(q):
    await chatbot(q, q.args.chatbot_default)


@on()
async def chatbot_customized(q):
    await chatbot(q, q.args.chatbot_customized)


@on()
async def chatbot(q: Q, user_message):
    """Send a user's message to a Large Language Model and stream the response."""

    q.client.default_interaction = ChatBotInteraction(
        system_prompt=q.client.system_prompt_default, user_message=user_message
    )

    q.client.custom_interaction = ChatBotInteraction(
        system_prompt=q.client.system_prompt_customized, user_message=user_message
    )

    q.page["chatbot_default"].data += [q.client.default_interaction.user_message, True]
    q.page["chatbot_default"].data += [
        q.client.custom_interaction.content_to_show,
        False,
    ]

    q.page["chatbot_customized"].data += [
        q.client.default_interaction.user_message,
        True,
    ]
    q.page["chatbot_customized"].data += [
        q.client.custom_interaction.content_to_show,
        False,
    ]

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))
    await asyncio.gather(
        placeholder(q, q.client.default_interaction),
        placeholder(q, q.client.custom_interaction),
    )
    await update_ui


async def placeholder(q, variable):
    await q.run(chat, variable)


async def stream_updates_to_ui(q: Q):
    """
    Update the app's UI every 1/10th of a second with values from our chatbot interaction
    :param q: The query object stored by H2O Wave with information about the app and user behavior.
    """
    while (
        q.client.default_interaction.responding
        or q.client.custom_interaction.responding
    ):
        q.page["chatbot_default"].data[-1] = [
            q.client.default_interaction.content_to_show,
            False,
        ]
        q.page["chatbot_customized"].data[-1] = [
            q.client.custom_interaction.content_to_show,
            False,
        ]
        await q.page.save()
        await q.sleep(0.1)

    q.page["chatbot_default"].data[-1] = [
        q.client.default_interaction.content_to_show,
        False,
    ]
    q.page["chatbot_customized"].data[-1] = [
        q.client.custom_interaction.content_to_show,
        False,
    ]
    await q.page.save()


def chat(chatbot_interaction):
    """
    Send the user's message to the LLM and save the response
    :param chatbot_interaction: Details about the interaction between the user and the LLM
    """

    def stream_response(message):
        """
        This function is called by the blocking H2OGPTE function periodically
        :param message: response from the LLM, this is either a partial or completed response
        """
        chatbot_interaction.update_response(message)

    client = H2OGPTE(
        address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN")
    )
    collection_id = client.create_collection("temp", "")
    chat_session_id = client.create_chat_session(collection_id)
    with client.connect(chat_session_id) as session:
        session.query(
            system_prompt=chatbot_interaction.system_prompt,
            message=chatbot_interaction.user_message,
            timeout=60,
            callback=stream_response,
            rag_config={"rag_type": "llm_only"},
        )
    client.delete_collections([collection_id])
    client.delete_chat_sessions([chat_session_id])


class ChatBotInteraction:
    def __init__(self, system_prompt, user_message) -> None:
        self.system_prompt = system_prompt
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


def heap_analytics(userid) -> ui.inline_script:
    if "HEAP_ID" not in os.environ:
        logger.warning("UI Analytics is not enabled.")
        return

    import hashlib
    script = f"""
window.heap=window.heap||[],heap.load=function(e,t){{window.heap.appid=e,window.heap.config=t=t||{{}};var r=document.createElement("script");r.type="text/javascript",r.async=!0,r.src="https://cdn.heapanalytics.com/js/heap-"+e+".js";var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(r,a);for(var n=function(e){{return function(){{heap.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}},p=["addEventProperties","addUserProperties","clearEventProperties","identify","resetIdentity","removeEventProperty","setEventProperties","track","unsetEventProperty"],o=0;o<p.length;o++)heap[p[o]]=n(p[o])}};
heap.load("{os.getenv("HEAP_ID")}"); 
    """

    if userid is not None:  # is OIDC Enabled? we do not want to identify all non-logged in users as "none"
        identity = hashlib.sha256(userid.encode()).hexdigest()
        script += f"heap.identify('{identity}');"

    return ui.inline_script(content=script)