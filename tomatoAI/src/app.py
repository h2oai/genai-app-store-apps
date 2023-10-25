import os

import toml

from h2o_wave import app, Q, handle_on, copy_expando, main

from loguru import logger

#from src.wave_utils import heap_analytics
from src.handlers import handler
from src.layout import layout
from src.view import landing_page_view


@app('/')
async def serve(q: Q):
    logger.info("Starting user request")
    logger.debug(q.args)
    copy_expando(q.args, q.client)

    if not q.app.initialized:
        await initialize_app(q)

    if not q.client.initialized:
        await initialize_client(q)

    if not await handle_on(q):
        await handler(q)

    await q.page.save()

    logger.info("Ending user request")


async def initialize_app(q: Q):
    logger.info("Initializing the app for all users and sessions")
    q.app.toml = toml.load("app.toml")

    if q.app.home_image is None:
        (q.app.home_image,) = await q.site.upload(['./static/home.jpg'])
    if q.app.app_icon is None:
        (q.app.app_icon,) = await q.site.upload(['./static/icon.jpg'])
    if q.app.llm_url is None:
        q.app.llm_url = q.app.toml["H2OGPT"]["H2OGPT_URL"]
    if q.app.h2ogpt_key is None:
        q.app.h2ogpt_key = os.getenv("H2OGPT_KEY", "H2OGPT_SECRET")

    q.app.initialized = True


async def initialize_client(q: Q):
    logger.info("Initializing the client")
    q.client.plants = set()

    layout(q)
    await landing_page_view(q)

    q.client.initialized = True


