from h2o_wave import main, app, Q, ui, run_on, copy_expando, on
import os
import toml
import asyncio
import h2o_authn

from loguru import logger

from src.wave_utils import heap_analytics

from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage



@app('/')
async def serve(q: Q):
    logger.info("Starting user request")
    copy_expando(q.args, q.client)  # Save any UI responses of the User to their session

    if not q.client.initialized:
        await initialize_session(q)

    elif not await run_on(q):
        await generate_prompt(q)
    await q.page.save()


async def initialize_session(q: Q):
    logger.info("Initializing the app for this browser session")
    if not q.app.initialized:
        await initialize_app(q)

    q.client.restrictions = []
    q.client.meals = ['Breakfast', 'Lunch', 'Snack', 'Dinner']
    q.client.cooking_instructions = True
    q.client.adults = '2'
    q.client.children = '2'

    landing_page_layout(q)
    prompt_generating_form(q)
    await generate_prompt(q)
    q.client.initialized = True


async def initialize_app(q: Q):
    logger.info("Initializing the app for all users and sessions - this runs the first time someone visits this app")
    q.app.toml = toml.load("app.toml")
    q.app.initialized = True


def landing_page_layout(q: Q):
    logger.info("")
    q.page['meta'] = ui.meta_card(
        box='',
        title=q.app.toml['App']['Title'],
        icon="https://h2o.ai/content/experience-fragments/h2o/us/en/site/header/master/_jcr_content/root/container/header_copy/logo.coreimg.svg/1696007565253/h2o-logo.svg",
        theme="lighting",
        script=heap_analytics(),
        stylesheet=ui.inline_stylesheet("""
            [data-test="footer"] a {color: #0000EE !important;}
             
            [data-test="source_code"] {background-color: #FFFFFF !important;}
            [data-test="app_store"] {background-color: #FFFFFF !important;}
            [data-test="support"] {background-color: #FFFFFF !important;}
            
        """),
        layouts=[
            ui.layout(
                breakpoint='xs',
                min_height='100vh',
                max_width="1600px",
                zones=[
                    ui.zone(name='header'),
                    ui.zone(name="mobile", size="1"),
                    ui.zone(name="footer")
                ]
            ),
            ui.layout(
                breakpoint='l',
                min_height='100vh',
                max_width="1600px",
                zones=[
                    ui.zone(name='header'),
                    ui.zone('body', size='1', direction=ui.ZoneDirection.ROW, zones=[
                        ui.zone('left', size='40%'),
                        ui.zone('right', size='60%'),
                    ]),
                    ui.zone(name="footer")
                ]
            )
        ]
    )
    q.page['header'] = ui.header_card(
        box='header',
        title=q.app.toml['App']['Title'],
        subtitle=q.app.toml["App"]["Description"],
        icon="Brunch",
        items=[
            ui.button(
                name="source_code",
                icon="Code",
                path="https://github.com/h2oai/genai-app-store-apps/tree/main/weekly-dinner-plan",
                tooltip="View the source code",
            ),
            ui.button(
                name="app_store",
                icon="Shop",
                path="https://genai.h2o.ai",
                tooltip="Visit the App Store",
            ),
            ui.button(
                name="support",
                icon="Help",
                path="https://support.h2o.ai/support/tickets/new",
                tooltip="Get help",
            ),
        ]
    )

    q.page["footer"] = ui.footer_card(
        box="footer",
        caption="Made with [Wave](https://wave.h2o.ai), [h2oGPTe](https://h2o.ai/platform/enterprise-h2ogpte), and "
                "💛 by the Makers at H2O.ai.<br />Find more in the [H2O GenAI App Store](https://genai.h2o.ai/).",
    )


def prompt_generating_form(q):
    logger.info("")

    # Options for meal plan
    adults = range(1, 10)
    children = range(1, 10)
    restrictions = ['Vegetarian', 'Vegan', 'Gluten Free', 'Halal', 'Kosher']
    meals = ['Breakfast', 'Lunch', 'Snack', 'Dinner']

    q.page['input_form'] = ui.form_card(
        box=ui.box('left', size="0"),
        items=[
            ui.text_l("<b>Get Started</b>"),
            ui.text("Provide information about your family's eating habits to generate a meal plan."),
            ui.inline(justify='around',
                      items=[
                          ui.dropdown(
                              name='adults',
                              label='Number of Adults',
                              width='32%',
                              value=q.client.adults,
                              trigger=True,
                              choices=[ui.choice(name=str(i), label=str(i)) for i in adults]
                          ),
                          ui.dropdown(
                              name='children',
                              label='Number of Children',
                              width='32%',
                              value=q.client.children,
                              trigger=True,
                              choices=[ui.choice(name=str(i), label=str(i)) for i in children]
                          ),
                          ui.toggle(
                              name='cooking_instructions',
                              label='Cooking Instructions',
                              trigger=True,
                              value=q.client.cooking_instructions)
                      ]),

            ui.checklist(
                name='restrictions',
                label='Restrictions',
                inline=True,
                trigger=True,
                values=q.client.restrictions,
                choices=[ui.choice(name=i, label=i) for i in restrictions]
            ),

            ui.checklist(
                name='meals',
                label='Meals',
                inline=True,
                trigger=True,
                values=q.client.meals,
                choices=[ui.choice(name=i, label=i) for i in meals]
            ),
        ]
    )

    q.page['input_form_mobile'] = ui.form_card(
        box=ui.box('mobile', order=1),
        items=[
            ui.text_l("<b>Get Started</b>"),
            ui.text("Provide information about your family's eating habits to generate a meal plan."),
              ui.dropdown(
                  name='adults',
                  label='Number of Adults',
                  value=q.client.adults,
                  trigger=True,
                  choices=[ui.choice(name=str(i), label=str(i)) for i in adults]
              ),
              ui.dropdown(
                  name='children',
                  label='Number of Children',
                  value=q.client.children,
                  trigger=True,
                  choices=[ui.choice(name=str(i), label=str(i)) for i in children]
              ),
            ui.toggle(
                name='cooking_instructions',
                label='Cooking Instructions',
                trigger=True,
                value=q.client.cooking_instructions
            ),

            ui.checklist(
                name='restrictions',
                label='Restrictions',
                inline=True,
                trigger=True,
                values=q.client.restrictions,
                choices=[ui.choice(name=i, label=i) for i in restrictions]
            ),

            ui.checklist(
                name='meals',
                label='Meals',
                inline=True,
                trigger=True,
                values=q.client.meals,
                choices=[ui.choice(name=i, label=i) for i in meals]
            ),
        ]
    )

    q.page["meal_plan"] = ui.form_card(box="right", items=[ui.text(name="meal_plan", content="")])
    q.page["meal_plan_mobile"] = ui.form_card(box=ui.box(zone="mobile", order=3), items=[ui.text(name="meal_plan", content="")])


@on()
async def generate_prompt(q: Q):
    logger.info("")
    cooking_instructions = ""
    if q.client.cooking_instructions:
        cooking_instructions = " Include cooking instructions for each meal."

    prompt = f'''You are an average working person writing a meal plan for the week with the following restrictions:

* Meals Each Day: {q.client.meals}
* Number of Adults: {q.client.adults}
* Number of Children: {q.client.children}
* Dietary Restrictions: {q.client.restrictions}

Write a one week meal plan geared towards this family.{cooking_instructions} Format your output by using markdown to bold each day of the week.
'''

    q.page['prompt_card'] = ui.form_card(
        box='left',
        items=[
            ui.text_l("<b>Customized Prompt</b>"),
            ui.textbox(name='prompt', label="", value=prompt, multiline=True, height='200px'),
            ui.inline(
                justify='center',
                items=[ui.button(name='generate_plan', label='Generate Meal Plan', primary=True)]
            )
        ]
    )
    q.page['prompt_card_mobile'] = ui.form_card(
        box=ui.box(zone="mobile", order=2),
        items=[
            ui.text_l("<b>Customized Prompt</b>"),
            ui.textbox(name='prompt', label="", value=prompt, multiline=True, height='200px'),
            ui.inline(
                justify='center',
                items=[ui.button(name='generate_plan', label='Generate Meal Plan', primary=True)]
            )
        ]
    )


@on()
async def generate_plan(q: Q):
    """
    Handle a user interacting with the chat bot component.

    :param q: The query object for H2O Wave that has important app information.
    """

    q.client.chatbot_interaction = ChatBotInteraction(user_message=q.client.prompt)

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))
    await q.run(chat, q.client.chatbot_interaction, q.auth.refresh_token)
    await update_ui


async def stream_updates_to_ui(q: Q):
    """
    Update the app's UI every 1/10th of a second with values from our chatbot interaction
    :param q: The query object stored by H2O Wave with information about the app and user behavior.
    """

    while q.client.chatbot_interaction.responding:
        q.page["meal_plan"].meal_plan.content = q.client.chatbot_interaction.content_to_show
        q.page["meal_plan_mobile"].meal_plan.content = q.client.chatbot_interaction.content_to_show
        await q.page.save()
        await q.sleep(0.1)

    q.page["meal_plan"].meal_plan.content = q.client.chatbot_interaction.content_to_show
    q.page["meal_plan_mobile"].meal_plan.content = q.client.chatbot_interaction.content_to_show
    await q.page.save()


def chat(chatbot_interaction, token):
    """
    Send the user's message to the LLM and save the response
    :param chatbot_interaction: Details about the interaction between the user and the LLM
    :param chat_session_id: Chat session for these messages
    """

    def stream_response(message):
        """
        This function is called by the blocking H2OGPTE function periodically for updating the UI
        :param message: response from the LLM, this is either a partial or completed response
        """
        chatbot_interaction.update_response(message)

    try:
        client = connect_to_h2ogpte(refresh_token=token)

        with client.connect(client.create_chat_session()) as session:
            session.query(
                system_prompt="You are an expert at quick and easy meal planning. Do not explain yourself, "
                              "just return the text of the meal plan.",
                message=chatbot_interaction.user_message,
                timeout=60,
                rag_config={"rag_type": "llm_only"},  # We are not looking at historic documents
                callback=stream_response,
            )


    except Exception as e:
        logger.error(e)
        return f""

def connect_to_h2ogpte(refresh_token):

    if refresh_token is None:
        client = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))
    else:

        token_provider = h2o_authn.TokenProvider(
            refresh_token=refresh_token,
            token_endpoint_url=f"{os.getenv('H2O_WAVE_OIDC_PROVIDER_URL')}/protocol/openid-connect/token",
            client_id=os.getenv("H2O_WAVE_OIDC_CLIENT_ID"),
            client_secret=os.getenv("H2O_WAVE_OIDC_CLIENT_SECRET"),
        )
        client = H2OGPTE(address=os.getenv("H2OGPTE_URL"), token_provider=token_provider)
    return client

class ChatBotInteraction:
    def __init__(self, user_message) -> None:
        self.user_message = user_message
        self.responding = True

        self.llm_response = ""
        self.content_to_show = "🔵"

    def update_response(self, message):
        if isinstance(message, ChatMessage):
            self.content_to_show = message.content
            self.responding = False
        elif isinstance(message, PartialChatMessage):
            if message.content != "#### LLM Only (no RAG):\n":
                self.llm_response += message.content
                self.content_to_show = self.llm_response + " 🔵"
