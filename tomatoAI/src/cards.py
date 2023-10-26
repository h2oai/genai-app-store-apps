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

    choices = [ui.choice(name=key, label=value) for key, value in questions.items()]

    return ui.form_card(
        box="body_middle",
        items=[
            ui.dropdown(
                name="questions",
                label="",
                choices=choices,
                trigger=True,
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


def vegetable_selection_card(q: Q):
    solanum_choices = [
        ui.choice(name="Potato", label="Potato"),
        ui.choice(name="Tomato", label="Tomato"),
        ui.choice(name="Bell_pepper", label="Bell pepper"),
        ui.choice(name="Egg_plant", label="Egg plant"),
        ui.choice(name="Hot_pepper", label="Hot pepper")
    ]

    cucurbitaceae_choices = [
        ui.choice(name="Zucchini", label="Zucchini"),
        ui.choice(name="Cucumber", label="Cucumber"),
        ui.choice(name="Pumpkin", label="Pumpkin"),
        ui.choice(name="Watermelon", label="Watermelon"),
        ui.choice(name="Butternut", label="Butternut Squash")
    ]

    brassicaceae_choices = [
        ui.choice(name="Broccoli", label="Borccoli"),
        ui.choice(name="Cabbage", label="Cabbage"),
        ui.choice(name="Cauliflower", label="Cauliflower"),
        ui.choice(name="Kale", label="Kale"),
        ui.choice(name="Radish", label="Radish")
    ]

    fabaceae_choices = [
        ui.choice(name="Peas", label="Peas"),
        ui.choice(name="Beans", label="Beans"),
        ui.choice(name="Lentils", label="Lentils"),
        ui.choice(name="Chickpeas", label="Chickpeas"),
        ui.choice(name="Soybeans", label="Soybeans")
    ]

    alliaceae_choices = [
        ui.choice(name="Onions", label="Onions"),
        ui.choice(name="Garlic", label="Garlic"),
        ui.choice(name="Leek", label="Leek"),
        ui.choice(name="Shallot", label="Shallot"),
        ui.choice(name="Chives", label="Chives")
    ]

    return ui.form_card(
        box="body_top",
        items=[
            ui.inline([
                ui.checklist(
                    name="solanum",
                    label="Solanum",
                    choices=solanum_choices,
                    trigger=True,
                    values=q.client.solanum if q.client.solanum is not None else ["Tomato"]
                ),
                ui.checklist(
                    name="cucurbitaceae",
                    label="Curcubitaceae",
                    choices=cucurbitaceae_choices,
                    trigger=True,
                    values=q.client.cucurbitaceae if q.client.cucurbitaceae is not None else None
                ),
                ui.checklist(
                    name="brassicaceae",
                    label="Brassicaceae",
                    choices=brassicaceae_choices,
                    trigger=True,
                    values=q.client.brassicaceae if q.client.brassicaceae is not None else None
                ),
                ui.checklist(
                    name="fabaceae",
                    label="Fabaceae",
                    choices=fabaceae_choices,
                    trigger=True,
                    values=q.client.fabaceae if q.client.fabaceae is not None else None
                ),
                ui.checklist(
                    name="alliaceae",
                    label="Alliaceae",
                    choices=alliaceae_choices,
                    trigger=True,
                    values=q.client.alliaceae if q.client.alliaceae is not None else None
                ),
            ]),
            ui.inline(
                items=[
                    ui.spinbox(
                        name="num_beds",
                        min=1,
                        max=6,
                        value=1 if q.client.num_beds is None else q.client.num_beds,
                        trigger=True,
                        label="Number of beds",
                        width="150px"),
            ])

        ]
    )
