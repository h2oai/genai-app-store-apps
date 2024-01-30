from h2o_wave import Q, ui, data
import glob
from .layout import layout, get_sec_header_items
from .doc_qna_h2ogpte import QnAManager, H2OGPTEClient, HighlightDocs
from .constants import *
from loguru import logger


async def load_chat_page(q: Q):
    q.client.ref_index_chat = 0
    zones=[
            ui.zone(name="chat_sidebar", direction="column", size="30%"),
            ui.zone(name="chat_content", direction="column", size="70%"),
        ]
    await layout(q, zones)
    q.page["header"].secondary_items=get_sec_header_items(q, 'chat')
    if q.client.display_doc is None:
        q.client.display_doc = list(q.client.document_names.keys())[0]

    await display_doc_pdf(q)
    q.page["chatbot_card"] = ui.chatbot_card(
        box=ui.box('chat_content', height='100%'),
        data=data(
            "content from_user",
            t="list",
            rows=q.client.texts['first_rows'],
        ),
        events=["stop"],
        name="chatbot_stfgpt",
        )
    await q.page.save()
    q.app.h2ogpte = H2OGPTEClient(q.app.h2ogpte_keys['address'], q.app.h2ogpte_keys['api_key'])
    q.client.qnamanager = QnAManager(q.app.h2ogpte, LLM)     
    first_query = q.client.qnamanager._write_initial_prompt(q)
    q.page["chatbot_card"].data += [first_query, False]
    q.page["chatbot_card"].generating = False
    await q.page.save()


async def display_doc_pdf(q: Q, highlight=False):
    if highlight:
        highlight_docs = HighlightDocs(q.client.process_selected)
        score, doc_path = highlight_docs.highlight_pdf(q, q.client.current_context, q.client.ref_index_chat)
        score = round(float(score)*100)
        paths = [doc_path]
        q.client.ref, = await q.site.upload(paths)
        doc_name = paths[0].split('/')[-1].replace('.pdf', '')
        q.page["sidebar"] = ui.form_card(
            box=ui.box('chat_sidebar', height='100%'),
            items=[
                ui.inline([ui.text('Process: **{}**'.format(q.client.process_selected))], justify='center'),
                ui.separator(),
                ui.inline([
                    ui.button(name='previous_ref_chat', label='', primary=False, icon='ChevronLeft', disabled=True),
                    ui.button(name='next_ref_chat', label='', primary=False, icon='ChevronRight'),
                ], justify='center'),
                ui.inline([
                    ui.text(q.client.texts['references']['reference_number'].format(q.client.ref_index_chat + 1)),
                    ui.text(q.client.texts['references']['relevance'].format(doc_name, score)),
                    ui.text(f"""<object data="{q.client.ref}" type="application/pdf" width="420px" height="520px"></object>"""),
                ], direction='column', align='center'),
            ])
        # highlight_docs.clean_up()
    else:
        q.page["sidebar"] = ui.form_card(
            box=ui.box('chat_sidebar', height='100%'),
            items=[
                ui.inline([ui.text('Process: **{}**'.format(q.client.process_selected))], justify='center'),
                ui.separator(),
                ui.inline([ui.text(q.client.texts['references']['sidebar_subtext'])], justify='center'),
            ])

