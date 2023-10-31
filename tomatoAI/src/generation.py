from h2o_wave import Q
from h2ogpt_client import Client
from loguru import logger


async def llm_query(llm_url: str,
                    h2ogpt_key: str,
                    user_message: str,
                    plants: str,
                    num_beds: int,
                    climate: str) -> str:
    logger.info("Prompting LLM with user query.")

    system_prompt = ("Specializing in cultivating vegetables and fruits within kitchen spaces or "
                     "small vegetable gardens, you provide guidance and easy-to-understand explanations "
                     "in a humorous manner, assisting inexperienced gardeners in their endeavors. "
                     "You prefer to create lists using bullet points rather than text blocks.")

    if climate is None:
        context = [
            f"The user is passionate about cultivating {plants} and currently tends to "
            f"{num_beds} beds, each with a size of 2 square meters. tThey are seeking advice on growing vegetables "
            f"that are well-suited to their specific climate conditions and small bed size. "
            f"Unfortunately they forgot to select a climate subzone. Remind them to do so! "
            f"They are open to exploring alternatives if the plants do not fit "
            f"are not optimal for preventing pests and diseases."
            f"They prefer concise answers with a subtle touch of humor. "
        ]
    else:
        context = [
            f"The user is passionate about cultivating {plants} and currently tends to "
            f"{num_beds} beds, each with a size of 2 square meters. Located in the {climate} "
            f"climate subzone, they are seeking advice on growing vegetables that are well-suited "
            f"to their specific climate conditions and small bed size. "
            f"Additionally, they are curious to know if the chosen plants thrive "
            f"in this particular climate subzone. They are open to exploring alternatives if the plants do not fit "
            f"the climate subzone or are not optimal for preventing pests and diseases. "
            f"They prefer concise answers with a subtle touch of humor. "
        ]

    try:
        logger.debug(user_message)
        client = Client(llm_url, h2ogpt_key=h2ogpt_key)
        llm = client.text_completion.create(
            visible_models=["gpt-3.5-turbo-0613"],
            system_prompt=system_prompt,
            text_context_list=context
        )
        response = llm.complete_sync(user_message)
        return response.strip()

    except Exception as e:
        logger.error(e)
        return ""


async def get_response(q: Q, prompt: str):

    plants = []
    if q.client.plants is not None:
        plants.extend(q.client.plants)

    if len(plants) > 0:
        selection = plants[0]
        for n in range(1, len(plants)):
            selection += ", "
            selection += plants[n]
    else:
        selection = ["tomatoes"]

    response = await q.run(
        llm_query,
        q.app.h2ogpt_url,
        q.app.h2ogpt_key,
        prompt,
        selection,
        q.client.num_beds,
        q.client.climate_subzone
    )
    return response
