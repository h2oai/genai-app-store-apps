from h2o_wave import Q, ui
import glob
from .doc_qna_h2ogpte import HighlightDocs
from loguru import logger


async def load_highlight_page(q: Q, highlights: list):
    choices = [q.client.texts['topic_labels'][key] for key in q.client.contexto_processo.keys()]
    q.page["perguntas"] = ui.form_card(
        box=ui.box('zone_1_4', height='100%', width='100%'),
        items=[
            ui.inline([
                ui.text_l(q.client.texts['references']['title']),
                ], justify='center'), 
            ui.separator(),
            ui.dropdown(
                name='highlight_pergunta',
                label=q.client.texts['references']['dropdown'],
                value=q.client.highlight_pergunta,
                trigger=True,
                choices=[ui.choice(name=pergunta, label=pergunta) for i, pergunta in enumerate(choices)],
            ),
            ui.separator(),
        ui.inline([
            ui.button(name='previous_ref', label='', primary=False, icon='ChevronLeft', disabled=True),
            ui.button(name='next_ref', label='', primary=False, icon='ChevronRight'),
        ], justify='center'),
       ] + highlights)


async def display_highlights(q: Q):
    label = list(q.client.texts['topic_labels'].keys())[list(q.client.texts['topic_labels'].values()).index(q.client.highlight_pergunta)]
    markers = q.client.contexto_processo[label]
    highlight_docs = HighlightDocs(q.client.process_selected)
    score, doc_path = highlight_docs.highlight_pdf(q, markers, q.client.ref_index)
    score = round(float(score)*100)
    paths = [doc_path]
    logger.info(f"doc_path: {doc_path}")
    q.client.ref, = await q.site.upload(paths)
    doc_name = doc_path.split('/')[-1].replace('.pdf', '')
    items = [
        ui.inline([
            ui.text(q.client.texts['references']['reference_number'].format(q.client.ref_index + 1)),
            ui.text(q.client.texts['references']['relevance'].format(doc_name, score)),
            ui.text(f"""<object data="{q.client.ref}" type="application/pdf" width="600px" height="500px"></object>"""),
        ], direction='column', align='center'),
    ]
    return items

