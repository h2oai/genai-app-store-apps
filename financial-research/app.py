import os

from h2o_wave import app, Q, ui, on, data, main, copy_expando, run_on
from h2ogpte import H2OGPTE


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
    if not q.app.initialized:
        await initialize_app(q)

    # Set default properties for a new session
    q.client.collection_name = "ABBOTT_LABORATORIES_145_2021"
    q.client.chat_length = 0

    # Create landing page UI elements
    q.page['meta'] = ui.meta_card(
        box='',
        title='Digital Assets Investment Research',
        theme='solarized',
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
        title='Digital Assets Investment Research',
        subtitle="AI-enhanced research through SEC 10k forms",
        icon='StackedLineChart',
        items=[ui.persona(title='John Doe', subtitle='Researcher', caption='Online', size='m',
                          image='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260')]
    )
    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Made with 💛 using [H2O Wave](https://wave.h2o.ai).'
    )

    q.page['image'] = ui.tall_info_card(
        box=ui.box('vertical'),
        title='',
        name='image_card',
        caption='',
        image_height='300px',
        image='https://franklintempletonprod.widen.net/content/fghctkvqjy/webp/uk-gilts-masthead-640x360.jpg'
    )

    q.page['selectors'] = ui.form_card(
        box=ui.box('horizontal', size='0'),
        items=[
            ui.choice_group(name='collection_name', label='Select a firm to research', value=q.client.collection_name,
                            choices=q.app.collections, trigger=True),
        ]
    )
    q.client.initialized = True  # Save that we have setup the app for this browser session

    await collection_name(q)


async def initialize_app(q: Q):
    """
    Initialize the app for all users.

    :param q: The query object for H2O Wave that has important app information.
    """
    q.app.load, = await q.site.upload(['./static/load.gif'])

    # Create a list of available SEC 10-Ks to chat with
    supported_companies = {
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
    available_collections = [c.name for c in h2ogpte.list_recent_collections(0, 1000)]
    q.app.collections = [ui.choice(c, supported_companies[c]) for c in supported_companies.keys() if c in available_collections]

    q.app.initialized = True  # Save that we have setup the app


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
    q.page['chatbot'] = ui.chatbot_card(
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

    # Support the user asking multiple questions at once, show users a loading image
    starting_chat_length = q.client.chat_length
    q.client.chat_length += 2
    q.page['chatbot'].data += [q.client.chatbot, True]
    q.page['chatbot'].data += ["<img src='{}' height='200px'/>".format(q.app.load), False]
    await q.page.save()

    # Get a response from the LLM
    bot_res = await q.run(get_chat_answer, q.client.chat_session_id, q.client.chatbot)

    # Update the UI with the LLM's response
    diff = q.client.chat_length - starting_chat_length - 1
    q.page['chatbot'].data[-diff] = [bot_res, False]

    stream = chunk = ''
    for w in bot_res:
        chunk += w
        await q.sleep(0.01)
        if len(chunk) == 5:
            stream += chunk
            q.page['chatbot'].data[-diff] = [stream, False]
            await q.page.save()
            chunk = ''
    if chunk:
        q.page['chatbot'].data[-diff] = [stream + chunk, False]


def get_chat_answer(chat_session_id, question):
    """
    Interact with the Large Language Model.

    :param chat_session_id: The H2OGPTE ID for a specific chat session. Ensures related queries are contained in one chat thread.
    :param question: The input text into the chat bot from the end user.
    """

    try:
        h2ogpte = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))

        with h2ogpte.connect(chat_session_id) as session:
            reply = session.query(message=question, timeout=200)
        return reply.content.strip()

    except Exception as e:
        return f"Unable to get an response: {e}"


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
