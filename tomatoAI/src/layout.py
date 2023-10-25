from typing import List

from src.utils import heap_analytics
from src.cards import *


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
