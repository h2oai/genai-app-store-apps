from h2o_wave import main, app, Q, ui, run_on, copy_expando
import os
import toml

from loguru import logger

from src.generate_content import generate_content_ui, initialize_generate_content_app, initialize_generate_content_client
from src.wave_utils import heap_analytics


@app('/')
async def serve(q: Q):
    logger.info("Starting user request")
    logger.debug(q.args)
    copy_expando(q.args, q.client)  # Save any UI responses of the User to their session

    if not q.client.initialized:
        await initialize_session(q)

    await run_on(q)
    await q.page.save()

    logger.info("Ending user request")


async def initialize_app(q: Q):
    logger.info("Initializing the app for all users and sessions - this runs the first time someone visits this app")
    q.app.toml = toml.load("app.toml")
    q.app.load, = await q.site.upload(['./static/load.gif'])

    initialize_generate_content_app(q)

    q.app.initialized = True


async def initialize_session(q: Q):
    logger.info("Initializing the app for this browser session")
    if not q.app.initialized:
        await initialize_app(q)

    q.client.cards = []
    initialize_generate_content_client(q)
    landing_page_layout(q)

    await generate_content_ui(q)
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
                page=os.getenv("SECONDARY_COLOR", "#E8E5E1"),
            )
        ],
        layouts=[
            ui.layout(
                breakpoint='xs',
                min_height='100vh',
                max_width="1200px",
                zones=[
                    ui.zone(name='header'),
                    ui.zone(name='body', size='1'),
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
                        "https://h2o.ai/content/experience-fragments/h2o/us/en/site/header/master/_jcr_content/root/container/header_copy/logo.coreimg.svg/1696007565253/h2o-logo.svg"
                        ),
        items=[
            ui.persona(title="Guest User", initials_color="#000000", initials="G", size="xs"),
        ]
    )

    q.page["footer"] = ui.footer_card(
        box="footer",
        caption="Made with 💛 and [H2O Wave](https://wave.h2o.ai)."
    )



