from h2o_wave import Q, ui, data
import toml
import os
import glob
import hashlib
from .utils import get_body, get_questions, loading
from .constants import COMPANY, COMPANY_LOGO, APP_TITLE, THEME, BACKGROUND_IMAGE

text_heading = "<font size=4><b>{}</b></font>"
themes = [ui.theme(
                name='legal-theme',
        primary='#dbcc42',
        text='#ffffff',
        card='#000000',
        page='#1D1D1D',
            )]


async def layout(q: Q):
    q.app.toml = toml.load("app.toml")
    zones = [
        ui.zone(name="zone_0", direction="row", size="10%"),
        ui.zone(name="zone_1", direction="row", size="82%", zones=[
            ui.zone(name="zone_1_1", direction="column", size="30%"),
            ui.zone(name="zone_1_2", direction="column", size="70%"),
        ]),
        ui.zone(name="zone_2", direction="row", size="8%"),
    ]

    q.page["meta"] = ui.meta_card(
        box="",
        themes=themes,
        theme="legal-theme",
        script=heap_analytics(
            userid=q.auth.subject,
            event_properties=f"{{"
            f"version: '{q.app.toml['App']['Version']}', "
            f"product: '{q.app.toml['App']['Title']}'"
            f"}}",
            ),
        layouts=[ui.layout(breakpoint="m", width="1600px", zones=zones)],
    )

    q.page["header"] = get_header_card(q, [])
    q.page["card_2"] = ui.footer_card(
        box="zone_2",
        caption=f"© 2023 powered by {COMPANY}GPT",
    )

    await q.page.save()


def get_header_card(q, items):
    title = q.client.texts['title']
    subtitle = q.client.texts['subtitle']
    items = items + [ui.menu(
            icon='Globe',
            items=[
                ui.command(name='portuguese', label='Portuguese 🇧🇷'),
                ui.command(name='english', label='English 🇺🇸'),
            ])]
    return ui.header_card(
        box="zone_0",
        title=title,
        subtitle=subtitle,
        image=COMPANY_LOGO,
        items=items
    )

async def get_home_items(q, flag):
    if flag == "home":
        q.page["header"] = get_header_card(q, [])
        caption, category, image = get_body(q)
        q.page['sidebar'] = ui.form_card(
            box=ui.box('zone_1_1'),
            items=get_sidebar(q))

        q.page["card_1"] = ui.tall_info_card(
            box='zone_1_2',
            name='',
            title=category,
            caption=caption,
            category=f'powered by {COMPANY}GPT',
            label='',
            image=image,
            image_height='400px',
        )

    elif flag == "uploaded":
        items = await get_questions(q)
        q.page["header"] = get_header_card(q, [ui.button(name='reset', label='Voltar', primary=True, icon='ArrowDownRight')])
        q.page["sidebar"] = ui.form_card(
            box=ui.box('zone_1_1'),
            items=items)
        await display_chat_view(q)


async def display_chat_view(q: Q):
    rows = q.client.texts['first_rows']
    q.page["card_1"] = ui.chatbot_card(
        box=ui.box('zone_1_2', height='100%'),
        data=data(
            "content from_user",
            t="list",
            rows=rows,
        ),
        events=["stop"],
        name="chatbot_brlaw",
        )
    await q.page.save()

def get_sidebar(q):
    files = glob.glob("demo_files/*.pdf")
    filenames = [os.path.basename(file) for file in files]
    sidebar_text = q.client.texts['sidebar']
    items = [
        ui.text(text_heading.format(sidebar_text['heading'])),
        ui.dropdown(name='initial_petition_demo',
                    label=sidebar_text['sub_heading'],
                    choices=[ui.choice(name=filename, label=filename) for filename in filenames]),
        ui.button(name='submit_demo', label=sidebar_text['label'], primary=True, icon='Upload'),
        ui.separator(),
        ui.text(text_heading.format(sidebar_text['heading_2'])),
        ui.textbox(name='url', label=sidebar_text['label_2'], required=True),
        ui.button(name='submit_url', label=sidebar_text['button'], primary=True, icon='Upload'),
    ]
    return items


# -------------------------------

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