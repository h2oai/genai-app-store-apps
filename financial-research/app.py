import os
import asyncio

from h2o_wave import app, Q, ui, on, data, main, copy_expando, run_on
from h2ogpte import H2OGPTE
from h2ogpte.types import PartialChatMessage, ChatMessage


@app('/')
async def serve(q: Q):
    """
    Route end users through the application code.

    :param q: The query object for H2O Wave that has important app information.
    """

    if not q.client.initialized:  # Initialize the app if it's a new session
        await init(q)

    copy_expando(q.args, q.client)  # Save user UI interactions

    await run_on(q)      # Route user to the appropriate functionality
    await q.page.save()  # Save changes and update the UI


async def init(q: Q):
    """
    Initialize the app for a new browser session.

    :param q: The query object for H2O Wave that has important app information.
    """

    # Create landing page UI elements
    q.page['meta'] = ui.meta_card(
        box='',
        title='Digital Assets Investment Research',
        theme='solarized',
        stylesheet=ui.inline_stylesheet("""
            [data-test="footer"] a {
                color: #0000EE !important;
            }
            
            [data-test="source_code"] {
                background-color: #FFFFFF !important;
            }
            [data-test="app_store"] {
                background-color: #FFFFFF !important;
            }
            [data-test="support"] {
                background-color: #FFFFFF !important;
            }
        """),
        script=heap_analytics(
            event_properties=f"{{"
                             f"version: '0.0.8', "
                             f"product: 'Digital Assets Investment Research'"
                             f"}}",
        ),
        layouts=[
            ui.layout(
                breakpoint='m',
                min_height='100vh',
                max_width='1200px',
                zones=[
                    ui.zone('header'),
                    ui.zone('content', size='1', zones=[
                        ui.zone('vertical', size='0'),
                        ui.zone('horizontal', direction=ui.ZoneDirection.ROW, size="1"),
                    ]),
                    ui.zone(name='footer'),
                ]
            )
        ]
    )
    q.page['header'] = ui.header_card(
        box='header',
        title='Investment Research',
        subtitle="AI-enhanced research through SEC 10k forms",
        icon='StackedLineChart',
        items=[
            ui.persona(title='John Doe', subtitle='Researcher', caption='Online', size='m',
                       image='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'),
            ui.button(
                name="source_code",
                icon="Code",
                path="https://github.com/h2oai/genai-app-store-apps/tree/main/financial-research",
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
        ]
    )
    q.page["footer"] = ui.footer_card(
        box="footer",
        caption="Made with [Wave](https://wave.h2o.ai), [h2oGPTe](https://h2o.ai/platform/enterprise-h2ogpte), and "
        "💛 by the Makers at H2O.ai.<br />Find more in the [H2O GenAI App Store](https://genai.h2o.ai/).",
    )

    if os.getenv("MAINTENANCE_MODE", "false") == "true":
        q.page["meta"].dialog = ui.dialog(
            title="",
            blocking=True,
            closable=True,
            items=[
                ui.text_xl("<center>This app is under maintenance!</center>"),
                ui.text("<center>Please come back soon for digital assets investment research support.</center>")

            ],
        )
        return

    q.page['image'] = ui.tall_info_card(
        box=ui.box('vertical'),
        title='',
        name='image_card',
        caption='',
        image_height='300px',
        image='https://franklintempletonprod.widen.net/content/fghctkvqjy/webp/uk-gilts-masthead-640x360.jpg'
    )

    # Create a list of available SEC 10-Ks to chat with
    q.client.collection_name = "ABBOTT_LABORATORIES_145_2021"
    companies = {
        "ABBOTT_LABORATORIES_145_2021": "Abbot Laboratories",
        "Diamondback_Energy_Inc._129_2021": "Diamondback Energy",
        "EXXON_MOBIL_CORP_171_2021": "Exxon Mobile",
        "Johnson_Controls_International_plc_246_2021": "Johnson Controls",
        "Kraft_Heinz_Co_136_2021": "Kraft Heinz",
        "PFIZER_INC_220_2021": "Pfizer",
        "UNITEDHEALTH_GROUP_INC_210_2021": "United Health",
        "VERIZON_COMMUNICATIONS_INC_212_2021": "Verizon Communications",
        "WELLS_FARGO___COMPANY_MN_206_2021": "Wells Fargo",
        "WESTERN_DIGITAL_CORP_72_2021": "Western Digital"
    }
    h2ogpte = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))
    all_h2ogpte_collections = [c.name for c in h2ogpte.list_recent_collections(0, 1000)]
    app_collections = [ui.choice(c, companies[c]) for c in companies.keys() if c in all_h2ogpte_collections]
    q.page['selectors'] = ui.form_card(
        box=ui.box('horizontal', size='0'),
        items=[
            ui.choice_group(name='collection_name', label='Select a firm to research', value=q.client.collection_name,
                            choices=app_collections, trigger=True),
        ]
    )

    q.client.initialized = True  # Save that we have setup the app for this browser session

    await collection_name(q)


@on()
async def collection_name(q: Q):
    """
    Setup chat on a specific SEC 10-K form.

    :param q: The query object for H2O Wave that has important app information.
    """

    # Create a chat session for the selected collection
    h2ogpte = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))
    collections = h2ogpte.list_recent_collections(0, 1000)
    collection_id = [i.id for i in collections if i.name == q.client.collection_name][0]
    q.client.chat_session_id = h2ogpte.create_chat_session(collection_id)

    # Show a new chat session to the user
    q.page['chatbot_card'] = ui.chatbot_card(
        name='chatbot',
        box='horizontal',
        data=data('content from_user', t='list', rows=[
            [f"Welcome! What do you want to know about the collection called **{q.client.collection_name}**?", False]
        ])
    )


@on()
async def chatbot(q: Q):
    """
    Handle a user interacting with the chat bot component.

    :param q: The query object for H2O Wave that has important app information.
    """

    q.client.chatbot_interaction = ChatBotInteraction(user_message=q.args.chatbot)

    q.page["chatbot_card"].data += [q.args.chatbot, True]
    q.page["chatbot_card"].data += [q.client.chatbot_interaction.content_to_show, False]

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))
    await q.run(chat, q.client.chatbot_interaction, q.client.chat_session_id)
    await update_ui


async def stream_updates_to_ui(q: Q):
    """
    Update the app's UI every 1/10th of a second with values from our chatbot interaction
    :param q: The query object stored by H2O Wave with information about the app and user behavior.
    """
    while q.client.chatbot_interaction.responding:
        q.page["chatbot_card"].data[-1] = [q.client.chatbot_interaction.content_to_show, False]
        await q.page.save()
        await q.sleep(0.1)

    q.page["chatbot_card"].data[-1] = [q.client.chatbot_interaction.content_to_show, False]
    await q.page.save()


def chat(chatbot_interaction, chat_session_id):
    """
    Send the user's message to the LLM and save the response
    :param chatbot_interaction: Details about the interaction between the user and the LLM
    :param chat_session_id: Chat session for these messages
    """

    def stream_response(message):
        """
        This function is called by the blocking H2OGPTE function periodically
        :param message: response from the LLM, this is either a partial or completed response
        """
        chatbot_interaction.update_response(message)

    try:
        client = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))

        with client.connect(chat_session_id) as session:
            session.query(
                message=chatbot_interaction.user_message,
                timeout=60,
                callback=stream_response,
            )

    except Exception as e:
        return f"Unable to get an response: {e}"


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
            self.llm_response += message.content
            self.content_to_show = self.llm_response + " 🔵"


def heap_analytics(event_properties=None) -> ui.inline_script:
    """
    Create the needed javascript for recording user behavior to Heap Analytics.

    :param event_properties: Information about the interaction that we want to know in our analytics.
    """

    if "HEAP_ID" not in os.environ:
        return

    heap_id = os.getenv("HEAP_ID")
    script = f"""
window.heap=window.heap||[],heap.load=function(e,t){{window.heap.appid=e,window.heap.config=t=t||{{}};var r=document.createElement("script");r.type="text/javascript",r.async=!0,r.src="https://cdn.heapanalytics.com/js/heap-"+e+".js";var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(r,a);for(var n=function(e){{return function(){{heap.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}},p=["addEventProperties","addUserProperties","clearEventProperties","identify","resetIdentity","removeEventProperty","setEventProperties","track","unsetEventProperty"],o=0;o<p.length;o++)heap[p[o]]=n(p[o])}};
heap.load("{heap_id}"); 
    """

    if event_properties is not None:
        script += f"heap.addEventProperties({event_properties})"

    return ui.inline_script(content=script)


