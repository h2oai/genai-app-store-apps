from h2o_wave import Q, ui
import os
import pandas as pd
from .constants import *
from .layout import get_header_card, layout


async def load_home(q: Q,):
    await layout(q, [ui.zone(name="home", direction="row", size="100%")])
    processos = [processo for processo in os.listdir(PROCESSOS_FOLDER) if not processo.startswith('.')]
    h2o_logo_resize = (H2O_LOGO_DIM[0]*FACTOR_H2O_LOGO, H2O_LOGO_DIM[1]*FACTOR_H2O_LOGO)
    logo_resize = (LOGO_DIM[0]*FACTOR_LOGO, LOGO_DIM[1]*FACTOR_LOGO)
    stf_image = f'<img style="width:{logo_resize[0]}px;height:{logo_resize[1]}px;" src="{q.app.logo}"/>'
    v_line = f'<img style="width:{50}px;height:{logo_resize[1]}px;" src="{q.app.vline}"/>'
    h2o_image = f'<img style="width:{h2o_logo_resize[0]}px;height:{h2o_logo_resize[1]}px;" src="{q.app.h2o_logo}"/>'
    image_markup = ui.markup(f'<center> {stf_image} {v_line} {h2o_image} </center>')


    q.page["selecao_processos"] = ui.form_card(
        box=ui.box('home', height='80%', width='50%'),
        items=[
            image_markup,
            ui.separator(width='70%'),
            ui.dropdown(name='process_selected',
                    label=q.client.texts['process_number'],
                    required=True,
                    width='70%',
                    placeholder = q.client.texts['process_number_placeholder'],
                    value=q.client.process_selected,
                    choices=[ui.choice(name=opp, label=opp) for opp in sorted(processos)]),
            ui.inline([
                ui.button(name='reset', label=q.client.texts['back_botton'], primary=False),
                ui.button(name='submit_process', label=q.client.texts['submit_process'], primary=True),
                ], justify='center'),
            ui.separator(width='70%', label='or'),
            ui.inline([
                ui.file_upload(name='file_upload', label=q.client.texts['file_upload'], multiple=False, file_extensions=['zip'], compact=True),
                ui.button(name='submit_zip_file', label='', caption=q.client.texts['submit_zip_file'], primary=False, icon='Upload'),
                ], justify='center', align='end'),
        ])
    await get_header_card(q)