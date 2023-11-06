from h2o_wave import Q

from src.generation import get_response
from src.layout import (
    landing_page_view,
    waiting_dialog
)
from src.prompts import get_default_prompt, expand_prompt


async def add_prompt_to_chat(q: Q, prompt: str):
    q.page['chat'].data += [prompt, True]
    await q.page.save()


async def add_response_to_chat(q: Q, response: str):
    q.page['chat'].data += [response, False]
    await q.page.save()


async def answer_question(q: Q, prompt: str):
    await waiting_dialog(q)
    response = await q.run(get_response, q, prompt)
    return response


async def handler(q: Q):
    if q.args.chatbot:
        await add_prompt_to_chat(q, prompt=q.args.chatbot)
        response = await answer_question(q, prompt=q.args.chatbot)
        await add_response_to_chat(q, response=response)
    elif q.args.inspect_code:
        prompt = get_default_prompt(q)
        await add_prompt_to_chat(q, prompt=prompt)
        prompt = await expand_prompt(q, prompt=prompt)
        response = await answer_question(q, prompt=prompt)
        await add_response_to_chat(q, response=response)
    else:
        await landing_page_view(q)
