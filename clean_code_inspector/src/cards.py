from h2o_wave import ui, Q, data

from src.utils import get_method_level_rules, get_class_level_rules


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


def user_code_card():
    return ui.form_card(
        box="bottom_left",
        items=[
            ui.textbox(
                name="user_code",
                label="Insert your code here!",
                width="100%",
                height="100%",
                multiline=True,
                value=f"def xyz(a, b, c): \n    result = a + b * c \n    return result"
            ),
            ui.button(name="inspect_code", label="Analyze Code")
        ]
    )


def checklist_card():
    return ui.form_card(
        box="top_left",
        items=[
            ui.separator(label="Code Quality Checklist"),
            ui.text(""),
            ui.inline(
                items=[
                    ui.checklist(
                        name="method_level_checks",
                        label="Method level",
                        choices=get_method_level_rules()
                    ),
                    ui.checklist(
                        name="class_level_checks",
                        label="Class level",
                        choices=get_class_level_rules()
                    )
                ]
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