from h2o_wave import Q, ui
import pandas as pd
from fpdf import FPDF
from loguru import logger
from .layout import layout


async def load_dash_page(q: Q,):
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
    await get_status(q, 0)


async def get_status(q: Q, step: int):
    items = [
        ui.inline([ui.text('Process: **{}**'.format(q.client.process_selected))], justify='center'),
        ui.separator()
        ]
    step_1 = q.client.texts['steps_texts']['step_1']
    step_2 = q.client.texts['steps_texts']['step_2']
    if step == 0:
        items += [
            ui.inline([
                ui.text(q.client.texts['steps_texts']['step_0']),
                ui.progress(label='', caption='Conectando', type='spinner', name='progress_docs'),
            ], justify='between', align='center'),
            ui.inline([
                ui.markup(f'<html><span style="opacity: 0.2;">{step_1}</font></html>'),
                ui.markup('<html><span style="opacity: 0.2;">...</font></html>'),
            ], justify='between', align='center'),
            ]
    elif step == 1:
        items += [
            ui.inline([
                ui.text(q.client.texts['steps_texts']['step_0']),
                ui.text('☑️'),
            ], justify='between', align='center'),
            ui.inline([
                ui.text(step_1),
                ui.progress(label='', caption='0%', type='spinner', name='progress_perguntas'),
            ], justify='between', align='center'),
            ui.inline([
                ui.markup(f'<html><span style="opacity: 0.2;">{step_2}</font></html>'),
            ], justify='between', align='center'),
            ]
    elif step == 2:
        items += [
            ui.inline([
                ui.text(q.client.texts['steps_texts']['step_0']),
                ui.text('☑️'),
            ], justify='between', align='center'),
            ui.inline([
                ui.text(step_1),
                ui.text('☑️'),
            ], justify='between', align='center'),
            ui.inline([
                ui.text(step_2),
                ui.progress(label='', caption='', type='spinner', name='progress'),
            ], justify='between', align='center'),
            ]
    elif step == 3:
        n_docs = len(q.client.document_names.keys())
        docs_texts = q.client.texts['steps_texts']['docs'].format(n_docs)
        items += [
            ui.inline([
                ui.text(q.client.texts['steps_texts']['step_0']),
                ui.text('☑️'),
            ], justify='between', align='center'),
            ui.inline([
                ui.text(step_1),
                ui.text('☑️'),
            ], justify='between', align='center'),
            ui.inline([
                ui.text(step_2),
                ui.text('☑️'),
            ], justify='between', align='center'),
            ui.separator(),
            ui.inline([
                ui.text(docs_texts),
            ], align='center'),
            ui.inline([
                ui.text(q.client.texts['steps_texts']['perguntas']),
            ], align='center'),
            ui.buttons([
                ui.button(name='resumo_botao', label=q.client.texts['steps_texts']['resumo_botao'], primary=True),
            ], justify='center'),
            ]
    elif step == 4:
        n_docs = len(q.client.document_names.keys())
        docs_texts = q.client.texts['steps_texts']['docs'].format(n_docs)
        try:
            filename = save_relatorio(q, q.client.current_summary)
        except:
            report = q.client.current_summary.encode('latin-1', 'ignore').decode('latin-1')
            filename = save_relatorio(q, report)
        download_path, = await q.site.upload([filename])
        items += [
            ui.inline([
                ui.text(q.client.texts['steps_texts']['step_0']),
                ui.text('☑️'),
            ], justify='between', align='center'),
            ui.inline([
                ui.text(step_1),
                ui.text('☑️'),
            ], justify='between', align='center'),
            ui.inline([
                ui.text(step_2),
                ui.text('☑️'),
            ], justify='between', align='center'),
            ui.separator(),
            ui.inline([
                ui.text(docs_texts),
            ], align='center'),
            ui.inline([
                ui.text(q.client.texts['steps_texts']['perguntas']),
            ], align='center'),
            ui.buttons([
                ui.button(name='resumo_botao', label=q.client.texts['steps_texts']['resumo_botao'], primary=True),
            ], justify='center'),
            ui.inline([
                ui.link(name='download_pdf', label='Download', path=download_path, download=True,  button=True),
            ], justify='center'),
            ]
        delete_filepath(filename)
    
    q.page['main_infos'] = ui.form_card(
        box=ui.box('zone_1_1_1', width='100%'),
        items=items
        )

def save_relatorio(q, text):
    if q.client.language == 'pt':
        title = 'RELATÓRIO - ' + q.client.process_selected
    else:
        title = 'REPORT - ' + q.client.process_selected
    filename = 'relatorio_' + q.client.process_selected + '.pdf'
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Times', '', 18)
    pdf.cell(w=180,
            h=20,
            txt=title,
            border=0,
            align='C',
            ln=1)
    pdf.set_font('Times', '', 12)
    pdf.multi_cell(w=180,
                h=6,
                txt=text,
                border=0,
                )
    pdf.output(filename, "F")
    return filename


def delete_filepath(filepath):
    import os
    try:
        os.unlink(filepath)
    except Exception as e:
        logger.warning(f'Failed to delete {filepath}. Reason: {e}')
