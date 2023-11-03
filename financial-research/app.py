import os

from h2o_wave import app, Q, ui, on, handle_on, data, main, copy_expando, run_on
from h2ogpte import H2OGPTE


@app('/')
async def serve(q: Q):
    print(q.args)
    if not q.client.initialized:
        await init(q)
        q.client.initialized = True

    copy_expando(q.args, q.client)
    await run_on(q)
    await q.page.save()


async def init(q: Q):
    if not q.app.initialized:
        q.app.load, = await q.site.upload(['./static/load.gif'])

        q.app.h2ogpte = {"address": os.getenv("H2OGPTE_URL"), "api_key": os.getenv("H2OGPTE_API_TOKEN")}

        all_choices = {
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

        h2ogpte = H2OGPTE(address=q.app.h2ogpte["address"], api_key=q.app.h2ogpte["api_key"])

        collection_names = [c.name for c in h2ogpte.list_recent_collections(0, 1000)]
        q.app.available_choices = [ui.choice(c, all_choices[c]) for c in all_choices.keys() if c in collection_names]

        q.app.initialized = True

    q.client.collection_name = "ABBOTT_LABORATORIES_145_2021"
    q.client.chat_length = 0

    q.page['meta'] = ui.meta_card(
        box='',
        title='Digital Assets Investment Research',
        theme='solarized',
        layouts=[
            ui.layout(
                breakpoint='m',
                min_height='100vh',
                max_width='1200px',
                zones=[
                    ui.zone('header'),
                    ui.zone('content', size='1', zones=[
                        ui.zone('vertical', size='1', ),
                        ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                        ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
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
    await home(q)


@on()
async def home(q: Q):
    q.page['image'] = ui.tall_info_card(
        box=ui.box('vertical'),
        title='',
        name='image_card',
        caption='Named Entity Extraction and Text Summarization',
        image_height='400px',
        image='https://franklintempletonprod.widen.net/content/fghctkvqjy/webp/uk-gilts-masthead-640x360.jpg')

    q.page['selectors'] = ui.form_card(
        box=ui.box('horizontal', size='0'),
        items=[
            ui.choice_group(name='collection_name', label='Select a firm to research', value=q.client.collection_name,
                            choices=q.app.available_choices, trigger=True),
        ]
    )

    await collection_name(q)


@on()
async def collection_name(q):

    # Log into Helium
    h2ogpte = H2OGPTE(address=q.app.h2ogpte["address"], api_key=q.app.h2ogpte["api_key"])

    collections = h2ogpte.list_recent_collections(0, 1000)

    collection_id = [i.id for i in collections if i.name == q.client.collection_name][0]

    # Start chat session
    session = h2ogpte.create_chat_session(collection_id)
    print(session)
    q.client.chat_session_id = session

    q.page['chatbot'] = ui.chatbot_card(
        name='chatbot_name',
        box='horizontal',
        data=data('content from_user', t='list', rows=[
            ["Welcome! What do you want to know about the collection called **{}**?".format(q.client.collection_name), False]
        ])
    )


@on()
async def chatbot_name(q: Q):
    print(q.client)
    starting_chat_length = q.client.chat_length
    q.client.chat_length += 2

    q.page['chatbot'].data += [q.client.chatbot_name, True]
    q.page['chatbot'].data += ["<img src='{}' height='200px'/>".format(q.app.load), False]
    await q.page.save()

    bot_res = await q.run(get_chat_answer, q.app.h2ogpte, q.client.chat_session_id, q.client.chatbot_name)

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


def get_chat_answer(connection_details, chat_session_id, question):

    try:
        h2ogpte = H2OGPTE(address=connection_details["address"], api_key=connection_details["api_key"])

        with h2ogpte.connect(chat_session_id) as session:
            reply = session.query(message=question, timeout=200)
        return reply.content.strip()

    except Exception as e:
        return f"Unable to get an response: {e}"
