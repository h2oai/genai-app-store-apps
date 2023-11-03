import os

from h2o_wave import ui, Q

from src.cards import (
    header_card,
    footer_card,
    device_not_supported_card,
    chatbot_card
)
from src.utils import heap_analytics


async def waiting_dialog(q: Q):
    q.page["meta"].dialog = ui.dialog(
        title="",
        items=[ui.image(title="", path=q.app.loader_s, width="300px")],
        blocking=True,
        width="300px"
    )
    await q.page.save()
    q.page["meta"].dialog = None


async def landing_page_view(q: Q):
    q.page['header'] = header_card(q)
    q.page["footer"] = footer_card()
    q.page["device-not-supported"] = device_not_supported_card()
    q.page['chatbot'] = chatbot_card()


def landing_page_layout(q: Q):
    q.page['meta'] = ui.meta_card(
        box='',
        title=q.app.toml['App']['Title'],
        icon='Dictionary',
        theme="custom",
        script=heap_analytics(
            userid=q.auth.subject,
            event_properties=f"{{"
                             f"version: '{q.app.toml['App']['Version']}', "
                             f"product: '{q.app.toml['App']['Title']}'"
                             f"}}",
        ),
        themes=[
            ui.theme(
                name='custom',
                primary=os.getenv("PRIMARY_COLOR", "#585481"),
                text='#000000',
                card='#ffffff',
                page=os.getenv("SECONDARY_COLOR", "#C49BBB"),
            )
        ],
        layouts=[
            ui.layout(
                breakpoint="xs",
                height="100vh",
                zones=[
                    ui.zone(name='header'),
                    ui.zone(name='body', size="1", direction="column", zones=[
                        ui.zone(name="collections-mobile"),
                        ui.zone(name="chat")
                    ]),
                    ui.zone(name="footer")
                ],
            ),
            ui.layout(
                breakpoint='s',
                min_height='100vh',
                zones=[
                    ui.zone(name='header'),
                    ui.zone(name='body', size="1", direction="row", zones=[
                        ui.zone(name="collections", size="50%"),
                        ui.zone(name="chat", size="50%")
                    ]),
                    ui.zone(name="footer")
                ]
            )
        ]
    )
