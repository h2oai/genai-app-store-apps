import os
from datetime import datetime
import hashlib
import asyncio

import toml
from h2ogpte import H2OGPTE
from h2ogpte.types import PartialChatMessage, ChatMessage
from h2o_wave import app, Q, ui, on, copy_expando, data, main, run_on
from loguru import logger



@app('/')
async def serve(q: Q):
    copy_expando(q.args, q.client)  # Save any UI responses of the User to their session

    try:
        # Route the end user based on how they interacted with the app.
        logger.info(q.args)

        # Setup the application for a new browser tab, if not done yet
        if not q.client.initialized:
            await initialize_client(q)

        await run_on(q)
        await q.page.save()

    except Exception as ex:
        logger.error(ex)
        q.page["meta"].dialog = ui.dialog(
            title="", blocking=True, closable=False,
            items=[
                ui.text_xl("<center>Something went wrong!</center>"),
                ui.text(f"<center>Please come back soon to chat with the H2O Product Docs.</center>")
            ],
        )
    await q.page.save()  # Update the UI


async def initialize_client(q: Q):

    if not q.app.initialized:
        q.app.toml = toml.load("app.toml")
        q.app.initialized = True

    h2ogpte = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))
    q.client.collections = {}
    for c in h2ogpte.list_recent_collections(0, 1000):
        if c.document_count > 0:  # Empty collections do not help our end users
            q.client.collections[c.id] = c.name

    q.client.selected_collection = list(q.client.collections.keys())[0] if len(q.client.collections) > 0 else None

    landing_page_layout(q)
    await selected_collection(q)

    q.client.initialized = True


def landing_page_layout(q: Q):
    logger.info("")
    style = """
        [data-test="header"] {
            background-color: #000000 !important;
        }

        [data-test="source_code"] {
            color: #000000 !important;
            background-color: #FFE600 !important
        }

        img {
            cursor: default;
        }

        [data-test="footer"] a {
            color: #ff9632 !important;
        }
        
        .ms-Persona-secondaryText {
            white-space: unset;
        }
    """

    q.page['meta'] = ui.meta_card(
        box='',
        title=f"{q.app.toml['App']['Title']} | H2O.ai",
        icon="https://h2o.ai/content/experience-fragments/h2o/us/en/site/header/master/_jcr_content/root/container/header_copy/logo.coreimg.svg/1696007565253/h2o-logo.svg",
        themes=[ui.theme(name="custom", primary="#FFE600", text="#000000", card="#FFFFFF", page="#E2E2E2")],
        theme="custom",
        stylesheet=ui.inline_stylesheet(style),
        script=heap_analytics(
            userid=q.auth.subject,
            event_properties=f"{{"
                             f"version: '{q.app.toml['App']['Version']}', "
                             f"product: '{q.app.toml['App']['Title']}'"
                             f"}}",
        ),
        layouts=[
            ui.layout(
                breakpoint="xs",
                height="100vh",
                zones=[
                    ui.zone(name='header'),
                    ui.zone(name='body', size="1", direction="column", zones=[
                        ui.zone(name="collections-mobile"),
                        ui.zone(name="chat")
                    ]),
                    ui.zone(name="footer")
                ],
            ),
            ui.layout(
                breakpoint='m',
                min_height='100vh',
                zones=[
                    ui.zone(name='header'),
                    ui.zone(name='body', size="1", direction="row", zones=[
                        ui.zone(name="collections", size="50%"),
                        ui.zone(name="chat", size="50%")
                    ]),
                    ui.zone(name="footer")
                ]
            )
        ]
    )
    q.page['header'] = ui.header_card(
        box='header',
        title=f"{q.app.toml['App']['Title']}",
        subtitle=q.app.toml["App"]["Description"],
        image="https://h2o.ai/content/experience-fragments/h2o/us/en/site/header/master/_jcr_content/root/container/header_copy/logo.coreimg.svg/1696007565253/h2o-logo.svg",
        items=[
            ui.button(name="source_code", icon="Code", tooltip="View source code", path="https://github.com/h2oai/genai-app-store-apps/tree/main/ask-h2o"),
        ]
    )

    q.page["chatbot"] = ui.chatbot_card(
        box="chat",
        data=data('content from_user', t='list'),
        name='chatbot'
    )

    q.page["footer"] = ui.footer_card(
        box="footer",
        caption="Made with [Wave](https://wave.h2o.ai), [h2oGPTe](https://h2o.ai/platform/enterprise-h2ogpte), and 💛 by the Makers at H2O.ai."
    )


@on()
async def selected_collection(q):
    logger.info("")

    all_collections_dropdown = [
        ui.dropdown(
            name="selected_collection",
            label="Explore the available collections and documents",
            value=q.client.selected_collection,
            trigger=True,
            choices=[ui.choice(c, q.client.collections[c]) for c in q.client.collections.keys()]
        )
    ]

    h2ogpte = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))

    collection = h2ogpte.get_collection(q.client.selected_collection)
    collection_documents = h2ogpte.list_documents_in_collection(q.client.selected_collection, 0, 4000)

    all_documents_table = [
        ui.inline(justify='between', items=[
            ui.persona(title=collection.name, subtitle=collection.description, size='xs', initials_color="#000000"),
            ui.text_s(get_time_since(collection.updated_at)),
        ]),
        ui.table(
            name='table_{}'.format(collection.id), width='1',
            columns=[
                ui.table_column(name='Name', label='Name', link=False, min_width="400px"),
                ui.table_column(name='Type', label='Type'),
                ui.table_column(name='Date', label='Date')
            ],
            rows=[ui.table_row(name=d.id, cells=[d.name, d.type, d.updated_at.strftime("%Y-%m-%d %H:%M:%S")]) for
                  d in collection_documents]
        ),
    ]

    q.page["collection"] = ui.form_card(
        box=ui.box("collections"),
        items=all_collections_dropdown + [ui.separator("")] + all_documents_table
    )

    q.page["collection-mobile"] = ui.form_card(
        box=ui.box("collections-mobile"),
        items=all_collections_dropdown
    )


@on()
async def chatbot(q):

    q.client.chatbot_interaction = ChatBotInteraction(user_message=q.args.chatbot)

    q.page['chatbot'].data += [q.args.chatbot, True]
    q.page["chatbot"].data += [q.client.chatbot_interaction.content_to_show, False]

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))
    await q.run(llm_query_with_context, q.client.selected_collection, q.client.chatbot_interaction)
    await update_ui


async def stream_updates_to_ui(q: Q):
    """
    Update the app's UI every 1/10th of a second with values from our chatbot interaction
    :param q: The query object stored by H2O Wave with information about the app and user behavior.
    """
    while q.client.chatbot_interaction.responding:
        q.page["chatbot"].data[-1] = [
            q.client.chatbot_interaction.content_to_show,
            False,
        ]
        await q.page.save()
        await q.sleep(0.1)

    q.page["chatbot"].data[-1] = [
        q.client.chatbot_interaction.content_to_show,
        False,
    ]
    await q.page.save()


def get_time_since(last_updated_timestamp):
    logger.info("")
    duration = datetime.now(last_updated_timestamp.tzinfo) - last_updated_timestamp
    duration_in_s = duration.total_seconds()

    years = 60 * 60 * 24 * 365
    months = 60 * 60 * 24 * 30
    days = 60 * 60 * 24
    hours = 60 * 60
    minutes = 60

    if duration_in_s >= years:
        return '{} Years Ago'.format(int(divmod(duration_in_s, years)[0]))
    elif duration_in_s >= months:
        return '{} Months Ago'.format(int(divmod(duration_in_s, months)[0]))
    elif duration_in_s >= days:
        return '{} Days Ago'.format(int(divmod(duration_in_s, days)[0]))
    elif duration_in_s >= hours:
        return '{} Hours Ago'.format(int(divmod(duration_in_s, hours)[0]))
    elif duration_in_s >= minutes:
        return '{} Minutes Ago'.format(int(divmod(duration_in_s, minutes)[0]))
    else:
        return '{} Seconds Ago'.format(int(duration_in_s))


def llm_query_with_context(collection_id, chatbot_interaction):
    logger.info("")

    def stream_response(message):
        """
        This function is called by the blocking H2OGPTE function periodically
        :param message: response from the LLM, this is either a partial or completed response
        """
        chatbot_interaction.update_response(message)

    try:
        logger.debug(chatbot_interaction.user_message)

        h2ogpte = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))
        chat_session_id = h2ogpte.create_chat_session(collection_id=collection_id)

        with h2ogpte.connect(chat_session_id) as session:
            session.query(message=chatbot_interaction.user_message, timeout=60,callback=stream_response)

    except Exception as e:
        logger.error(e)


def heap_analytics(userid, event_properties=None) -> ui.inline_script:

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

    if event_properties is not None:
        script += f"heap.addEventProperties({event_properties})"

    return ui.inline_script(content=script)


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
            if message.content != "#### No RAG (LLM only):\n":
                self.llm_response += message.content
                self.content_to_show = self.llm_response + " 🟡"