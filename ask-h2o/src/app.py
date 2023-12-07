import os
from datetime import datetime
import time
import hashlib

import toml
from h2ogpte import H2OGPTE
from h2o_wave import app, Q, ui, on, copy_expando, data, main, run_on
from loguru import logger


@app('/')
async def serve(q: Q):
    request_id = int(time.time() * 1000)
    logger.info(f"Starting user request: {request_id}")
    logger.debug(q.args)
    copy_expando(q.args, q.client)  # Save any UI responses of the User to their session

    if not q.client.initialized:
        await initialize_client(q)

    await run_on(q)
    await q.page.save()

    logger.info(f"Ending user request: {request_id}")


async def initialize_app(q: Q):
    logger.info("Initializing the app for the first time.")
    q.app.toml = toml.load("app.toml")
    q.app.load, = await q.site.upload(['./static/load.gif'])

    q.app.session_count = 0

    q.app.h2ogpte = {
        "address": os.getenv("H2OGPTE_URL"),
        "api_key": os.getenv("H2OGPTE_API_TOKEN"),
    }

    h2ogpte = H2OGPTE(address=q.app.h2ogpte["address"], api_key=q.app.h2ogpte["api_key"])

    q.app.collections = {}
    for c in h2ogpte.list_recent_collections(0, 1000):
        if c.document_count > 0:  # Empty collections do not help our end users
            q.app.collections[c.id] = c.name

    q.app.initialized = True


async def initialize_client(q: Q):

    if not q.app.initialized:
        await initialize_app(q)

    q.app.session_count += 1
    logger.info(f"Initializing the app for the {q.app.session_count} user")

    q.client.cards = []
    q.client.selected_collection = list(q.app.collections.keys())[0] if len(q.app.collections) > 0 else None
    q.client.chat_length = 0

    landing_page_layout(q)

    if len(q.app.collections) == 0:
        q.page["meta"].dialog = ui.dialog(
            title="App Unavailable",
            items=[
                ui.text("There is no data available for chatting, please try again later."),
                ui.text("You can report this issue by sending an email to cloud-feedback@h2o.ai.")
            ],
            closable=False,
            blocking=True
        )
        return

    await selected_collection(q)

    q.page["chatbot"] = ui.chatbot_card(
        box="chat",
        data=data('content from_user', t='list'),
        name='chatbot'
    )

    q.client.initialized = True


def landing_page_layout(q: Q):
    logger.info("")
    q.page['meta'] = ui.meta_card(
        box='',
        title=q.app.toml['App']['Title'],
        icon=os.getenv("LOGO",
                       "https://h2o.ai/content/experience-fragments/h2o/us/en/site/header/master/_jcr_content/root/container/header_copy/logo.coreimg.svg/1696007565253/h2o-logo.svg"),
        theme="custom",
        script=heap_analytics(
            userid=q.auth.subject,
            event_properties=f"{{"
                             f"version: '{q.app.toml['App']['Version']}', "
                             f"product: '{q.app.toml['App']['Title']}'"
                             f"}}",
        ),
        themes=[
            ui.theme(
                name='custom',
                primary=os.getenv("PRIMARY_COLOR", "#FEC925"),
                text='#000000',
                card='#ffffff',
                page=os.getenv("SECONDARY_COLOR", "#D3D3D1"),
            )
        ],
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
                breakpoint='s',
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
        image=os.getenv("LOGO",
                        "https://h2o.ai/content/experience-fragments/h2o/us/en/site/header/master/_jcr_content/root/container/header_copy/logo.coreimg.svg/1696007565253/h2o-logo.svg"),
    )

    q.page["footer"] = ui.footer_card(
        box="footer",
        caption="Made with 💛 and H2O Wave."
    )
    q.page["device-not-supported"] = ui.form_card(
        box="device-not-supported",
        items=[
            ui.text_xl(
                "This app was built desktop; it is not available on mobile or tablets."
            )
        ],
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
            choices=[ui.choice(c, q.app.collections[c]) for c in q.app.collections.keys()]
        )
    ]

    h2ogpte = H2OGPTE(address=q.app.h2ogpte["address"], api_key=q.app.h2ogpte["api_key"])

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
    q.client.cards.append("collection")

    q.page["collection-mobile"] = ui.form_card(
        box=ui.box("collections-mobile"),
        items=all_collections_dropdown
    )
    q.client.cards.append("collection-mobile")


@on()
async def chatbot(q):

    starting_chat_length = q.client.chat_length
    q.client.chat_length += 2

    q.page['chatbot'].data += [q.client.chatbot, True]
    q.page['chatbot'].data += ["<img src='{}' height='200px'/>".format(q.app.load), False]
    await q.page.save()

    bot_res = await q.run(llm_query_with_context, q.app.h2ogpte, q.client.selected_collection, q.client.chatbot)

    diff = q.client.chat_length - starting_chat_length - 1
    q.page['chatbot'].data[-diff] = [bot_res, False]

    # stream = chunk = ''
    # for w in bot_res:
    #     chunk += w
    #     await q.sleep(0.01)
    #     if len(chunk) == 5:
    #         stream += chunk
    #         q.page['chatbot'].data[-diff] = [stream, False]
    #         await q.page.save()
    #         chunk = ''
    # if chunk:
    #     q.page['chatbot'].data[-diff] = [stream + chunk, False]


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


def llm_query_with_context(connection_details, collection_id, user_message):
    logger.info("")
    try:
        logger.debug(user_message)

        h2ogpte = H2OGPTE(address=connection_details["address"], api_key=connection_details["api_key"])
        chat_session_id = h2ogpte.create_chat_session(collection_id=collection_id)

        with h2ogpte.connect(chat_session_id) as session:
            reply = session.query(
                message=user_message,
                timeout=16000,
            )

        response = reply.content
        logger.debug(response)
        return response.strip()

    except Exception as e:
        logger.error(e)
        return ""


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