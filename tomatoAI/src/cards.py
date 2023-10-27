import os
from h2o_wave import ui, Q
from src.prompts import questions


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


def response_card(content: str = ""):
    return ui.form_card(
        box='body_bottom',
        items=[
            ui.text('Response:'),
            ui.text(content, name='response')
        ]
    )


def questions_card():
    items = [ui.button(name=key, label=f"> {value}", link=True) for key, value in questions.items()]
    return ui.form_card(
        box="body_middle",
        items=items
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


def vegetable_selection_card(q: Q):
    choices = [
        ui.choice(name="Potato", label="Potato"),
        ui.choice(name="Tomato", label="Tomato"),
        ui.choice(name="Bell_pepper", label="Bell pepper"),
        ui.choice(name="Egg_plant", label="Egg plant"),
        ui.choice(name="Hot_pepper", label="Hot pepper"),
        ui.choice(name="Zucchini", label="Zucchini"),
        ui.choice(name="Cucumber", label="Cucumber"),
        ui.choice(name="Pumpkin", label="Pumpkin"),
        ui.choice(name="Watermelon", label="Watermelon"),
        ui.choice(name="Broccoli", label="Borccoli"),
        ui.choice(name="Cabbage", label="Cabbage"),
        ui.choice(name="Cauliflower", label="Cauliflower"),
        ui.choice(name="Kale", label="Kale"),
        ui.choice(name="Radish", label="Radish"),
        ui.choice(name="Peas", label="Peas"),
        ui.choice(name="Beans", label="Beans"),
        ui.choice(name="Lentils", label="Lentils"),
        ui.choice(name="Chickpeas", label="Chickpeas"),
        ui.choice(name="Soybeans", label="Soybeans"),
        ui.choice(name="Onions", label="Onions"),
        ui.choice(name="Garlic", label="Garlic"),
        ui.choice(name="Leek", label="Leek"),
        ui.choice(name="Shallot", label="Shallot"),
        ui.choice(name="Chives", label="Chives"),
        ui.choice(name="Lettuce", label="Lettuce"),
        ui.choice(name="Carrots", label="Carrots"),
        ui.choice(name="Beets", label="Beets"),
        ui.choice(name="Spinach", label="Spinach"),
        ui.choice(name="Marigold", label="Marigold"),
        ui.choice(name="Corn", label="Corn"),
    ]

    return ui.form_card(
        box="body_top",
        items=[
            ui.inline([
                ui.picker(
                    name="plants",
                    label="Your plants",
                    choices=choices,
                    trigger=True,
                    values=list(q.client.plants) if q.client.plants is not None else None,
                ),
                ui.dropdown(
                    name="climate_zone",
                    value="Temperate" if q.client.climate_zone is None else q.client.climate_zone,
                    trigger=True,
                    choices=[
                        ui.choice(name="Tropical", label="Tropical"),
                        ui.choice(name="Dry", label="Dry"),
                        ui.choice(name="Temperate", label="Temperate"),
                        ui.choice(name="Continental", label="Continental"),
                    ],
                    label="Climate Zone",
                    width="200px"),
            ]),
            ui.inline([
                ui.spinbox(
                    name="num_beds",
                    min=1,
                    max=6,
                    value=1 if q.client.num_beds is None else q.client.num_beds,
                    trigger=True,
                    label="Number of Beds",
                    width="150px"),
            ])

        ]
    )
