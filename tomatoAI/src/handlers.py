from h2o_wave import Q

from src.generation import get_response
from src.layout import (
    landing_page_view,
    image_view,
    waiting_dialog
)
from src.prompts import questions


async def answer_question(q: Q, prompt: str):
    q.page['chat'].data += [prompt, True]
    await q.page.save()
    await waiting_dialog(q)
    response = await get_response(q, prompt)
    q.page['chat'].data += [response, False]
    await q.page.save()


async def handler(q: Q):

    if q.args.chatbot:
        await q.run(answer_question, q, q.args.chatbot)
        await image_view(q)
    elif q.args["prompts"] is not None and q.args["prompts"] in list(questions.keys()):
        await q.run(answer_question, q, questions[q.args["prompts"]]["prompt"])
        await image_view(q)
    else:
        await landing_page_view(q)
