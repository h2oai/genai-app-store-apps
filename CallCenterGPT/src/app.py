import traceback
import os
from h2o_wave import app, Q, main, handle_on
from src.initializers import init_application,  init_browser
from src.utils import render_error_page
from src.handlers import render_page
from src.log import log, setup_logger


def on_startup():
    """Initializer logger"""
    setup_logger()
    log.info('================================================App started!')

@app('/', on_startup=on_startup, mode='unicast')
async def serve(q: Q):
    """
    Handle user interactions such as arriving at the app for the first time or clicking a button
    """
    try:
        log.info("========================== Start Serve Function ===============================")
        log.info(f"q.auth.username: {q.auth.username}")
        log.info(f"q.args: {q.args}")
        log.info(f"q.client: {q.client}")
        log.info(f"q.user: {q.user}")
        log.info(f"q.events: {q.events}")
        log.info(f"q.app: {q.app}")
        log.info(f"H2O_CLOUD_INSTANCE_OWNER: {os.environ.get('H2O_CLOUD_INSTANCE_OWNER')}")
        log.info(f"q.auth.subject: {q.auth.subject}")
        log.info(f"q.auth.username: {q.auth.username}")

        """ Initialize the Application"""
        log.info("init application")
        await init_application(q)
        log.info("end init application")

        """ Initialize browser/tab"""
        log.debug("Main. Before init_browser")
        await init_browser(q)

        # render main page first time only
        log.info("Main. Before render_page")
        if (not q.args['details'] and
            not q.args['delete']
            ):
            log.info("Render Page")
            await render_page(q)

        # handle navigation clicks
        log.debug("Main. Before handle_on")
        await handle_on(q)
        log.debug("Main. After handle_on")

    # In the case of an exception, handle and report it to the user
    except Exception as err:
        log.error(f"Unhandled Application Error: {str(err)}")
        log.error(traceback.format_exc())
        await render_error_page(q, str(err))