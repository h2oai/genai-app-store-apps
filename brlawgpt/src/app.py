from h2o_wave import Q, app, main, on, site, ui, run_on, copy_expando
import os
import logging
from pathlib import Path
import requests
from .texts_app import texts_app_ptbr, texts_app_en
from .doc_qna_h2ogpte import QnAManager, H2OGPTEClient
from .utils import get_body, get_questions, loading, loading_home
from .constants import *
from .layout import get_header_card, layout, get_home_items

logging.basicConfig(level=logging.INFO)

name_collection_temas='temas_stf'
description_collection_temas="Temas STF"

llm = "h2oai/h2ogpt-4096-llama2-70b-chat-4bit"

@app("/")
async def serve(q: Q):
    if not q.app.initialized:
        await initialize_app(q)
        q.app.initialized = True
    if not q.client.initialized:
        logging.info("New client session started.")
        q.client.texts = texts_app_ptbr
        q.client.language = 'ptbr'
        await layout(q)
        await get_home_items(q, flag="home")
        await q.page.save()
        q.client.initialized = True
        
    copy_expando(q.args, q.client)
    logging.debug('q.args: %s', q.args)
    await run_on(q)


async def initialize_app(q):
    q.app.h2ogpte_keys = {
                "address": os.getenv("H2OGPTE_URL", "https://internal.h2ogpte.h2o.ai"),
                "api_key": os.getenv("H2OGPTE_API_TOKEN"),
            }
    q.app.h2ogpte = H2OGPTEClient(q.app.h2ogpte_keys['address'], q.app.h2ogpte_keys['api_key'])
    q.app.collection_temas_id = q.app.h2ogpte.create_collection(name_collection_temas, description_collection_temas)
    q.app.h2ogpte.ingest_file_folder('temas_stf', q.app.collection_temas_id)
    q.app.loader, = await q.site.upload(['./static/loader_legal.gif'])
    q.app.backgroud, = await q.site.upload([BACKGROUND_IMAGE])


@on()
async def chatbot_brlaw(q: Q):
    await on_generating(q, q.client.chatbot_brlaw, q.client.peticao_chunks)


@on()
async def questions(q: Q):
    data = q.client.texts['questions_data']
    question_prompt = data['Question'][int(q.client.questions[0])]
    await on_generating(q, question_prompt, q.client.peticao_chunks)


async def on_generating(q, question_prompt, doc_chunks):
    q.app.h2ogpte = H2OGPTEClient(q.app.h2ogpte_keys['address'], q.app.h2ogpte_keys['api_key'])
    q.client.qnamanager = QnAManager(q.app.h2ogpte, llm, q.client.collection_peticao_id, q.app.collection_temas_id)
    pdf_docs = [q.client.path]
    q.page["card_1"].data += [question_prompt, True]
    q.page["card_1"].data += ["<img src='{}' height='40px'/>".format(q.app.loader), False]
    await q.page.save()
    output = await q.run(q.client.qnamanager.answer_question, q, question_prompt, pdf_docs, doc_chunks)
    q.page["card_1"].data[-1] = [output, False]
    q.page["card_1"].generating = False
    await q.page.save()


@on(arg='english')
async def set_english(q: Q):
    q.client.texts = texts_app_en
    q.client.language = 'en'
    await get_home_items(q, flag="home")
    await q.page.save()


@on(arg='portuguese')
async def set_portuguese(q: Q):
    q.client.texts = texts_app_ptbr
    q.client.language = 'ptbr'
    await get_home_items(q, flag="home")
    await q.page.save()

@on()
async def submit_url(q: Q):
    if q.client.url == "":
        await get_home_items(q, flag="home")
        await q.page.save()
    else:
        try:
            filename = q.client.url.split("/")[-1]
            q.client.path = Path('pdf/' + filename)
            await loading(q)
            response = requests.get(q.client.url)
            q.client.path.write_bytes(response.content)
            name_collection_peticao = f'collection_{filename}'
            description_collection_peticao = f'Collection for {filename}'
            q.app.h2ogpte = H2OGPTEClient(q.app.h2ogpte_keys['address'], q.app.h2ogpte_keys['api_key'])
            q.client.collection_peticao_id = q.app.h2ogpte.create_collection(name_collection_peticao, description_collection_peticao)
            q.client.qnamanager = QnAManager(q.app.h2ogpte, llm, q.client.collection_peticao_id, q.app.collection_temas_id)
            q.client.peticao_chunks = await q.run(q.app.h2ogpte.ingest_url, q.client.url, q.client.collection_peticao_id)
            q.page['meta'].dialog = None
            await get_home_items(q, flag="uploaded")
            await q.page.save()
            delete_filepath(q.client.path)
        except:
            await get_home_items(q, flag="home")
            await q.page.save()


@on()
async def submit_demo(q: Q):
    try:
        filename = q.client['initial_petition_demo']
        q.client.path = Path('./demo_files/' + filename)
        await loading(q)
        q.app.h2ogpte = H2OGPTEClient(q.app.h2ogpte_keys['address'], q.app.h2ogpte_keys['api_key'])
        q.client.collection_peticao_id = q.app.h2ogpte.create_collection(f'collection_{filename}', f'Collection for {filename}')
        q.client.qnamanager = QnAManager(q.app.h2ogpte, llm, q.client.collection_peticao_id, q.app.collection_temas_id)
        q.client.peticao_chunks = await q.run(q.app.h2ogpte.ingest_filepath, q.client.path, q.client.collection_peticao_id)
        q.page['meta'].dialog = None
        await get_home_items(q, flag="uploaded")
        await q.page.save()
    except:
        q.page['meta'].dialog = None
        await get_home_items(q, flag="home")
        await q.page.save()


@on()
async def reset(q: Q):
    await get_home_items(q, flag="home")
    await q.page.save()


def delete_filepath(filepath):
    import os
    try:
        os.unlink(filepath)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (filepath, e))

