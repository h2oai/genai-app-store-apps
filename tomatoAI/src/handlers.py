from h2o_wave import Q

from src.generation import get_response
from src.layout import landing_page_view


async def handler(q: Q):

    if q.args.questions:
        response = await get_response(q, choice=q.args.questions)
        await landing_page_view(q, response)
    else:
        await landing_page_view(q)
