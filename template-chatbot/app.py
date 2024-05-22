import os
import asyncio
import hashlib

from h2o_wave import main, app, Q, ui, data, run_on, on
from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage
import h2o_authn

from loguru import logger


@app("/")
async def serve(q: Q):
    """Route the end user based on how they interacted with the app."""

    if not q.client.initialized:
        initialize_client(q)

    elif q.events.chatbot:
        label, caption, icon = q.app.suggestions[q.events.chatbot.suggestion]
        q.args.chatbot = label + ' ' + caption

    await run_on(q)  # Route user to the appropriate "on" function
    await q.page.save()  # Update the UI


def initialize_client(q):
    """Code that is needed for each new browser that visits the app"""

    if not q.app.suggestions:
        q.app.suggestions = {
            'sug1': ["Write a poem", "about H2O Wave", "Edit"],
            'sug2': ["Plan a trip", "to Europe", "Airplane"],
            'sug3': ["Give me ideas", "for a new project", "Lightbulb"],
            'sug4': ["Explain to me", "CSS preprocessors", "Code"]
        }

    q.page["meta"] = ui.meta_card(
        box="",
        title="Chatbot | H2O.ai",
        layouts=[ui.layout(breakpoint="xs", width="900px", zones=[
            ui.zone(name="header"),
            ui.zone(name="main", size="1"),
            ui.zone(name="footer")
        ])],
        script=heap_analytics(userid=q.auth.subject),
        stylesheet=ui.inline_stylesheet("""
            [data-test="footer_card"] a {color: #0000EE !important;}
                
            [data-test="source_code"], [data-test="app_store"],[data-test="support"] {
                color: #000000 !important; background-color: #FFE600 !important
            } 
        """),
    )

    try:
        client = connect_to_h2ogpte(q.auth.refresh_token)
        chat_session_id = client.create_chat_session()

    except Exception as ex:
        handle_exception(ex, q)
        return

    q.client.chatbot = ChatBot(
        system_prompt="Hi! I am a Large Language Model, I am super friendly and here to try and answer any question "
                      "you might have with a casual and fun tone.",
        chat_session_id=chat_session_id
    )

    q.page["header_card"] = ui.header_card(
        box="header",
        title="Starter Chatbot",
        subtitle="Basic chatbot with h2oGPTe",
        image="https://h2o.ai/company/brand-kit/_jcr_content/root/container/section/par/advancedcolumncontro/columns1/advancedcolumncontro/columns0/image.coreimg.svg/1697220254347/h2o-logo.svg",
        items=[
            ui.button(
                name="source_code",
                icon="Code",
                path="https://github.com/h2oai/genai-app-store-apps/tree/main/template-chatbot",
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
    q.page["chatbot_card"] = ui.chatbot_card(
        box="main",
        name="chatbot",
        data=data(
            fields="content from_user",
            t="list",
            rows=[[q.client.chatbot.system_prompt, False]],
        ),
        placeholder="Ask me anything...",
        events=['suggestion'],
        suggestions=[ui.chat_suggestion(name, label=value[0], caption=value[1], icon=value[2])
                     for name, value in q.app.suggestions.items()]
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

    q.client.chatbot.handle_user_request(q.args.chatbot)

    q.page["chatbot_card"].data += [q.client.chatbot.user_message, True]
    q.page["chatbot_card"].data += [q.client.chatbot.content_to_show, False]

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))
    await q.run(chat, q)
    await update_ui


async def stream_updates_to_ui(q: Q):
    """Update the app's UI every 1/10th of a second with values from our chatbot interaction"""
    q.page["chatbot_card"].disabled = True
    q.page['chatbot_card'].suggestions = []

    while q.client.chatbot.responding:
        q.page["chatbot_card"].data[-1] = [q.client.chatbot.content_to_show, False]
        await q.page.save()
        await q.sleep(0.1)

    q.page["chatbot_card"].data[-1] = [q.client.chatbot.content_to_show, False]
    q.page["chatbot_card"].disabled = False
    await q.page.save()


def chat(q: Q):
    """Interact with h2oGPTe and stream the response"""

    def stream_response(message):
        """This function is called by the blocking H2OGPTE function periodically"""
        q.client.chatbot.update_response(message)

    try:
        client = connect_to_h2ogpte(q.auth.refresh_token)

        with client.connect(q.client.chatbot.chat_session_id) as session:
            session.query(
                system_prompt=q.client.chatbot.system_prompt,
                message=q.client.chatbot.user_message,
                timeout=60,
                callback=stream_response,
                rag_config={"rag_type": "llm_only"},
            )

    except Exception as ex:
        q.client.chatbot.responding = False
        handle_exception(ex, q)


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


def handle_exception(ex, q):
    logger.error(ex)
    logger.error(type(ex))
    q.page["meta"].dialog = ui.dialog(
        title="Something went wrong! Please try again later.",
        items=[
            ui.text("You can report this error by sending an email to support@h2o.ai!")
        ],
        closable=False,
        blocking=True
    )


def heap_analytics(userid) -> ui.inline_script:
    if "HEAP_ID" not in os.environ:
        return
    heap_id = os.getenv("HEAP_ID")
    script = f"""
window.heap=window.heap||[],heap.load=function(e,t){{window.heap.appid=e,window.heap.config=t=t||{{}};var r=document.createElement("script");r.type="text/javascript",r.async=!0,r.src="https://cdn.heapanalytics.com/js/heap-"+e+".js";var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(r,a);for(var n=function(e){{return function(){{heap.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}},p=["addEventProperties","addUserProperties","clearEventProperties","identify","resetIdentity","removeEventProperty","setEventProperties","track","unsetEventProperty"],o=0;o<p.length;o++)heap[p[o]]=n(p[o])}};
heap.load("{heap_id}"); 
    """

    if userid is not None:  # is OIDC Enabled? we do not want to identify all non-logged in users as "none"
        identity = hashlib.sha256(userid.encode()).hexdigest()
        script += f"heap.identify('{identity}');"

    return ui.inline_script(content=script)


class ChatBot:
    def __init__(self, system_prompt, chat_session_id) -> None:
        self.system_prompt = system_prompt
        self.chat_session_id = chat_session_id
        self.starting_content_to_show = "🟡"

        self.responding = False
        self.user_message = ""
        self.llm_response = ""
        self.content_to_show = ""

    def handle_user_request(self, user_message):
        self.responding = True
        self.user_message = user_message

        self.content_to_show = self.starting_content_to_show
        self.llm_response = ""

    def update_response(self, message):
        if isinstance(message, ChatMessage):
            self.content_to_show = message.content
            self.responding = False
            logger.success("Completed streaming user's LLM response")
        elif isinstance(message, PartialChatMessage):
            if message.content != "#### LLM Only (no RAG):\n":
                self.llm_response += message.content
                self.content_to_show = self.llm_response + " 🟡"


