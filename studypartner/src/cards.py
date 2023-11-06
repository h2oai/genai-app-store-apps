import os

from h2o_wave import ui, Q, data


def header_card(q: Q):
    return ui.header_card(
        box='header',
        title=f"{q.app.toml['App']['Title']}",
        subtitle=q.app.toml["App"]["Description"],
        image=os.getenv(
            "LOGO",
            "https://h2o.ai/content/experience-fragments/h2o/us/en/site/header/master/_jcr_content/root/container/header_copy/logo.coreimg.svg/1696007565253/h2o-logo.svg"
        ),
    )


def footer_card():
    return ui.footer_card(
        box="footer",
        caption="Made with 💛 and H2O Wave."
    )


def device_not_supported_card():
    return ui.form_card(
        box="device-not-supported",
        items=[
            ui.text_xl(
                "This app was built desktop; it is not available on mobile or tablets."
            )
        ],
    )


def chatbot_card():
    return ui.chatbot_card(
        box="chat",
        data=data('content from_user', t='list'),
        name='chatbot',
        placeholder="What is your answer?"
    )
