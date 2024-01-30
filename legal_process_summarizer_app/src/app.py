from h2o_wave import Q, app, main, on, site, ui, run_on, copy_expando
import os, json
import zipfile
from loguru import logger
from .texts_app import texts_app_eng, texts_app_pt
from .constants import *
from .layout import layout, get_sec_header_items
from .doc_qna_h2ogpte import QnAManager, H2OGPTEClient, HighlightDocs
from .page_highlight import load_highlight_page, display_highlights
from .page_dashboard import load_dash_page, get_status
from .page_home import load_home
from .page_chat import load_chat_page, display_doc_pdf


@app("/")
async def serve(q: Q):
    if not q.app.initialized:
        await initialize_app(q)
        q.app.initialized = True
    if not q.client.initialized:
        logger.info("New client session started.")
        q.client.language = 'eng'
        q.client.language_flag = '🇺🇸'
        q.client.texts = texts_app_eng
        q.client.initialized = True
        await initialize_client(q)

    copy_expando(q.args, q.client)
    logger.debug(f'q.args: \n {q.args}')
    await run_on(q)


async def initialize_app(q):
    q.app.h2ogpte_keys = {
                "address": os.getenv("H2OGPTE_URL"),
                "api_key": os.getenv("H2OGPTE_API_TOKEN"),
            }
    q.app.h2ogpte = H2OGPTEClient(q.app.h2ogpte_keys['address'], q.app.h2ogpte_keys['api_key'])
    q.app.loader, = await q.site.upload([LOADING_GIF])
    q.app.logo, = await q.site.upload([COMPANY_LOGO])
    q.app.h2o_logo, = await q.site.upload([H2O_LOGO])
    q.app.sec_image, = await q.site.upload([COMPANY_SEC_IMAGE])
    q.app.vline, = await q.site.upload([VLINE])


async def initialize_client(q):
    q.client.current_chat = ''
    q.client.process_selected = None
    q.client.contexto_processo = dict()
    q.client.current_summary = None
    q.client.highlight_pergunta = None
    q.client.max_ref = 3
    await load_home(q)
    await q.page.save()


@on(arg='portuguese')
async def set_portuguese(q: Q):
    q.client.language = 'pt'
    q.client.language_flag = '🇧🇷'
    q.client.texts = texts_app_pt
    await initialize_client(q)


@on(arg='english')
async def set_english(q: Q):
    q.client.language = 'eng'
    q.client.language_flag = '🇺🇸'
    q.client.texts = texts_app_eng
    await initialize_client(q)

@on()
async def chatbot_stfgpt(q: Q):
    await q.run(on_generating, q, q.client.chatbot_stfgpt)


def ingest_doc(q, pdf_file):
    logger.info(f'Ingesting file {pdf_file}')
    doc_name = os.path.basename(pdf_file)
    try:
        q.app.h2ogpte.ingest_filepath(pdf_file, q.client.collection_processo_id)
    except Exception as e:
        logger.error(f'Error ingesting file {pdf_file}: {e}')
        return False
    q.client.document_names[doc_name] = pdf_file
    return True


async def prepare_collection(q, processo, new=False):
    q.app.h2ogpte = H2OGPTEClient(q.app.h2ogpte_keys['address'], q.app.h2ogpte_keys['api_key'])
    pdf_files = get_all_files_in_folder(processo, new=new)
    q.client.document_names = dict()
    q.client.collection_processo_id = q.app.h2ogpte.create_collection(f'collection_{processo}', f'Coleção para o processo {processo}')
    n_docs = len(pdf_files)


    for i, pdf_file in enumerate(pdf_files):
        logger.info(f'Ingesting file {pdf_file} - {i} of {n_docs}')
        doc_name = os.path.basename(pdf_file)
        q.page["main_infos"].progress_docs.caption = '{}/{}'.format(i+1, n_docs)
        await q.page.save()
        try:
            await q.run(q.app.h2ogpte.ingest_filepath, pdf_file, q.client.collection_processo_id)

        except Exception as e:
            logger.error(f'Error ingesting file {pdf_file}: {e}')
            continue
        q.client.document_names[doc_name] = pdf_file

    await get_doc_id_dict(q)
    return

async def get_doc_id_dict(q):
    q.app.h2ogpte = H2OGPTEClient(q.app.h2ogpte_keys['address'], q.app.h2ogpte_keys['api_key'])
    doc_id_dict = await q.run(q.app.h2ogpte.list_all_docs, q.client.collection_processo_id)

    q.client.doc_type_dict = dict()
    for doc_name, doc_path in q.client.document_names.items():
        doc_type = doc_path.split('/')[-2]
        if q.client.doc_type_dict.get(doc_type):
            q.client.doc_type_dict[doc_type].append(doc_id_dict[doc_name])
        else:
            q.client.doc_type_dict[doc_type] = [doc_id_dict[doc_name]]
    return


@on('submit_process')
async def submit_process(q: Q):
    if q.client.process_selected == None or q.client.process_selected == '':
        q.page['meta'].notification_bar = ui.notification_bar(
                text=q.client.texts['error_message'],
                name="error_bar",
                type='error',
                timeout=3,
            )
        await q.page.save()
    else:
        import time
        start = time.time()
        q.page['meta'].notification_bar = None
        await load_dash_page(q)
        await q.page.save()
        q.client.current_chat = ''
        await prepare_collection(q, q.client.process_selected)    
        await get_status(q, 1)
        await q.page.save()
        q.client.qnamanager = QnAManager(q.app.h2ogpte, LLM)
        q.client.current_summary = await q.run(q.client.qnamanager.reduce_questions, q)
        doc_names = q.client.document_names.keys()
        q.page["docs"] = ui.form_card(
            box=ui.box('zone_1_1_2', width='100%', height='100%'),
            items=[
                ui.inline([
                    ui.text(q.client.texts['docs_indexed']),
                    ], direction='column', align='center'),
                ui.separator(),
                    ] + [ui.text(f'- {doc}') for doc in doc_names]
            )
        logger.warning(f'Process {q.client.process_selected} took {round(time.time() - start, 2)} seconds')
        await q.page.save()

@on()
async def submit_zip_file(q: Q):
    if q.client.file_upload is None:
        q.page['meta'].notification_bar = ui.notification_bar(
                text=q.client.texts['error_message_upload'],
                name="error_bar",
                type='error',
                timeout=3,
            )
        await q.page.save()
    else:
        q.page['meta'].notification_bar = None
        q.page['meta'].dialog = ui.dialog(
                title='Novo processo', 
                closable=False,
                blocking=True,
                items=[
                    ui.text(q.client.texts['dialog_upload']),
                    ui.textbox(name='novo_processo', label=q.client.texts['process_number_placeholder'], required=True),
                    ui.separator(),
                    ui.inline([
                        ui.button(name='submit_novo_processo', label='Upload', primary=False, icon='Upload'),
                    ], justify='center'),
                ])

        await q.page.save()


@on()
async def submit_novo_processo(q: Q):
    if q.client.novo_processo is None or q.client.novo_processo == '':
        q.page['meta'].notification_bar = ui.notification_bar(
                text=q.client.texts['dialog_upload'],
                name="error_bar",
                type='error',
                timeout=3,
            )
        await q.page.save()
    else:
        q.page['meta'].notification_bar = None
        q.client.process_selected = q.client.novo_processo
        path_novo_processo = TEMP_NEW_PROCESS_FOLDER + q.client.process_selected
        path_to_zip_file = await q.site.download(url=q.client.file_upload[0], path=TEMP_FOLDER_ZIPFILES)

        if not os.path.exists(path_novo_processo):
            os.mkdir(path_novo_processo)
        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
            zip_ref.extractall(path_novo_processo)
        os.remove(path_to_zip_file)

        await load_dash_page(q)
        await q.page.save()
        q.client.current_chat = ''
        await prepare_collection(q, q.client.process_selected, new=True)
        await get_status(q, 1)
        await q.page.save()
        q.client.qnamanager = QnAManager(q.app.h2ogpte, LLM)
        q.client.current_summary = await q.run(q.client.qnamanager.reduce_questions, q)
        doc_names = q.client.document_names.keys()
        q.page["docs"] = ui.form_card(
            box=ui.box('zone_1_1_2', width='100%', height='100%'),
            items=[
                ui.inline([
                    ui.text(q.client.texts['docs_indexed']),
                    ], direction='column', align='center'),
                ui.separator(),
                    ] + [ui.text(f'- {doc}') for doc in doc_names]
            )
        await q.page.save()


@on()
async def resumo_botao(q: Q):
    await get_status(q, 4)
    title = 'RELATÓRIO' if q.client.language == 'pt' else 'REPORT'
    q.page["resumo"] = ui.markdown_card(
        box=ui.box('zone_1_2', height='100%', width='100%'),
        title=title,
        content=q.client.current_summary
    )
    q.page["ref_botao"] = ui.form_card(
        box=ui.box('zone_1_3', height='100%', width='100%'),
        items=[
            ui.inline([
            ui.button(name='referencias', icon='ChevronRight', caption=q.client.texts['references']['caption']),
            ], justify='center', align='center', direction='column'),
        ])
    q.page["header"].secondary_items=get_sec_header_items(q, 'highlight')
    await q.page.save()


@on()
async def referencias(q: Q):
    choices = [q.client.texts['topic_labels'][key] for key in q.client.contexto_processo.keys()]
    zones=[
            ui.zone(name="zone_1_1", direction="column", size="20%",
                    zones=[
                ui.zone(name="zone_1_1_1", direction="row", size="62%"),
                ui.zone(name="zone_1_1_2", direction="row", size="38%"),
            ]),
            ui.zone(name="zone_1_2", direction="row", size="38%"),
            ui.zone(name="zone_1_4", direction="row", size="38%"),
            ui.zone(name="zone_1_3", direction="row", size="3%"),
        ]
    await layout(q, zones)
    q.page["perguntas"] = ui.form_card(
        box=ui.box('zone_1_4', height='100%', width='100%'),
        items=[
            ui.inline([
                ui.text_l(q.client.texts['references']['title']),
            ], justify='center', align='center', direction='column'),
            ui.separator(),
            ui.dropdown(
                name='highlight_pergunta',
                label=q.client.texts['references']['dropdown'],
                trigger=True,
                choices=[ui.choice(name=pergunta, label=pergunta) for i, pergunta in enumerate(choices)],
            ),
            ui.separator(),
        ])
    q.page["ref_botao"] = ui.form_card(
        box=ui.box('zone_1_3', height='100%', width='100%'),
        items=[
            ui.inline([
            ui.button(name='fechar_referencias', icon='ChevronLeft', caption=q.client.texts['references']['caption_close']),
            ], justify='center', align='center', direction='column'),
        ])
    await q.page.save()

@on('voltar')
@on('fechar_referencias')
async def dash_page(q: Q):
    zones=[
            ui.zone(name="zone_1_1", direction="column", size="20%",
                    zones=[
                ui.zone(name="zone_1_1_1", direction="row", size="62%"),
                ui.zone(name="zone_1_1_2", direction="row", size="38%"),
            ]),
            ui.zone(name="zone_1_2", direction="row", size="38%"),
            ui.zone(name="zone_1_3", direction="row", size="3%"),
        ]
    await layout(q, zones)
    q.page["ref_botao"] = ui.form_card(
        box=ui.box('zone_1_3', height='100%', width='100%'),
        items=[
            ui.inline([
            ui.button(name='referencias', icon='ChevronRight', caption=q.client.texts['references']['caption']),
            ], justify='center', align='center', direction='column'),
        ])
    if q.args.__wave_submission_name__ == 'voltar':
        q.page["header"].secondary_items=get_sec_header_items(q, 'highlight')
    await q.page.save()



@on()
async def highlight_pergunta(q: Q):
    q.client.ref_index = 0
    highlights = await display_highlights(q)
    await load_highlight_page(q, highlights)
    await q.page.save()


@on()
async def chat_page_button(q: Q):
    await load_chat_page(q)
    await q.page.save()


@on()
async def previous_ref(q: Q):
    if q.client.ref_index > 0:
        q.client.ref_index -= 1
    highlights = await display_highlights(q)
    await load_highlight_page(q, highlights)
    ref_button_status(q)
    await q.page.save()

@on()
async def next_ref(q: Q):
    if q.client.ref_index < q.client.max_ref:
        q.client.ref_index += 1
    highlights = await display_highlights(q)
    await load_highlight_page(q, highlights)
    ref_button_status(q)
    await q.page.save()

@on()
async def previous_ref_chat(q: Q):
    if q.client.ref_index_chat > 0:
        q.client.ref_index_chat -= 1
    await display_doc_pdf(q, highlight=True)
    ref_button_status_chat(q)
    await q.page.save()

@on()
async def next_ref_chat(q: Q):
    if q.client.ref_index_chat < q.client.max_ref:
        q.client.ref_index_chat += 1
    await display_doc_pdf(q, highlight=True)
    ref_button_status_chat(q)
    await q.page.save()


def ref_button_status(q):
    if q.client.ref_index == 0:
        q.page["perguntas"].previous_ref.disabled = True
        q.page["perguntas"].next_ref.disabled = False
    elif q.client.ref_index == q.client.max_ref - 1:
        q.page["perguntas"].next_ref.disabled = True
        q.page["perguntas"].previous_ref.disabled = False
    else:
        q.page["perguntas"].previous_ref.disabled = False
        q.page["perguntas"].next_ref.disabled = False
    return

def ref_button_status_chat(q):
    if q.client.ref_index_chat == 0:
        q.page["sidebar"].previous_ref_chat.disabled = True
        q.page["sidebar"].next_ref_chat.disabled = False
    elif q.client.ref_index_chat == q.client.max_ref - 1:
        q.page["sidebar"].next_ref_chat.disabled = True
        q.page["sidebar"].previous_ref_chat.disabled = False
    else:
        q.page["sidebar"].previous_ref_chat.disabled = False
        q.page["sidebar"].next_ref_chat.disabled = False
    return


# =======================================================================================================================


async def on_generating(q, question_prompt):
    q.page['meta'].notification_bar = None
    q.app.h2ogpte = H2OGPTEClient(q.app.h2ogpte_keys['address'], q.app.h2ogpte_keys['api_key'])
    q.client.qnamanager = QnAManager(q.app.h2ogpte, LLM)
    q.page["chatbot_card"].data += [question_prompt, True]
    q.page["chatbot_card"].data += ["<img src='{}' height='40px'/>".format(q.app.loader), False]
    await q.page.save()
    output = await q.run(q.client.qnamanager.answer_question, q, question_prompt)
    q.page["chatbot_card"].data[-1] = [output, False]
    q.page["chatbot_card"].generating = False
    await display_doc_pdf(q, highlight=True)
    await q.page.save()


@on('reset')
@on('home')
async def reset(q: Q):
    cards_del = ['chatbot_card', 'resumo', 'ref_botao', 'perguntas', 'docs', 'main_infos']
    for card in cards_del:
        del q.page[card]

    highlight_docs = HighlightDocs('')
    highlight_docs.delete_all_files()
    await initialize_client(q)
    # delete_old_processes()


def get_all_files_in_folder(processo, new=False):
    if new:
        processo_list_path = './processo_list_delete.json'
        folder = TEMP_NEW_PROCESS_FOLDER + processo
        with open(processo_list_path, "r") as json_file:
            existing_processos_folder = json.load(json_file)

        if folder not in existing_processos_folder:
            existing_processos_folder.append(folder)
        with open(processo_list_path, "w", encoding="utf-8") as json_file:
            json.dump(existing_processos_folder, json_file, indent=4)
    else:
        folder = os.path.join(PROCESSOS_FOLDER, processo)
    pdf_files = []
    for dirpath, dirs, files in os.walk(folder):
        for filename in files:
            if filename.endswith('.pdf'):
                pdf_files.append(os.path.join(dirpath, filename))
    return pdf_files


def delete_old_processes():
    import shutil
    processo_list_path = './processo_list_delete.json'
    with open(processo_list_path, "r") as json_file:
        existing_processos_folder = json.load(json_file)
    for folder in existing_processos_folder:
        try:
            shutil.rmtree(folder)
        except:
            pass
    with open(processo_list_path, "w", encoding="utf-8") as json_file:
        json.dump([], json_file, indent=4)
    return