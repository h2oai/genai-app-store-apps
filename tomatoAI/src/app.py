import os

import toml

from h2o_wave import app, Q, handle_on, copy_expando, main

from loguru import logger

from src.handlers import handler
from src.layout import (
    layout,
    landing_page_view,
    image_view
)
from src.cards import chat_card


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

    if q.app.h2ogpt_url is None:
        q.app.h2ogpt_url = os.getenv("H2OGPT_URL")
    if q.app.h2ogpt_key is None:
        q.app.h2ogpt_key = os.getenv("H2OGPT_API_TOKEN")
    if q.app.load is None:
        q.app.load, = await q.site.upload(['./static/load.gif'])

    q.app.initialized = True


async def initialize_client(q: Q):
    logger.info("Initializing the client")
    q.client.plants = set()
    await image_view(q)
    q.page['chat'] = chat_card()

    layout(q)
    await landing_page_view(q)

    q.client.initialized = True
