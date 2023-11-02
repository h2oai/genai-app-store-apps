from h2o_wave import on, ui, data, Q
from h2ogpt_client import Client
from src.wave_utils import clear_cards, long_process_dialog

from loguru import logger
import re
import os


text_heading = "<font size=4><b>{}</b></font>"

def initialize_generate_content_app(q):
    logger.info("")
    q.app.h2ogpt = {
        "address": os.getenv("H2OGPTE_URL"),
        "api_key": os.getenv("H2OGPTE_API_TOKEN"),
    }

    q.client.attributes = ['Hardwood Floors', 'Air Conditioning']
    q.client.sqft = '1600'
    q.client.bedrooms = '3'
    q.client.bathrooms = '2'
    q.client.persona = "Young Professionals"
    q.client.image = 'https://thumbor.forbes.com/thumbor/fit-in/900x510/https://www.forbes.com/home-improvement/wp-content/uploads/2022/07/download-23.jpg'

    q.client.system_prompt = f"You are a real estate agent making a listing." \
                             f"Do not explain yourself, just return the text of the listing."


def initialize_generate_content_client(q):
    logger.info("")


@on()
async def side_input_generate_content(q):
    logger.info("")
    clear_cards(q)

    # Options for listing
    bathroom_choices = range(1, 10)
    bedroom_choices = range(1, 10)
    attributes = ['Hardwood Floors', 'Air Conditioning', 'Basement', 'Pool', 'Hot Water Heating']
    personas = ['School Aged Family', 'Young Professionals', 'Empty Nesters']

    # User input form
    q.page['help'] = ui.form_card(
        box='left',
            items=[
                ui.text(text_heading.format("Get Started")),
                ui.text("Provide information about the home you are selling and then use the chatbot to generate the listing."),
                ui.inline(justify='around', 
                          items=[
                              ui.dropdown(
                                  name='bedrooms', 
                                  label='Number of Bedrooms', 
                                  width='250px',
                                  value=q.client.bedrooms,
                                  choices=[ui.choice(name=str(i), label=str(i)) for i in bathroom_choices ]
                                  ),

                              ui.dropdown(
                                  name='bathrooms', 
                                  label='Number of Bathrooms', 
                                  width='250px', 
                                  value=q.client.bathrooms,
                                  choices=[ui.choice(name=str(i), label=str(i)) for i in bedroom_choices]
                                  ),

                              ui.textbox(
                                  name='sqft', 
                                  label='Square Footage', 
                                  value=q.client.sqft)
                                  ]),
                                  
                ui.checklist(
                    name='attributes', 
                    label='Attributes', 
                    inline=True, 
                    values=q.client.attributes,
                    choices=[ui.choice(name=i, label=i) for i in attributes]
                    ),
                    
                    ui.inline(items=[
                        ui.dropdown(
                            name='persona', 
                            label='Audience Persona', 
                            value =q.client.persona,
                            choices=[ui.choice(name=str(i), label=str(i)) for i in personas]
                            ),   

                        ui.textbox(
                            name='image', 
                            label='Home Image', 
                            value=q.client.image, 
                            width='400px')
                            ]),

                ui.inline(justify='center', items=[
                    ui.button(
                        name='generate_prompt', 
                        label='Generate Prompt', 
                        primary=True)
                        ])
                ]
    )
    q.client.cards.append("help")


@on()
async def generate_prompt(q: Q):
    logger.info("")

    if q.args.attributes:
        q.client.attributes = q.args.attributes
    if q.args.sqft:
        q.client.sqft = q.args.sqft
    if q.args.bedrooms:
        q.client.bedrooms = q.args.bedrooms
    if q.args.bathrooms:
        q.client.bathrooms = q.args.bathrooms
    if q.args.persona:
        q.client.persona = q.args.persona
    if q.args.iamge:
        q.client.image = q.args.image

    await q.page.save()

    prompt = f'''
You are a real estate agent writing a listing for a home with the following attributes:

* Number of Bathrooms: {q.client.bathrooms}
* Number of Bedrooms: {q.client.bedrooms}
* SQFT: {q.client.sqft}
* Attributes: {q.client.attributes}

Write a real estate listing for the home geared towards {q.client.persona}.
'''

    q.page['prompt_card'] = ui.form_card(
        box='left',
        items=[
            ui.textbox(
                name='prompt', 
                label="Prompt",
                value=prompt, 
                multiline=True, 
                height='200px'
                ),
            ui.inline(
                justify='center', 
                items=[
                    ui.button(
                        name='generate_listing', 
                        label='Generate Listing', 
                        primary=True)
                    ]
                )]
    )

    q.client.cards.append("prompt_card")



@on()
async def generate_listing(q: Q):
    logger.info("")

    q.client.prompt = q.args.prompt
    await q.page.save()

    persona_pic = 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'
    q.page['listing_card'] = ui.wide_article_preview_card(
        box='right',
        persona=ui.persona(
            title='John Doe', 
            subtitle='Listing Agent',
            image=persona_pic),
        commands=[],
        aux_value='1m ago',
        image=q.client.image,
        title="Generated Listing",
        content="",
        items=[]
    )
    await q.page.save()
    q.client.cards.append("listing_card")

    q.client.waiting_dialog = "H2OGPT is creating your listing!"
    await long_process_dialog(q)


    q.page["listing_card"].content = await q.run(
        llm_query_custom, q.client.system_prompt, q.client.prompt, q.app.h2ogpt
    )
    await q.page.save()


async def llm_query_custom(system_prompt, prompt, connection_details):
    logger.info("")
    try:
        logger.debug(system_prompt)
        logger.debug(prompt)

        client = Client(connection_details["address"], h2ogpt_key=connection_details["api_key"])

        text_completion = client.text_completion.create(
            system_prompt=system_prompt,
            visible_models=['gpt-3.5-turbo-0613']
        )
        response = text_completion.complete_sync(prompt)

        logger.debug(response.strip())
        return response.strip()

    except Exception as e:
        logger.error(e)
        return ""