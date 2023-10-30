from h2o_wave import Q, copy_expando

from src.generation import get_response
from src.layout import landing_page_view, waiting_dialog
from src.prompts import questions


async def answer_question(q, prompt):
    q.page['chat'].data += [prompt, True]
    await q.page.save()
    #await waiting_dialog(q)
    response = await get_response(q, prompt)
    q.page['chat'].data += [response, True]
    await q.page.save()


async def handler(q: Q):

    if q.args.chatbot:
        await answer_question(q, q.args.chatbot)
    elif q.args["prompts"]=="bed_planning":
        await answer_question(q, questions["bed_planning"]["prompt"])
    elif q.args["prompts"] == "crop_rotation":
        await answer_question(q, questions["crop_rotation"]["prompt"])
    elif q.args["prompts"]=="fertilizer":
        await answer_question(q, questions["fertilizer"]["prompt"])
    elif q.args["prompts"] == "pests":
        await answer_question(q, questions["pests"]["prompt"])
    elif q.args["prompts"] == "biodiversity":
        await answer_question(q, questions["biodiversity"]["prompt"])
    elif q.args["prompts"] == "composting":
        await answer_question(q, questions["composting"]["prompt"])
    elif q.args["prompts"] == "agriculture_ai":
        await answer_question(q, questions["agriculture_ai"]["prompt"])
    elif q.args["prompts"] == "climate":
        await answer_question(q, questions["climate"]["prompt"])
    elif q.args["prompts"] == "gardening_ai":
        await answer_question(q, questions["gardening_ai"]["prompt"])
    else:
        await landing_page_view(q)
