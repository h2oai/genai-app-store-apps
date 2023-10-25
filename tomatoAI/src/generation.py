from h2o_wave import Q, ui
from h2ogpt_client import Client
from loguru import logger

from src.prompts import questions


async def llm_query(llm_url: str,
                    h2ogpt_key: str,
                    user_message: str,
                    plants: str,
                    num_beds: int = 4,
                    width_bed: float = 1.2,
                    length_bed: float = 2) -> str:
    logger.info("")

    system_prompt = ("You are an expert of planting vegetables and fruits in a kitchen"
                     " or vegetable garden. You provide tips and assistance to unexperienced"
                     " gardeners with easy to understand explanations. Don't give more than 8 tips. ")

    try:
        logger.debug(user_message)
        client = Client(llm_url, h2ogpt_key=h2ogpt_key)
        llm = client.text_completion.create(
            visible_models=["h2oai/h2ogpt-4096-llama2-70b-chat"],
            system_prompt=system_prompt,
            text_context_list=[f"{num_beds} beds of {width_bed} m width and {length_bed} m length. "
                               f"The user wants to grow {plants}."]
        )
        response = llm.complete_sync(user_message)
        return response.strip()

    except Exception as e:
        logger.error(e)
        return ""


async def get_response(q: Q, choice: str):

    plants = []
    if q.client.solanum is not None:
        plants.extend(q.client.solanum)
    if q.client.cucurbitaceae is not None:
        plants.extend(q.client.cucurbitaceae)
    if q.client.brassicaceae is not None:
        plants.extend(q.client.brassicaceae)
    if q.client.fabaceae is not None:
        plants.extend(q.client.fabaceae)
    if q.client.alliaceae is not None:
        plants.extend(q.client.alliaceae)

    if len(plants) > 0:
        selection = plants[0]
        for n in range(1, len(plants)):
            selection += ", "
            selection += plants[n]
    else:
        selection="Tomato"

    prompt = questions[choice]

    response = await q.run(
        llm_query,
        q.app.llm_url,
        q.app.h2ogpt_key,
        prompt,
        selection,
        q.client.num_beds,
        q.client.bed_width,
        q.client.bed_length
    )
    return response
