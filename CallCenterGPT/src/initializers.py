from h2o_wave import Q, ui
from src.utils import render_header, render_nav_bar, card_zones
from src.log import log
from src.config import Config, h2ogpte_config

"""Initialize client / browser"""
async def init_application(q:Q):
    '''
    Initialize the Application by setting up the layout, header, and navbar
    :param q:
    :return:
    '''
    if q.app.initialized:
        log.info("q.app.initialized - already initialised")
        return
    log.debug("Start Call center GPT App")

    q.app.global_config = Config()
    log.info(f"""GLOBAL CONFIG values:
              - domain_url: {q.app.global_config.domain_url}
              - is_cloud: {q.app.global_config.is_cloud}
              """)

    q.app.h2ogpte = h2ogpte_config

    q.app.initialized = True

    log.debug("Complete Call center GPT App")

async def init_browser(q:Q):
    '''
    Initialize browser (client)
    :param q:
    :return:
    '''
    # define layout and zones
    log.debug("Start init_browser")
    if q.client.initialized:
        log.debug("Function init_browser early exit")
        return
    
    # define layout
    await init_layout(q)
    await q.page.save()

    # render header
    await render_header(q)
    await q.page.save()

    # render navigation by default on tab 'getting started'
    await render_nav_bar(q, tab='#howtouse')
    await q.page.save()
    q.client.delete_cards= set()
    q.client.initialized = True
    log.debug("Complete init_browser")

async def init_layout(q:Q):
    '''
    Layout definitions for the client
    :param q:
    :return:
    '''
    from src.utils import heap_analytics
    import toml
    q.app.toml = toml.load("app.toml")

    log.debug("Start init_layout")
    q.page['meta'] = ui.meta_card(box='',
                                title='Call Center Sentiment GPT powered by Enterprise H2oGPT',
                                layouts=[
                                    # # xs: portrait phones, s: landscape phones, m: tablets, l: desktop, xl: large desktop
                                    ui.layout(
                                        breakpoint="xs",
                                        height="100vh",
                                        zones=[ui.zone("device-not-supported")],
                                    ),
                                    ui.layout(breakpoint='m', zones=card_zones(mode="home")),
                                ],
                                script=heap_analytics(
                                userid=q.auth.subject,
                                event_properties=f"{{"
                                f"version: '{q.app.toml['App']['Version']}', "
                                f"product: '{q.app.toml['App']['Title']}'"
                                f"}}",
                                ),
    )

    q.page["device-not-supported"] = ui.form_card(
        box="device-not-supported",
        items=[
            ui.text_xl(
                "This app was built for desktop or landscape view; it is not available on mobile."
            )
        ],
    )
    log.debug("Complete init_layout")