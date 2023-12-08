import traceback
import random
from h2o_wave import Q, on, ui, handle_on, data
from src.utils import *
from src.utils import (get_recording_metadata_table,
                       llm_validate_message,
                        llm_transcript_analysis,
                        get_plot_audio_data)
from src.log import log
   

# Invoked when navigation item high level analysis was clicked
@on("#viewhighlevelanalysis")
async def render_high_level_analysis_page(q):   

    clean_cards(q, mode = "analysis")

    q.page['pie_chart'] = ui.wide_pie_stat_card(
                            box=ui.box('down', size ='60%'),
                            title='Top 5 topics in calls, emails & chats',
                            pies=[
                                ui.pie(label='Banking App', value='', fraction=0.30, color='$green', aux_value='30%'),
                                ui.pie(label='Loan Application', value='', fraction=0.23, color='$green', aux_value='23%'),
                                ui.pie(label='Currency Exchange fees', value='', fraction=0.16, color='$amber', aux_value='16%'),
                                ui.pie(label='Overdraft Fees', value='', fraction=0.14, color='$red', aux_value='14%'),
                                ui.pie(label='Fraud prevention', value='', fraction=0.12, color='$amber', aux_value='12%'),
                                ui.pie(label='Other', value='', fraction=0.05, color='$grey', aux_value='5%'),
                            ]
                        )
    
    q.page['info_card'] = ui.tall_info_card(
                                    box=ui.box('down', size ='40%'),
                                    name='#audio_call',
                                    title='',
                                    caption='''The app helps you to analyse text and audio files giving you
                                    \n a single view of what your customers are contacting you about from calls to emails.''',
                                    category='Powered by H2oGPT Enterprise',
                                    label='Analyse my text',
                                    image='https://codigosdebonus.com.br/wp-content/uploads/2020/05/participant-support-webinar-20-638.jpg',
                                )

    def generate_dollars(min=250, max=9000):
        d = max - min
        while True:
            yield f'${min + d * random.random():,.2f}'

    sample_dollars = generate_dollars()
    sample_color = ['$green', '$green', '$amber', '$red','$amber', '$grey']
    sample_topic = ['Banking App', 'Loan Application', 'Currency Exchange fee', 'Overdraft Fee', 'Fraud prevention', 'Other']
    sample_icon = ['CellPhone', 'ReminderPerson', 'AllCurrency', 'CompareUneven', 'ContactLock', 'CircleShapeSolid']
    sample_amount = ['12161', '9323', '6486', '5675', '4864', '2026']
    sample_rating = ['9','8','6','4','5','7']

    q.page['table_topics'] = ui.stat_table_card(
        box='up',
        title='What your customers talk the most about...',
        subtitle='Transcripted calls analysed by LLM',
        columns=["Top Topics", "Avg. Customer Value", "Volume of touchpoints", "Avg. Rating (0-low, 10-high)"],
        items=[
            ui.stat_table_item(label=sample_topic[i],
                               values=[next(sample_dollars), sample_amount[i], sample_rating[i]],
                               icon=sample_icon[i], icon_color=sample_color[i]) for i in range(6)
        ]
    )
    await q.page.save()


@on("#viewcalls")
async def render_viewcalls_page(q):
    '''
    Render the call analysis page
    :param q:
    :param refresh_ind:
    :return:
    '''
    if q.client.local_file_path:
            del q.client.local_file_path
    log.info("Starting render_viewcalls_page")
    await render_nav_bar(q, "#viewcalls")
    await q.page.save()
    log.info(f"q.args: {q.args}")

    local_data_folder = './data/agents/'
    local_metadata_file_path = './data/metadata/meta.json'


    if q.args['details'] is not False and q.args['details'] is not None: #action after selecting table and wanting calls details
        log.debug(f""" details number {q.args['details']} of the call to open which concerns the file :
                {local_data_folder+q.client.decomp[int(q.args['details'])]['file_name']}
                """)
        clean_cards(q, mode = "home", logger = log)
        await render_dive_call_details(q, local_metadata_file_path, q.client.decomp[int(q.args['details'])]['file_name'])

    else: #display of page after clicking nav bar OR after deleting file
        log.info("Generic page of call analysis")
        calls_table, calls_info = await get_recording_metadata_table(q,
                                                                    local_data_folder,
                                                                    local_metadata_file_path)

        clean_cards(q, mode = "home", logger = log)
        add_card(q, name = "content/calls_table")
        q.page['content/calls_table'] = ui.form_card(box='content',
                                        items=[ui.inline(justify='between',
                                                        items=[ui.text_l("Transcripted calls analysed with Enterprise H2oGPT"),
                                                                ]),
                                            calls_table])
        q.client.decomp = calls_info
        await q.page.save()
        log.debug(f"q.args: {q.args}")
        log.info("Complete render_viewcalls_page")

async def render_dive_call_details(q: Q, local_metadata_file_path, file_name):
    
    log.info("display details anbout the call")
    add_card(q, name = "content/call_details")
    add_card(q, name = "content/transcript")
    import json

    meta_data = json.load(open(local_metadata_file_path))

    call_info = meta_data[file_name]
    
    columns = [
        ui.table_column(name='text', label='Topic', min_width='400px'),
        ui.table_column(name='tag', label='Sentiment associated', cell_type=ui.tag_table_cell_type(name='tags', tags=[
            ui.tag(label='Negative', color='$red'),
            ui.tag(label='Neutral', color='#D2E3F8', label_color='#053975'),
            ui.tag(label='Positive', color='$mint'),
        ])),
    ]

    q.page["content/transcript"]= ui.article_card( box='content',
                                            title='Transcript of call',
                                            content=call_info.get("transcript", "empty")
                                        )
    
    emoji = "EmojiNeutral"
    if call_info.get("overall_sentiment", "Neutral") == "Positive":
        emoji = "Emoji2"
    elif call_info.get("overall_sentiment", "Neutral") == "Negative":
        emoji = "EmojiDisappointed"

    q.page["content/transcript"]= ui.wide_info_card(
                                                box='content', 
                                                name='transcript',
                                                title='Transcript of call',
                                                subtitle='powered by H2O.ai Model',
                                                caption=call_info.get("transcript", "empty"),
                                                label='Back',
                                                icon=emoji
                                            )
                                            
    q.page["content/call_details"] = ui.form_card(box='content', items=[
                                                                ui.table(
                                                                    name='issues',
                                                                    columns=columns,
                                                                    rows=[ui.table_row(name="same", cells=[topic, sentiment.capitalize()])
                                                                          for topic, sentiment in call_info.get("topics_associated_sentiment").items()],
                                                                ),
                                                                ui.text(call_info.get("issue_resolution_outcome", "No Next Steps")),
                                                                ui.markup(content=get_plot_audio_data("converted_audio.wav")), #TODO to implement
                                                            ])
    
    await q.page.save()

@on("#audio_call")
async def render_upload_analyse_calls_page(q):
    '''
    Render the upload_analyse_calls_page
    :param q:
    :return:
    '''

    log.info("Start render_upload_analyse_calls_page")
    ''' Set Navigation menu focus '''
    await render_nav_bar(q, "#audio_call")
    await q.page.save()
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card instead of recreating it every time
    clean_cards(q, exclude = ['content'], logger = log)
    
    if q.args.show_inputs:
        clean_cards(q)
        await long_process_dialog(q)
        log.info(f"q.client.transcript_multiline: {q.client.transcript_multiline}")

        async def clean_and_check_input(input_user):
            input_user = input_user[:2048]
            import re
            re.sub(' +', ' ', input_user)
            log.info(f"lenght of message: {len(input_user)}")
            if input_user.isalnum() or input_user==" " or len(input_user)<15:
                await render_error_page(q, "Please provide a valid input (no space or numbers only, 15+ characters) - if you need inspiration, check out our examples !")
                return ""
            return input_user

        cleaned_input = await clean_and_check_input(q.client.transcript_multiline)

        try:
            log.info("Create Sentiment Analysis and topic analysis from Transcript")
            overall_sentiment, topics_associated_sentiment, issue_resolution_outcome = await q.run(llm_transcript_analysis, q, cleaned_input)
        
        except Exception as err:
            log.error(f"Unhandled Application Error: {str(err)}")
            log.error(traceback.format_exc())
            await render_error_page(q, "H2oGPT may be down, please try again later. thanks !")
            overall_sentiment, topics_associated_sentiment, issue_resolution_outcome = "Non available", {"Non available": "Non available"}, "H2oGPT may be down, please try again. thanks !"
            return ""
        
        log.info(f"overall_sentiment: {overall_sentiment} --- topics_associated_sentiment: {topics_associated_sentiment}")       
        
        add_card(q, name = "content/call_details")
        add_card(q, name = "content/transcript")
        add_card(q, name = "content/back")
        
        q.page['content/back'].items = [
            ui.button(name='show_form', label='Back', primary=True),
        ]

        columns = [
            ui.table_column(name='text', label='Topic', min_width='400px'),
            ui.table_column(name='tag', label='Sentiment associated', cell_type=ui.tag_table_cell_type(name='tags', tags=[
                ui.tag(label='Negative', color='$red'),
                ui.tag(label='Neutral', color='#D2E3F8', label_color='#053975'),
                ui.tag(label='Positive', color='$mint'),
            ])),
        ]
        
        emoji = "EmojiNeutral"
        if overall_sentiment == "Positive":
            emoji = "Emoji2"
        elif overall_sentiment == "Negative":
            emoji = "EmojiDisappointed"

        q.page["content/transcript"]= ui.wide_info_card(
                                                    box='content',
                                                    name='input_message',
                                                    title='Input message',
                                                    subtitle='powered by H2oGPT',
                                                    caption=cleaned_input,
                                                    label='Back',
                                                    icon=emoji
                                                )
                                            
        q.page["content/call_details"] = ui.form_card(box='content', items=[
                                                                    ui.table(
                                                                        name='issues',
                                                                        columns=columns,
                                                                        rows=[ui.table_row(name="same", cells=[topic, sentiment.capitalize()])
                                                                            for topic, sentiment in topics_associated_sentiment.items()],
                                                                    ),
                                                                    ui.text(issue_resolution_outcome), ])
        await q.page.save()     
    elif q.args.transcript_multiline:
            q.page['content'].show_inputs.disabled = False
            q.client.transcript_multiline = q.args.transcript_multiline
            await q.page.save()
    else:
        clean_cards(q, logger = log)
        add_card(q, name = "content")
        def is_none(x):
            if x is None:
                return True
            return False
        
        q.page['content'] = ui.form_card(box='content', items=[
            ui.textbox(name='transcript_multiline', label='Write a possible (public) customer/agent exchange or customer comment/review',
                       multiline=True, spellcheck=True,
                       placeholder="""contents of calls, emails etc. you would like to analyse""",
                       trigger = True,
                       required=True),
            ui.button(name='show_inputs', label='Submit', primary=True, disabled = True )
        ])
        
        log.info(f"len(q.args.transcript_multiline)>10:{is_none(q.args.transcript_multiline)>10}")
        log.info(f"(q.args.transcript_multiline):{q.args.transcript_multiline}")
        await q.page.save()   

    log.info("Complete render_upload_analyse_calls_page")


async def long_process_dialog(q):

    q.app.dialog_gif, = await q.site.upload(['./static/load_.gif'])
    
    items = [
        ui.image(title="", path=q.app.dialog_gif, width="550px"),
    ]

    q.page["meta"].dialog = ui.dialog(
        title='Analysing with H2oGPT ...',
        items=items,
        blocking=True
    )
    await q.page.save()
    q.page["meta"].dialog = None


@on('#howtouse')
async def render_howtouse_page(q: Q):
    '''
    Render the DAI howtouse page - home page
    :param q:
    :return:
    '''
    log.info("Start render_howtouse_page")
    ''' Set Navigation menu focus '''
    await render_nav_bar(q, "#howtouse")
    await q.page.save()
    clean_cards(q, logger = log)

    add_card(q, name = "content") #content
    q.page['content'] = ui.preview_card( #content
            name='get_started',
            box=ui.box('content', size='350px'),
            image='https://img.freepik.com/free-photo/happy-female-entrepreneur-with-headset-drinking-coffee-while-surfing-net-touchpad-office_637285-1983.jpg',
            items=[
                ui.text_xl('''Welcome to the Call Center GPT app'''),
                ui.text_l(f'''To get started:
                                \n 1. Check H2o-pre-generated transcript with sentiment and topic analysis in "Example calls analysis"
                                \n 2. You can then analyse your own transcript or text by clicking 'Analyse my transcript' on the navigation bar 
                                \n 3. The "Global Analytical report" section gives you a report of all global customer service items (chats, emails, calls) - of course, it is made up for this public app!
                        '''),
                ui.button(name='#audio_call', label='Get Started'),
            ],
        )
    await q.page.save()
    log.info("Complete render_howtouse_page")

@on('#help/contact')
async def handle_contact(q: Q):
    """
    Render the help page
    """
    clean_cards(q, logger = log)
    add_card(q, name = "content")
    q.page['content'] = ui.form_card(
        box='content',
        items=[ui.message_bar(type='info', text='''
                              Please note this demonstration app is sending transcript data to our servers to interact with Enterprise H2oGPT.
                              '''), ]
    )
    await q.page.save()


async def render_page(q: Q):
    """
    Function that renders the correct page based on navigation and buttons
    """
    # if no navigation was clicked defaults to Getting Started view
    tab = q.args['#'] or 'howtouse'

    # setup default view
    log.info("Start function render_page")
    log.debug("Value of the tab in focus:... %s" % str(tab))
    await render_nav_bar(q, tab='#{}'.format(tab))
    if tab == "howtouse":
        await render_howtouse_page(q)

    log.info(f"q.args: {q.args}")
    log.info(f"tab: {tab}")
    await q.page.save()
    log.info("Complete function render_page")