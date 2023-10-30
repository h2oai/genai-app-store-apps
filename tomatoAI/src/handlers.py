from h2o_wave import Q, copy_expando

from src.generation import get_response
from src.layout import landing_page_view, waiting_dialog
from src.prompts import questions


async def answer_question(q, prompt):
    await waiting_dialog(q)
    response = await get_response(q, prompt)
    await landing_page_view(q, response)


async def handler(q: Q):

    if q.args["bed_planning"]:
        await answer_question(q, questions["bed_planning"])
    elif q.args["crop_rotation"]:
        await answer_question(q, questions["crop_rotation"])
    elif q.args["fertilizer"]:
        await answer_question(q, questions["fertilizer"])
    elif q.args["pests"]:
        await answer_question(q, questions["pests"])
    elif q.args["biodiversity"]:
        await answer_question(q, questions["biodiversity"])
    elif q.args["composting"]:
        await answer_question(q, questions["composting"])
    elif q.args["agriculture_ai"]:
        await answer_question(q, questions["agriculture_ai"])
    elif q.args["climate"]:
        await answer_question(q, questions["climate"])
    elif q.args["gardening_ai"]:
        await answer_question(q, questions["gardening_ai"])
    else:
        await landing_page_view(q)
