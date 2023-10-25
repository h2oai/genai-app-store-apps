from typing import List

from src.utils import heap_analytics
from src.cards import *


async def waiting_dialog(q):
    q.page["meta"].dialog = ui.dialog(
        title="H2OGPT is creating the answer. Please wait.",
        items=[],
        blocking=True
    )
    await q.page.save()
    q.page["meta"].dialog = None


async def landing_page_view(q: Q, response=""):

    q.page['header'] = header_card(q)
    q.page['vegetables'] = vegetable_selection_card(q)
    q.page['response'] = response_card(content=response)
    q.page['user_questions'] = questions_card()
    q.page['footer'] = footer_card()
    q.page['device-not-supported'] = device_not_supported_card()


def layout(q: Q):
    q.page['meta'] = ui.meta_card(
        box='',
        title=q.app.toml['App']['Title'],
        script=heap_analytics(
            userid=q.auth.subject,
            event_properties=f"{{"
                             f"version: '{q.app.toml['App']['Version']}', "
                             f"product: '{q.app.toml['App']['Title']}'"
                             f"}}",
        ),
        theme="custom",
        layouts=[
            # xs: portrait phones, s: landscape phones, m: tablets, l: desktop, xl: large desktop
            ui.layout(
                breakpoint="xs",
                height="100vh",
                zones=[ui.zone("device-not-supported")],
            ),
            ui.layout(
                breakpoint="l",
                zones=get_zones(),
            ),
        ],
    )


def get_zones() -> List[ui.Zone]:
    zones = [
        ui.zone("header", direction=ui.ZoneDirection.ROW, size="100px"),
        ui.zone(
            "body",
            size="1",
            direction=ui.ZoneDirection.COLUMN,
            zones=[
                ui.zone("body_top", size="370px"),
                ui.zone("body_middle", size="100px"),
                ui.zone("body_bottom", size="1"),
            ],
        ),
        ui.zone("footer", size="70px"),
    ]
    return zones
