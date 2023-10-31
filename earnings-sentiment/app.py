from h2o_wave import main, app, Q, ui, on, handle_on, data, pack
from loguru import logger

from helpers import *

import toml

import json
import numpy as np
import pandas as pd
import os
import hashlib

def heap_analytics(userid, event_properties=None) -> ui.inline_script:

    if "HEAP_ID" not in os.environ:
        return
        
    heap_id = os.getenv("HEAP_ID")
    script = f"""
window.heap=window.heap||[],heap.load=function(e,t){{window.heap.appid=e,window.heap.config=t=t||{{}};var r=document.createElement("script");r.type="text/javascript",r.async=!0,r.src="https://cdn.heapanalytics.com/js/heap-"+e+".js";var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(r,a);for(var n=function(e){{return function(){{heap.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}},p=["addEventProperties","addUserProperties","clearEventProperties","identify","resetIdentity","removeEventProperty","setEventProperties","track","unsetEventProperty"],o=0;o<p.length;o++)heap[p[o]]=n(p[o])}};
heap.load("{heap_id}"); 
    """

    if userid is not None:  # is OIDC Enabled? we do not want to identify all non-logged in users as "none"
        identity = hashlib.sha256(userid.encode()).hexdigest()
        script += f"heap.identify('{identity}');"

    if event_properties is not None:
        script += f"heap.addEventProperties({event_properties})"

    return ui.inline_script(content=script)

@app('/')
async def serve(q: Q):
<<<<<<< HEAD
    q.app.toml = toml.load("app.toml") #loading analytics

    #q.page['meta'].side_panel = None
    q.page['meta'] = ui.meta_card(
        box='',
        script=heap_analytics(
        userid=q.auth.subject,
        event_properties=f"{{"
          f"version: '{q.app.toml['App']['Version']}', "
          f"product: '{q.app.toml['App']['Title']}'"
          f"}}",)
    )
    await q.page.save()
=======
    try: 
        q.page['meta'].side_panel = None
        await q.page.save()
>>>>>>> main

        # First time a browser comes to the app
        if not q.client.initialized:
            await init(q)
            q.client.initialized = True

        # Other browser interactions
        await handle_on(q)
        await q.page.save()
    
    except Exception as e:
        logger.error(e)
        logger.info('Startup Loading Failed!')

async def init(q: Q) -> None:
    try:
        q.client.cards = set()
        q.app.step1_loader, = await q.site.upload(['./static/step1.gif'])
        q.app.step2_loader, = await q.site.upload(['./static/step2.gif'])
        q.app.step3_loader, = await q.site.upload(['./static/step3.gif'])
        q.app.step4_loader, = await q.site.upload(['./static/step4.png'])

        q.client.nav_value = "home"
        q.client.detailed_quarter = "2024 Q1"
        q.client.company = "FEDEX"
        with open('./static/all_transcripts.json', 'r') as f:
            q.client.transcripts = json.load(f)
        with open('./static/chunked_transcript.json', 'r') as f:
            q.client.chunks = json.load(f)
        q.client.ratings_table = get_ratings_table(q.client.transcripts)
        q.client.close_price = get_close_price()
        q.client.speakers = get_speaker_stats(q.client.transcripts.get(q.client.detailed_quarter).get('url'), q.client.chunks, q.client.company)

        q.client.speakers_table = read_markdown(q.client.transcripts.get(q.client.detailed_quarter).get('speakers_table')).reset_index()
        q.client.speakers_table = q.client.speakers_table.drop(columns=['level_0']).iloc[1::].dropna()
        q.client.speakers_table['level_1'] = q.client.speakers_table['level_1'].str.strip()

        q.client.sentiment_stars = plot_sentiment_stars(q.client.ratings_table)

        

        series_data = []
        for k, v in q.client.chunks.items():
            if v.get('sentiment') is not None:
                series_data = series_data + [{'chunk': float(k), 
                                            'speaker': v.get('speaker'),
                                            'sentiment': v.get("sentiment").get("Rating"),
                                            'defensiveness': v.get("defensiveness").get("Rating")
                                            }]
        series_data = pd.DataFrame(series_data)
        q.client.series_data = series_data[series_data.speaker != "Operator"]

        q.page['meta'] = ui.meta_card(box='', layouts=[ui.layout(breakpoint='xs', min_height='100vh', zones=[
                ui.zone('header', size='80px'),
                ui.zone('main', size='1', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                        ui.zone(name="sidebar", direction=ui.ZoneDirection.COLUMN, size="15%"),
                        ui.zone('content', direction=ui.ZoneDirection.COLUMN, size="85%",  zones=[
                            ui.zone('body_header'),
                            # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                            ui.zone('body_top', direction=ui.ZoneDirection.ROW, zones=[
                                ui.zone('body_summary'),
                                ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center'),
                            ]),
                            ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                            ui.zone('vertical'),
                        ]),
                    ]),
                ])
            ])])
        q.page['header'] = ui.header_card(
            box='header', color='transparent',
            title='Analyzing Earnings Transcripts',
            subtitle="Powered by H2O Gen AI",
            image='https://wave.h2o.ai/img/h2o-logo.svg',
        )
        q.page['footer'] = ui.footer_card(
            box='footer',
            caption='Made with 💛 using [H2O Wave](https://wave.h2o.ai).'
        )

        await home(q)

    except Exception as e:
        logger.error(e)
        logger.info("Loading JSON Failed!")

@on()
async def home(q: Q):

    try:
        clear_cards(q, ignore=['header', 'footer'])
        q.page['meta'].side_panel = None
        q.client.nav_value = "home"
        await q.page.save()
        await get_nav(q)

        add_card(q, 'quarter_name', ui.form_card(
            box=ui.box('body_header'),
            items=[ui.inline(justify='center', items=[
                ui.text_xl('Earnings Call: {}'.format(q.client.detailed_quarter))])
                ]
        ))

        add_card(q, 'quarter_summary0', ui.form_card(
            box=ui.box('body_summary', width='500px', order=0),
            items=[ui.inline(items=[ui.text("**Overall Analysis**")], justify='center'),
                ui.text('*Positive tone and language used throughout the transcript, with mentions of "strong start for the year," "cost savings," "momentum," "differentiated network," "great culture," and "incredible opportunity".*')]
        ))


        add_card(q, 'quarter_summary2', ui.wide_series_stat_card(
            box=ui.box('body_summary', width='500px', height='140px', order=2),
            title='Overall Sentiment Ranking',
            value='={{intl qux minimum_fraction_digits=0 maximum_fraction_digits=0}}',
            aux_value='',
            data=dict(qux=int(q.client.ratings_table[q.client.ratings_table.Quarter == q.client.detailed_quarter].Rating.iloc[0].strip())),
            plot_type='area',
            plot_value='qux',
            plot_color='$green',
            plot_data=data('foo qux', 3, rows=q.client.series_data[['chunk', 'sentiment']].astype(str).values.tolist()),
            plot_zero_value=0,
            plot_curve='linear',
            )
        )

        add_card(q, 'quarter_summary3', ui.wide_series_stat_card(
            box=ui.box('body_summary', width='500px', height='140px', order=3),
            title='Defensiveness Ranking',
            value='={{intl qux minimum_fraction_digits=0 maximum_fraction_digits=0}}',
            aux_value='',
            data=dict(qux=int(round(q.client.series_data.defensiveness.mean()))),
            plot_type='area',
            plot_value='qux',
            plot_color='$red',
            plot_data=data('foo qux', 3, rows=q.client.series_data[['chunk', 'defensiveness']].astype(str).values.tolist()),
            plot_zero_value=0,
            plot_curve='linear',
            )
        )

            
        company_speakers = q.client.speakers[q.client.speakers.company == q.client.company]
        for idx, row in company_speakers.iterrows():
            add_card(q, 'speaker{}'.format(idx), ui.form_card(box=ui.box('grid', width='430px'), items=[
                ui.persona(title=row.speaker, subtitle=row.title, caption=row.company, image=row.image, size='s'),
                ui.stats(inset=True, items=[
                    ui.stat(label='Average Sentiment', value='{}'.format(round(row.sentiment, 2)), 
                            icon=sentiment_icon(round(row.sentiment, 2)), icon_color=sentiment_color(round(row.sentiment, 2))),
                    ui.stat(label='Words Spoken', value='{:,}'.format(round(row.word_count))),
                ]),
                ui.inline(justify='end', items=[
                ui.mini_buttons([
                    ui.mini_button(name='#dashboard/{}'.format(idx), label='View', icon='BIDashboard'),
                ])])
                ]
            )
            )

        await plot_sentiment_time(q)
    
    except Exception as e:
        logger.error(e)
        logger.info('Loading Home Page Failed!')


async def plot_sentiment_time(q, speaker=None):

    try:

        q.page['meta'].side_panel = None
        await q.page.save()

        plot_data = q.client.series_data[['chunk', 'sentiment', 'defensiveness']].copy(deep=True)
        
        marks = [ui.mark(type='line', x='=segment', y='=sentiment', color='$red',
                        x_title='Time into Conversation', y_title='Rating',
                        y_min=1, y_max=5, curve='step'),
                ui.mark(type='point',  x='=segment', y='=sentiment', 
                        color='$red', fill_color='$red'
                        ),
                ]
        
        if speaker is not None:
            speaker_marks = []
            speaker_data = q.client.series_data[q.client.series_data.speaker.str.split(" -- ").str[0] == speaker].copy(deep=True)
            for _, row in speaker_data.iterrows():
                speaker_marks = speaker_marks + [ui.mark(x=row.chunk, y=row.sentiment, label=speaker, fill_color='$orange')]
            
            marks = marks + speaker_marks

        add_card(q, 'sentiment_time', ui.plot_card(
                box='horizontal',
                title='Overall Sentiment',
                data=data('segment sentiment defensiveness', 5, rows=[tuple(i) for i in plot_data.values]),
                events=['select_marks'],
                plot=ui.plot(marks)
            )
            )
    except Exception as e:
        logger.error(e)
        logger.info('Plotting Sentiment Over Time Failed!')    

@on('sentiment_time.select_marks')
async def on_marks_selected(q: Q):
    q.page['meta'].side_panel = None
    await q.page.save()

    mark = q.events.sentiment_time.select_marks[0]
    if isinstance(mark, list):
        segment = str(mark[0].get('segment'))
    else:
        segment = str(mark.get('segment'))

    segment = q.client.chunks.get(segment)
    speaker = segment.get('speaker').split(" -- ")[0]
    speaker_stats = q.client.speakers[q.client.speakers.speaker == speaker].iloc[0]
    sentiment = round(segment.get('sentiment').get('Rating'), 2)
    defense = round(segment.get('defensiveness').get('Rating'), 2)
    q.page['meta'].side_panel = ui.side_panel(title=segment.get('speaker'), closable=True, items=[
            ui.persona(title=speaker_stats.speaker, 
                    subtitle=speaker_stats.title, 
                    caption=speaker_stats.company, 
                    image=speaker_stats.image, size='s'),
            ui.stats([
                ui.stat(label='Overall Sentiment', icon=sentiment_icon(sentiment), icon_color=sentiment_color(sentiment),
                        value=sentiment_text(sentiment), 
                        caption=segment.get('sentiment').get('Reason for Rating')),
            ]),
                    ui.stats([
                        ui.stat(label='Defensiveness', icon=defense_icon(defense), icon_color=defense_color(defense),
                                value=defense_text(defense), 
                                caption=segment.get('defensiveness').get('Reason for Rating')),
                    ]),
                    ui.text_l("Original Transcript: "),
                    ui.template(content=segment.get('xml_text'), data=None)
                ])

    await q.page.save()



@on('#dashboard/{idx}')
async def speaker_dashboard(q, idx):
    company_speakers = q.client.speakers[q.client.speakers.company == q.client.company]
    speaker = company_speakers.iloc[int(idx)].speaker
    
    await plot_sentiment_time(q, speaker=speaker)


@on()
async def overview(q: Q):

    logger.info('Loading Trend Overview!')
    logger.catch

    clear_cards(q, ignore=['header', 'nav', 'footer'])
    q.client.nav_value = "overview"
    q.page['meta'].side_panel = None
    await q.page.save()

    await get_nav(q)
    await q.page.save()
    await create_reviews_view(q)

    
async def create_reviews_view(q):
    try:

        q.page['meta'].side_panel = None
        await q.page.save()

        add_card(q, 'quarter_name', ui.form_card(
            box=ui.box('body_header'),
            items=[ui.inline(justify='center', items=[
                ui.text_xl('Earnings Transcripts Over Time')])
                ]
        ))

        add_card(q, 'plot', ui.frame_card(box=ui.box('vertical', height='300px'), 
                                        title='Sentiment Over Time', content=q.client.sentiment_stars))
            
        add_card(q, 'form', ui.form_card(box='vertical', items=[
            ui.table(
                name='table', height='500px',
                columns=[ui.table_column(name="Quarter", label="Quarter", sortable=True),
                        ui.table_column(name="Rating", label="Rating", sortable=True),
                        ui.table_column(name="Reason for Rating", label="Reason for Rating", cell_overflow='wrap', min_width='900')
                        ], 
                rows=[ui.table_row(name='row{}'.format(idx), cells=list(row)) for idx, row in q.client.ratings_table[::-1].iterrows()]
            ),
            ]))

        corr_table = q.client.ratings_table.merge(q.client.close_price, on=['Quarter'], how='inner')

            
        num_stats = get_num_stats(corr_table, "Close", "Rating")
        add_card(q, 'plot2', ui.wide_plot_card(
            box='vertical',
            title='Correlations',
            caption='''
            The graph to the right shows the correlation between the sentiment of the earnings calls transcripts and the average close price of the quarter. 
            We can see that quarters with worse call sentiment correspond to quarters with a lower close price.
            ''',
            data=data(
                fields=['Rating', 'low', 'q1', 'q2', 'q3', 'high'],
                rows=[list(row) for idx, row in num_stats.iterrows()],
                pack=True,
            ),
            plot=ui.plot([ui.mark(
                type='schema',
                x='=Rating',
                y1='=low',  # min
                y_q1='=q1',  # lower quartile
                y_q2='=q2',  # median
                y_q3='=q3',  # upper quartile
                y2='=high',  # max
                #color_range='$red $yellow $green',
                fill_color='#ccf5ff',
                x_title='Sentiment Rating', y_title='Stock Price',
            )])
        ))
            
        await q.page.save()
    except Exception as e:
        logger.error(e)
        logger.info('Creating Reviews Failed!')

@on()
async def about(q: Q):

    try:
        q.page['meta'].side_panel = None
        await q.page.save()
        clear_cards(q, ignore=['nav'])

        q.client.nav_value = "about"
        await get_nav(q)

        sleep = 3

        add_card(q, 'example', ui.form_card(
                box='vertical',
                items=[
                    ui.text_l('Earnings Transcript Sentiment'), 
                    create_stepper(),
                ])

            )
    except Exception as e:
        logger.error(e)
        logger.info('Loading About Failed!')

    await q.page.save()

    await q.sleep(1)
    add_card(q, 'example', ui.form_card(
            box='vertical',
            items=[
                ui.text_l('Earnings Transcript Sentiment'), 
                create_stepper(),
                ui.inline(justify='center', items=[ui.text_l("Scraping Earnings Sentiment")]),
                ui.inline(justify='center', items=[ui.image(title='Image title', path=q.app.step1_loader, width='900px', visible=True)]),
            ])

        )
    await q.page.save()

    await q.sleep(sleep)
    add_card(q, 'example', ui.form_card(
            box='vertical',
            items=[
                ui.text_l('Earnings Transcript Sentiment'), 
                create_stepper(step=1),
                ui.inline(justify='center', items=[ui.text_l("Ingesting Transcripts")]),
                ui.inline(justify='center', items=[ui.image(title='Image title', path=q.app.step2_loader, width='900px', visible=True)]),
            ])

        )
    await q.page.save()

    await q.sleep(5)
    add_card(q, 'example', ui.form_card(
            box='vertical',
            items=[
                ui.text_l('Earnings Transcript Sentiment'), 
                create_stepper(step=2),
                ui.inline(justify='center', items=[ui.text_l("Chatting with Transcripts")]),
                ui.inline(justify='center', items=[ui.image(title='Image title', path=q.app.step3_loader, width='900px', visible=True)]),
            ])

        )
    await q.page.save()

    await q.sleep(8)
    add_card(q, 'example', ui.form_card(
            box='vertical',
            items=[
                ui.text_l('Earnings Transcript Sentiment'), 
                create_stepper(step=2),
                ui.inline(justify='center', items=[ui.text_l("Generating Insights")]),
                ui.inline(justify='center', items=[ui.image(title='Image title', path=q.app.step4_loader, width='900px', visible=True)]),
            ])

        )
    await q.page.save()

def create_stepper(step=0):

    stepper = ui.stepper(name='stepper', items=[
            ui.step(label='Scrape Earnings Transcripts', icon='InternetSharing', done=(step>=1)),
            ui.step(label='Ingest Transcripts', icon='Upload', done=(step>=1)),
            ui.step(label='Chat with Transcripts', icon='ChatBot', done=(step>=2)),
            ui.step(label='Generate Insights', icon='Insights', done=(step>=3)),
            ])
    
    return stepper

# Use for cards that should be deleted on calling `clear_cards`. Useful for routing and page updates.
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card


def clear_cards(q, ignore=[]) -> None:
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)
    

async def get_nav(q):
    try:
        add_card(q, 'nav', ui.nav_card(
            box='sidebar', color='card', value=q.client.nav_value,
            items=[
                ui.nav_group('Menu', items=[
                    ui.nav_item(name='home', label='Detailed View'),
                    ui.nav_item(name='overview', label='Trends Over Time'),
                ]),
                ui.nav_group('Help', items=[
                    ui.nav_item(name='about', label='About'),
                ])
            ])
            )
    except Exception as e:
        logger.error(e)