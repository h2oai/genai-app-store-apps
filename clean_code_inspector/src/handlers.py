from h2o_wave import Q
from src.layout import landing_page_view


async def handler(q: Q):

    await landing_page_view(q)