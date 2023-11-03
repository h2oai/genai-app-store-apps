import os
import time
import random
from datetime import datetime

import toml
from loguru import logger
from h2ogpte import H2OGPTE
from h2o_wave import app, Q, ui, on, copy_expando, run_on, main

from src.prompts import (
    prompt_topic,
    prompt_question,
    prompt_feedback,
    prompt_best_answer,
    prompt_modifiers
)
from src.layout import (
    landing_page_layout,
    landing_page_view,
    waiting_dialog
)
from src.cards import chatbot_card

# Configurations
TOPICS_MIN = 8
TOPICS_MAX = 10
LOADER_CHAT = 'spiral.gif'
LOADER_PAGE = "bighead_load.gif"
CHATBOT_FILLER = "<center><img src={} height='150px'/></center>"


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
    print(q.args)


async def initialize_app(q: Q):
    logger.info("Initializing the app for the first time.")
    q.app.toml = toml.load("app.toml")
    q.app.loader_s, = await q.site.upload([f'./static/{LOADER_CHAT}'])
    q.app.loader_c, = await q.site.upload([f'./static/{LOADER_PAGE}'])

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
                ui.text("There are no documents available, please try again later."),
                ui.text("You can report this issue by sending an email to cloud-feedback@h2o.ai.")
            ],
            closable=False,
            blocking=True
        )
        return
    await landing_page_view(q)
    await selected_collection(q)

    q.client.initialized = True


@on()
async def selected_collection(q):
    logger.info("")
    topic_count = random.randint(TOPICS_MIN, TOPICS_MAX)
    query = prompt_topic.format_map({'count': topic_count})

    # UI we show while the LLM creates some topics
    q.page['chatbot'] = chatbot_card()
    all_collections_dropdown = [
        ui.dropdown(
            name="selected_collection",
            label="Select a collections of documents",
            value=q.client.selected_collection,
            trigger=True,
            choices=[
                ui.choice(
                    choice,
                    q.app.collections[choice]
                )
                for choice
                in q.app.collections.keys()
            ]
        )
    ]
    q.page["collection"] = ui.form_card(box=ui.box("collections"), items=all_collections_dropdown)
    q.client.cards.append("collection")
    await waiting_dialog(q, title="Generating topics about these documents to help you study!")

    # Generate and make a UI for topics
    topic_response = await q.run(llm_query_with_context, q.app.h2ogpte, q.client.selected_collection, query)
    q.client.topic_response = topic_response
    topics = ':'.join(topic_response.split(':')[1:]).strip().split('\n')

    h2ogpte = H2OGPTE(address=q.app.h2ogpte["address"], api_key=q.app.h2ogpte["api_key"])
    collection = h2ogpte.get_collection(q.client.selected_collection)
    all_topics_table = [
        ui.inline(
            justify='between',
            items=[
                ui.persona(
                    title=collection.name,
                    subtitle=collection.description,
                    size='xs',
                    initials_color="#000000"
                ),
                ui.text_s(
                    get_time_since(collection.updated_at)
                ),
            ]
        ),
        ui.table(
            name='topics_table',
            width='1',
            checkbox_visibility='always',
            single=True,
            values=[topics[0]],
            columns=[
                ui.table_column(
                    name='Topic',
                    label='Topic',
                    link=False,
                    min_width="500px"
                ),
            ],
            rows=[
                ui.table_row(
                    name=topic,
                    cells=[topic]
                )
                for topic
                in topics
            ]
        ),
    ]

    q.page["collection"] = ui.form_card(box=ui.box("collections"), items=all_collections_dropdown + [ui.separator("")] + all_topics_table + [ui.button(name='generate_question', label='Generate Question', primary=True)])

    q.page["collection-mobile"] = ui.form_card(
        box=ui.box("collections-mobile"),
        items=all_collections_dropdown
    )
    q.client.cards.append("collection-mobile")


@on()
async def generate_question(q):
    # Clean up topic string for cleaner query
    if q.args.topic is not None:
        q.client.topic = '.'.join(q.args.topics_table[0].split('.')[1:]).strip()
    query = prompt_question.format_map({'topic': q.client.topic, 'modifier': random.choice(prompt_modifiers)})
    logger.debug(f"Generate Question Query: {query}")

    # Append loading gif to data buffer while waiting on gpt
    q.page["chatbot"].data += [CHATBOT_FILLER.format(q.app.loader_c), False]
    q.page["collection"].generate_question.disabled = True
    await q.page.save()

    # Query to generate a possible question
    bot_res = await q.run(llm_query_with_context, q.app.h2ogpte, q.client.selected_collection, query)
    logger.debug(f"Generate Question Response: {bot_res}")

    # Clean up response and replace loading gif with response
    if ':' in bot_res:
        bot_res = ':'.join(bot_res.split(':')[1:]).lstrip()
    bot_res = f"**Question** {bot_res}"
    q.page['chatbot'].data[-1] = [bot_res, False]
    q.client.chat_length += 1
    q.client.last_question = bot_res
    q.page["collection"].generate_question.disabled = False


@on()
async def chatbot(q):
    if q.client.last_question is None:
        q.page['chatbot'].data += [q.client.chatbot, True]
        q.page['chatbot'].data += [f"Hi there! Please use the button to generate a question and start studying!", False]
        return

    # Add the answer to the chat window and create query
    answer = q.client.chatbot
    query = prompt_feedback.format_map({'question': q.client.last_question, 'answer': answer})
    q.page['chatbot'].data += [f"**Answer** {answer}", True]

    # Query to see if this is a good answer
    q.page["chatbot"].data += [CHATBOT_FILLER.format(q.app.loader_c), False]
    await q.page.save()
    bot_res = await q.run(llm_query_with_context, q.app.h2ogpte, q.client.selected_collection, query)
    q.page['chatbot'].data[-1] = [f"**Feedback** {bot_res}", False]

    # Get best answer
    query = prompt_best_answer.format_map({'question': q.client.last_question})
    q.page["chatbot"].data += [CHATBOT_FILLER.format(q.app.loader_c), False]
    await q.page.save()
    bot_res = await q.run(llm_query_with_context, q.app.h2ogpte, q.client.selected_collection, query)
    q.page['chatbot'].data[-1] = [f"**Better Answer** {bot_res}", False]


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
