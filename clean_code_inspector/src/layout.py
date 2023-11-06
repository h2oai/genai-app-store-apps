from h2o_wave import ui, Q
from typing import List
import os

from src.utils import heap_analytics
from src.cards import (
    header_card,
    footer_card,
    user_code_card,
    device_not_supported_card,
    checklist_card
)


async def waiting_dialog(q):
    q.page["meta"].dialog = ui.dialog(
        title="",
        items=[],#[ui.image(title="", path=q.app.load, width="150px")],
        blocking=True,
        width="200px"
    )
    await q.page.save()
    q.page["meta"].dialog = None


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
        themes=[
            ui.theme(
                name='custom',
                primary=os.getenv("PRIMARY_COLOR", "#33508a"),
                text='#000000',
                card='#ffffff',
                page=os.getenv("SECONDARY_COLOR", "#e2e2e2"),
            )
        ],
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
            direction=ui.ZoneDirection.ROW,
            zones=[
                ui.zone(
                    name="body_left",
                    zones=[
                        ui.zone(name="top_left", size="50%"),
                        ui.zone(name="bottom_left", size="50%")
                    ],
                    size="50%"
                ),
                ui.zone(
                    name="body_right",
                    size="50%"
                ),
            ],
        ),
        ui.zone("footer", size="70px"),
    ]
    return zones


async def landing_page_view(q: Q):

    q.page['header'] = header_card(q)
    q.page['footer'] = footer_card()
    q.page['user_code'] = user_code_card(q)
    q.page['checklist'] = checklist_card(q)
    q.page['device-not-supported'] = device_not_supported_card()