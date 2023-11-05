from h2o_wave import Q
from typing import Optional

from src.generation import get_response
from src.layout import (
    landing_page_view,
    waiting_dialog
)


async def answer_question(q: Q, prompt: Optional[str]):
    if prompt is None:
        placeholder = ("Could you share some tips on clean code principles to improve my "
                       "code?")
        q.page['chat'].data += [placeholder, True]
    else:
        q.page['chat'].data += [prompt, True]
    await q.page.save()
    await waiting_dialog(q)
    response = await q.run(get_response, q, prompt)
    q.page['chat'].data += [response, False]
    await q.page.save()


async def handler(q: Q):
    if q.args.chatbot:
        await answer_question(q, q.args.chatbot)
    elif q.args.inspect_code:
        await answer_question(q, prompt=None)
    else:
        await landing_page_view(q)
