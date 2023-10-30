from h2o_wave import ui, Q, data

from src.prompts import questions
from src.utils import get_climate_subzone, get_vegetable_choices


def header_card(q: Q):
    return ui.header_card(
        box='header',
        title=q.app.toml['App']['Title'],
        subtitle=f"{q.app.toml['App']['Description']}",
        icon="Flower",
        items=[
            ui.persona(title='Guest User', initials_color="#000000", initials='G', size='xs'),
        ]
    )


def chat_card():
    return ui.chatbot_card(
        box="body_right",
        name="chatbot",
        placeholder="Curious about plants or puzzled by pots? Ask your quirky gardening questions here!",
        data=data('content from_user', t='list', rows=[]),
    )


def questions_card():
    choices = [
        ui.choice(name=key, label=value["topic"]) for key, value in questions.items()
    ]
    return ui.form_card(
        box="middle",
        items=[
            ui.dropdown(
                name="prompts",
                choices=choices,
                placeholder="Assist me with...",
                trigger=True
            )
        ]
    )


def device_not_supported_card():
    return ui.form_card(
        box='device-not-supported',
        items=[
            ui.text_xl(
                'This app was built desktop; it is not available on mobile or tablets.'
            )
        ],
    )


def footer_card():
    return ui.footer_card(
        box='footer',
        caption='Made with 💛 and [H2O Wave](https://wave.h2o.ai).'
    )


def plants_card(q: Q):
    choices = get_vegetable_choices()

    return ui.form_card(
        box="top",
        items=[
            ui.inline([
                ui.dropdown(
                    name="climate_zone",
                    value=None if q.client.climate_zone is None else q.client.climate_zone,
                    trigger=True,
                    choices=[
                        ui.choice(name="Tropical", label="Tropical"),
                        ui.choice(name="Dry", label="Dry"),
                        ui.choice(name="Temperate", label="Temperate"),
                        ui.choice(name="Continental", label="Continental"),
                        ui.choice(name="Polar", label="Polar"),
                    ],
                    placeholder="Pick me!",
                    label="Climate Zone",
                    width="200px"),
                ui.dropdown(
                    name="climate_subzone",
                    label="Climate subzone",
                    choices=get_climate_subzone(q.client.climate_zone)
                        if q.client.climate_zone is not None
                        else None,
                    width="200px",
                    visible=True if q.client.climate_zone else False,
                    trigger=True,
                    placeholder="Pick me!",
                    value=q.client.climate_subzone if q.client.climate_subzone is not None else None,
                ),
            ]),
            ui.picker(
                name="plants",
                label="Your plants",
                choices=choices,
                trigger=True,
                values=list(q.client.plants) if q.client.plants is not None else None,
                tooltip="What about tomatoes? ;-)"
            ),
            ui.spinbox(
                name="num_beds",
                min=1,
                max=6,
                value=1 if q.client.num_beds is None else q.client.num_beds,
                trigger=True,
                label="Number of Beds",
                tooltip="Approx. 2m² in size",

                width="150px"),
        ]
    )

    def image_card():
        return ui.form_card(
            box='bottom',
            ui.image(title='', path='./static/images/VegetableGarden.jpg')
        )
