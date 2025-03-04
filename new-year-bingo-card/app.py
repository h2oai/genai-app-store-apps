import asyncio
import os
import re

from h2o_wave import Q, app, data, main, on, run_on, ui
from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage
from loguru import logger


@app("/")
async def serve(q: Q):
    try:
        """Route the end user based on how they interacted with the app."""
        logger.info(q.args)

        if (
            not q.client.initialized
        ):  # Setup the application for a new browser tab, if not done yet
            initialize_browser(q)

        await run_on(q)  # Route user to the appropriate "on" function
        await q.page.save()  # Update the UI
    except Exception as ex:
        logger.error(ex)
        q.page["meta"].dialog = ui.dialog(
            title="",
            blocking=True,
            closable=False,
            items=[
                ui.text_xl("<center>Something went wrong!</center>"),
                ui.text(
                    "<center>Please come back soon to create your Bingo Goals card.</center>"
                ),
            ],
        )


def initialize_browser(q):
    q.client.edit_mode = False

    style = """

    [data-test="header_mobile"] {
        background: url('https://0xdata-public.s3.amazonaws.com/Michelle/happyHolidays-2023-banner-no-logo-fade.png') !important;
        background-size: contain !important;
        background-repeat: repeat !important;
        background-position: center !important;
    }

    [data-test="header_desktop"] {
        background: url('https://0xdata-public.s3.amazonaws.com/Michelle/holiday-bingo-logo-linear.png'), url('https://0xdata-public.s3.amazonaws.com/Michelle/happyHolidays-2023-banner-no-logo-fade.png') !important;
        background-size: 50%, contain !important;
        background-repeat: no-repeat, repeat !important;
        background-position: center !important;
    }

    .ms-Button--primary {
        color: #000000 !important;
    }

    .ms-Button--icon {
        color: #000000 !important;
        background-color: #FFE600 !important
    }

    .ms-Button--icon.is-disabled {
        color: #595959 !important;
        background-color: #C8C8C8 !important
    }

    img {
        cursor: default;
    }

    [data-test="footer"] a {
        color: #0000EE !important;
    }
    """

    dialog = bingo_game_inputs(q, True)

    q.page["meta"] = ui.meta_card(
        box="",
        dialog=dialog,
        title="Bingo Goals | H2O.ai",
        layouts=[
            ui.layout(
                breakpoint="xs",
                height="100vh",
                zones=[
                    ui.zone("header_mobile"),
                    ui.zone("mobile", size="1"),
                    ui.zone("footer"),
                ],
            ),
            ui.layout(
                max_width="1000px",
                breakpoint="m",
                height="100vh",
                zones=[
                    ui.zone("header_desktop"),
                    ui.zone("desktop", size="1"),
                    ui.zone("footer"),
                ],
            ),
        ],
        themes=[
            ui.theme(
                name="custom",
                primary="#FFE600",
                text="#000000",
                card="#FFFFFF",
                page="#E2E2E2",
            )
        ],
        theme="custom",
        stylesheet=ui.inline_stylesheet(style),
        script=ui.inline_script(heap_analytics(userid=q.auth.subject)),
        icon="https://h2o.ai/company/brand-kit/_jcr_content/root/container/section/par/advancedcolumncontro/columns1/advancedcolumncontro/columns0/image.coreimg.svg/1697220254347/h2o-logo.svg",
    )

    q.page["header_mobile"] = ui.header_card(
        box="header_mobile",
        title="BINGO GOALS",
        subtitle="",
        image="https://h2o.ai/company/brand-kit/_jcr_content/root/container/section/par/advancedcolumncontro/columns1/advancedcolumncontro/columns0/image.coreimg.svg/1697220254347/h2o-logo.svg",
        items=[
            ui.button(
                name="source_code",
                disabled=True,
                icon="Code",
                path="https://github.com/h2oai/genai-app-store-apps/tree/main/new-year-bingo-card",
                tooltip="View source code",
            ),
            ui.button(
                name="edit_mode",
                disabled=True,
                icon="Edit",
                value=str(q.client.edit_mode),
                tooltip="Edit content",
            ),
            ui.button(
                name="regenerate", disabled=True, icon="Reset", tooltip="Try again"
            ),
        ],
    )
    q.page["header_desktop"] = ui.header_card(
        box="header_desktop",
        title="",
        subtitle="",
        image="https://h2o.ai/company/brand-kit/_jcr_content/root/container/section/par/advancedcolumncontro/columns1/advancedcolumncontro/columns0/image.coreimg.svg/1697220254347/h2o-logo.svg",
        items=[
            ui.button(
                name="source_code",
                disabled=True,
                icon="Code",
                path="https://github.com/h2oai/genai-app-store-apps/tree/main/new-year-bingo-card",
                tooltip="View source code",
            ),
            ui.button(
                name="edit_mode",
                disabled=True,
                icon="Edit",
                value=str(q.client.edit_mode),
                tooltip="Edit content",
            ),
            ui.button(
                name="regenerate", disabled=True, icon="Reset", tooltip="Try again"
            ),
        ],
    )
    q.page["footer"] = ui.footer_card(
        box="footer",
        caption="Made with [Wave](https://wave.h2o.ai), [h2oGPTe](https://h2o.ai/platform/enterprise-h2ogpte), and 💛 by the Makers at H2O.ai.<br />Find more in the [H2O GenAI App Store](https://genai.h2o.ai).",
    )

    q.client.initialized = True


@on()
async def generate_bingo_card(q: Q):
    """Send a user's message to a Large Language Model and stream the response."""
    logger.info("")

    q.page["meta"].dialog = None
    q.client.name = q.args.name
    q.client.goals = q.args.goals

    for i in range(1, 26):
        q.client[f"bingo_{i}"] = ""

    q.page["header_mobile"].source_code.disabled = True
    q.page["header_mobile"].edit_mode.disabled = True
    q.page["header_mobile"].regenerate.disabled = True
    q.page["header_desktop"].source_code.disabled = True
    q.page["header_desktop"].edit_mode.disabled = True
    q.page["header_desktop"].regenerate.disabled = True

    q.client.chatbot_interaction = ChatBotInteraction(user_message=q.args.goals)

    q.page["mobile_bingo_card"] = ui.form_card(box=ui.box("mobile", size="0"), items=[])
    q.page["desktop_bingo_card"] = ui.form_card(
        box=ui.box("desktop", size="0"), items=[]
    )

    if q.args.name is None or q.args.name == "":
        q.client.bingo_card_title = "Your Bingo Goals card!"
    else:
        q.client.bingo_card_title = f"{q.args.name}'s Bingo Goals card!"

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))
    await q.run(chat, q.client.chatbot_interaction, q.auth.refresh_token)
    await update_ui


@on()
async def edit_mode(q):
    if q.client.edit_mode:
        q.client.edit_mode = False
        q.page["header_mobile"].edit_mode.icon = "Edit"
        q.page["header_desktop"].edit_mode.icon = "Edit"

    elif not q.client.edit_mode:
        q.client.edit_mode = True
        q.page["header_mobile"].edit_mode.icon = "Save"
        q.page["header_desktop"].edit_mode.icon = "Save"

    make_bingo_card_ui(q)


@on()
async def regenerate(q):
    q.page["meta"].dialog = bingo_game_inputs(q, False)


async def stream_updates_to_ui(q: Q):
    """Update the app's UI every 1/10th of a second with values from our chatbot interaction"""

    while q.client.chatbot_interaction.responding:
        make_bingo_card_ui(q)
        await q.page.save()
        await q.sleep(0.1)

    make_bingo_card_ui(q)

    q.page["header_mobile"].source_code.disabled = False
    q.page["header_mobile"].edit_mode.disabled = False
    q.page["header_mobile"].regenerate.disabled = False
    q.page["header_desktop"].source_code.disabled = False
    q.page["header_desktop"].edit_mode.disabled = False
    q.page["header_desktop"].regenerate.disabled = False


def chat(chatbot_interaction, token):
    """Send the user's message to the LLM and save the response"""

    def stream_response(message):
        """
        This function is called by the blocking H2OGPTE function periodically

        :param message: response from the LLM, this is either a partial or completed response
        """
        chatbot_interaction.update_response(message)

    if (
        chatbot_interaction.user_message is None
        or chatbot_interaction.user_message == ""
    ):
        message = "The user has no specific goals."
    else:
        message = f'Here is the user\'s goals in free text: """\n{chatbot_interaction.user_message}\n"""'

    client = connect_to_h2ogpte(refresh_token=token)
    with client.connect(client.create_chat_session()) as session:
        session.query(
            system_prompt=(
                "You are a friendly bot that turns a user's message containing goals for the New Year into a numbered "
                "list "
                "of 25 fun, short tasks to accomplish throughout the year that will help them with their goals. "
                "Your content will be turned into a 2024 Bingo Card. "
                "Each line item should be in the format 'n. emoji text' with n being a number and the 13th item "
                "should be a free space for having a birthday. Each item should be no more than 10 words. "
                "If the input from the user is not very helpful you must make up generic goals on their behalf."
            ),
            message=message,
            timeout=60,
            callback=stream_response,
            llm="meta-llama/Meta-Llama-3.1-8B-Instruct",
            llm_args={"do_sample": True, "temperature": 0.6},
        )


def bingo_game_inputs(q, blocking):
    return ui.dialog(
        title="Generate your Bingo Goals card!",
        blocking=blocking,
        closable=not blocking,
        items=[
            ui.textbox(name="name", label="Your name", value=q.client.name),
            ui.textbox(
                name="goals",
                label="Goals",
                multiline=True,
                value=q.client.goals,
                placeholder="Use free text to write as much or little about what you want to accomplish...",
            ),
            ui.buttons(
                items=[
                    ui.button(
                        name="generate_bingo_card",
                        label="Create my bingo card!",
                        primary=True,
                    ),
                ],
                justify="end",
            ),
        ],
    )


def make_bingo_card_ui(q: Q):
    for i in range(len(q.client.chatbot_interaction.content_to_show)):
        q.client[f"bingo_{i+1}"] = q.client.chatbot_interaction.content_to_show[i]

    if q.client.edit_mode:
        mobile_items = mobile_edit_mode_ui(q)
        desktop_items = edit_mode_ui(q)
    else:
        mobile_items = mobile_print_mode_ui(q)
        desktop_items = print_mode_ui(q)

    q.page["mobile_bingo_card"].items = mobile_items
    q.page["desktop_bingo_card"].items = desktop_items


def mobile_edit_mode_ui(q: Q):
    items = [ui.textbox(name="name", label="", value=q.client.bingo_card_title)]
    for i in range(1, 26):
        items.append(
            ui.textbox(
                name=f"bingo_{i}",
                value=q.client[f"bingo_{i}"],
                multiline=True,
                height="60px",
            )
        )
    return items


def edit_mode_ui(q: Q):
    items = [ui.textbox(name="name", label="", value=q.client.bingo_card_title)]
    for j in range(1, 6):
        line_items = []
        for i in range(1, 6):
            item_number = (j - 1) * 5 + i
            line_items.append(
                ui.textbox(
                    name=f"bingo_{item_number}",
                    value=q.client[f"bingo_{item_number}"],
                    multiline=True,
                    height="130px",
                    width="19%",
                )
            )
        items.append(ui.inline(items=line_items, justify="center"))
    return items


def mobile_print_mode_ui(q: Q):
    items = [
        ui.text(
            name="name",
            content="<center>" + q.client.bingo_card_title + "</center>",
            size="m",
        )
    ]
    for j in range(1, 6):
        line_items = []
        for i in range(1, 6):
            item_number = (j - 1) * 5 + i
            line_items.append(
                ui.text(
                    name=f"bingo_{item_number}",
                    content="<center>"
                    + (q.client[f"bingo_{item_number}"] or "")
                    + "</center>",
                    width="19%",
                    size="s",
                )
            )
        items.append(
            ui.inline(
                items=line_items, justify="center", height="100px", align="center"
            )
        )

    return items


def print_mode_ui(q: Q):
    items = [
        ui.text(
            name="name",
            content="<center>" + q.client.bingo_card_title + "</center>",
            size="xl",
        )
    ]
    for j in range(1, 6):
        line_items = []
        for i in range(1, 6):
            item_number = (j - 1) * 5 + i
            line_items.append(
                ui.text(
                    name=f"bingo_{item_number}",
                    content="<center>"
                    + (q.client[f"bingo_{item_number}"] or "")
                    + "</center>",
                    width="19%",
                    size="l",
                )
            )
        items.append(
            ui.inline(
                items=line_items, justify="center", height="130px", align="center"
            )
        )

    return items


class ChatBotInteraction:
    def __init__(self, user_message) -> None:
        self.user_message = user_message
        self.responding = True

        self.llm_response = ""
        self.content_to_show = ["🟡"]

    def update_response(self, message):
        if isinstance(message, ChatMessage):
            content_to_show = message.content
            self.responding = False
        elif isinstance(message, PartialChatMessage):
            self.llm_response += message.content
            content_to_show = self.llm_response + " 🟡"

        # Split the string into individual lines
        lines = content_to_show.strip().split("\n")
        # Use regular expression to extract text after the number and period
        pattern = re.compile(r"\d+\.\s+(.*)")
        self.content_to_show = [
            pattern.match(line).group(1).strip()
            for line in lines
            if pattern.match(line)
        ]


def connect_to_h2ogpte(refresh_token):

    if refresh_token is None:
        client = H2OGPTE(
            address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN")
        )
    else:

        token_provider = h2o_authn.TokenProvider(
            refresh_token=refresh_token,
            token_endpoint_url=f"{os.getenv('H2O_WAVE_OIDC_PROVIDER_URL')}/protocol/openid-connect/token",
            client_id=os.getenv("H2O_WAVE_OIDC_CLIENT_ID"),
            client_secret=os.getenv("H2O_WAVE_OIDC_CLIENT_SECRET"),
        )
        client = H2OGPTE(
            address=os.getenv("H2OGPTE_URL"), token_provider=token_provider
        )
    return client


def heap_analytics(userid) -> ui.inline_script:
    if "HEAP_ID" not in os.environ:
        return
    heap_id = os.getenv("HEAP_ID")
    script = f"""
window.heap=window.heap||[],heap.load=function(e,t){{window.heap.appid=e,window.heap.config=t=t||{{}};var r=document.createElement("script");r.type="text/javascript",r.async=!0,r.src="https://cdn.heapanalytics.com/js/heap-"+e+".js";var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(r,a);for(var n=function(e){{return function(){{heap.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}},p=["addEventProperties","addUserProperties","clearEventProperties","identify","resetIdentity","removeEventProperty","setEventProperties","track","unsetEventProperty"],o=0;o<p.length;o++)heap[p[o]]=n(p[o])}};
heap.load("{heap_id}"); 
    """

    if (
        userid is not None
    ):  # is OIDC Enabled? we do not want to identify all non-logged in users as "none"
        script += f"heap.identify('{userid}');"

    return script
