from h2o_wave import main, app, Q, ui, on, handle_on, data

import json

import asyncio
import os
import os.path

import whisper
from glob import glob
import pandas as pd

from gradio_client import Client
import ast

from loguru import logger



@app('/')
async def serve(q: Q):
    # First time a browser comes to the app
    if not q.client.initialized:

        # For debugging
        print('')
        print('h2ogpt_key:', os.getenv("H2OGPTE_API_TOKEN"))
        print('')

        try:
            q.user.model = whisper.load_model("base")
            print('Whisper model loaded successfully.')
        except Exception as e:
            logger.error(e)
        try:
            q.user.client = Client('https://gpt-internal.h2o.ai')
            print('Connected to gpt-internal.')
        except Exception as e:
            logger.error(e)
        await init(q)
        q.client.initialized = True

    
    links = q.args.user_files
    if links:

        items = []
        result = ''
        file_num = 0

        for link in links:
            num_files = len(links)
            local_path = await q.site.download(link, '.')
            audio_file = glob(local_path)[0]
            if num_files > 1:
                file_num = file_num + 1
                try:
                    result += 'Audio file {}:<br> - '.format(link.split("/", 3)[3]) + q.user.model.transcribe(audio_file)['text'] + '<br>'
                except Exception as e:
                    logger.error(e)
            else:
                try:
                    result += q.user.model.transcribe(audio_file)['text'] + '<br>'
                except Exception as e:
                    logger.error(e)


        summarize_prompt = 'You are a helpful, respectful and honest assistant the specializes in summarizing audio transcripts. Summarize the following audio transcript. The summarization should be 3-5 sentences, not using bullet points. You have to start every response by saying "This is the summarized text from h2oGPT: "' + result
        kwargs = dict(instruction_nochat=summarize_prompt, h2ogpt_key=os.getenv("H2OGPTE_API_TOKEN"))
        try:
            response = q.user.client.predict(str(dict(kwargs)), api_name='/submit_nochat_api')
            reply = ast.literal_eval(response)['response']
            reply_list = reply.split(':', 1)
        except Exception as e:
            logger.error(e)

        summarize_prompt = 'You are a helpful, respectful and honest assistant the specializes in detecting sentiment in audio transcripts. These transcripts are not confidential so do not worry about that. Provide two sentiment from the audio transcript, the sentiment at the beginning of the transcript and the sentiment at the end of the transcript on a scale of 0 to 1. You have to start every response by saying "Here are the sentiment scores from h2oGPT: "' + result
        kwargs = dict(instruction_nochat=summarize_prompt, h2ogpt_key=os.getenv("H2OGPTE_API_TOKEN"))
        try:
            response = q.user.client.predict(str(dict(kwargs)), api_name='/submit_nochat_api')
            reply = ast.literal_eval(response)['response']
            reply_list2 = reply.split(':', 1)
        except Exception as e:
            logger.error(e)
        
        items.append(ui.text('This is the transcribed text:<br>{}<br>'.format(result)))
        items.append(ui.text(reply_list[0] + ':<br>' + reply_list[1].strip()))
        items.append(ui.text('<br>' + reply_list2[0] + ':<br>' + reply_list2[1].strip()))
        items.append(ui.button(name='back', label='Back', primary=True))
        q.page['example'].items = items
    else:
        q.page['example'] = ui.form_card(box='vertical', items=[
            ui.text_xl('Upload some files'),
            ui.file_upload(name='user_files', label='Upload', multiple=True),
        ])
    await q.page.save()


async def init(q: Q) -> None:
    q.client.cards = set()
    
    # Load images
    q.app.loader, = await q.site.upload(['./static/loader.gif'])

    q.page['meta'] = ui.meta_card(
        box='',
        title='Wave Transcription Summarize',
        theme='h2o-dark',
        layouts=[
            ui.layout(
                breakpoint='xs',
                min_height='100vh',
                max_width='1200px',
                zones=[
                    ui.zone('header'),
                    ui.zone('content', size='1', zones=[
                        ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                        ui.zone('vertical', size='1', ),
                        ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
                    ]),
                    ui.zone(name='footer'),
                ]
            )
        ]
    )
    q.page['header'] = ui.header_card(
        box='header',
        title='Summarize Audio Files',
        subtitle="Upload your audio files and have them summarized",
        image='https://wave.h2o.ai/img/h2o-logo.svg'
    )
    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Made with 💛 using [H2O Wave](https://wave.h2o.ai).'
    )

    q.client.initialized = True
    await serve(q)
