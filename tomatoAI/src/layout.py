from typing import List
import os
import numpy as np

from src.utils import heap_analytics
from src.cards import *


async def landing_page_view(q: Q):

    q.page['header'] = header_card(q)
    q.page['vegetables'] = plants_card(q)
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
        themes=[
            ui.theme(
                name='custom',
                primary=os.getenv("PRIMARY_COLOR", "#a32424"),
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
                ui.zone(name="body_left",
                        zones=[
                            ui.zone(name="top"),
                            ui.zone(name="middle"),
                            ui.zone(name="bottom")
                        ],
                        size="600px"),
                ui.zone("body_right", size="1"),
            ],
        ),
        ui.zone("footer", size="70px"),
    ]
    return zones


async def image_view(q):
    paths = os.listdir("./static/images/")
    path = np.random.choice(paths, size=1)
    path = f"./static/images/{path[0]}"
    image, = await q.site.upload([path])

    q.page['image'] = ui.form_card(
        box='bottom',
        items=[ui.image(title='', path=image, width="100%")]
    )
