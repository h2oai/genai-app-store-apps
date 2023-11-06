from h2o_wave import ui, Q, data

from src.utils import (
    get_method_level_rules,
    get_class_level_rules,
    get_code_file,
    get_example_code_choices
)


def header_card(q: Q):
    return ui.header_card(
        box='header',
        title=q.app.toml['App']['Title'],
        subtitle=f"{q.app.toml['App']['Description']}",
        icon="Broom",
        items=[
            ui.persona(title='Guest User', initials_color="#000000", initials='G', size='xs'),
        ]
    )


def chat_card():
    return ui.chatbot_card(
        box="body_right",
        name="chatbot",
        placeholder="Ready to untangle Python code? Ask away - I'm on a clean code mission!",
        data=data('content from_user', t='list', rows=[]),
    )


def user_code_card(q):
    return ui.form_card(
        box="top_left",
        items=[
            ui.textbox(
                name="user_code",
                label="Insert your code here!",
                width="100%",
                height="200px",
                multiline=True,
                value=get_code_file(q.client.example_code) if q.client.example_code is not None else None,
            ),
            ui.inline(
                items=[
                    ui.dropdown(
                        name="example_code",
                        label="Or pick an example!",
                        trigger=True,
                        width="200px",
                        choices=get_example_code_choices(),
                        value=q.client.example_code
                    ),
                ]
            ),
        ]
    )


def checklist_card(q):
    return ui.form_card(
        box="bottom_left",
        items=[
            ui.separator(label="Code Quality Checklist"),
            ui.text(""),
            ui.inline(
                items=[
                    ui.checklist(
                        name="method_level_checks",
                        label="Method level",
                        choices=get_method_level_rules(),
                        values=q.client.method_level_checks
                    ),
                    ui.checklist(
                        name="class_level_checks",
                        label="Class level",
                        choices=get_class_level_rules(),
                        values=q.client.class_level_checks
                    )
                ]
            ),
            ui.button(
                name="inspect_code",
                label="Analyze Code",
            ),
        ]
    )


def response_card():
    return ui.form_card(
        box="body_right",
        items=[
            ui.text(content='')
        ]
    )


def footer_card():
    return ui.footer_card(
        box='footer',
        caption='Made with 💛 and [H2O Wave](https://wave.h2o.ai).'
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