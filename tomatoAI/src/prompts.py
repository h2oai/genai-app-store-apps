crop_rotation = ("Can you recommend three fast-growing crops before and after each plant?")
bed_planning = ("Assist in planning beds with companion planting for optimal nutrient supply. "
                "Please take into account my climate subzone.")
fertilizer = "Kindly advise me on the most suitable organic fertilizer for each of my plants."
pests = ("Could you identify the prevalent pests and diseases affecting my plants,"
         " and offer guidance on prevention and control measures"
         " without resorting to pesticides?")
biodiversity = "How might I enhance the biodiversity of my vegetable garden?"
open_seeds = "What are open-pollinated seeds and why are they beneficial?"
composting = "Tell me more about composting. How can I start with it easily and how does it work?."
climate = ("What strategies can I employ to mitigate the impact of climate change on my vegetable garden?")
gardening_ai = ("How can data science, machine learning, and large language models (LLMs) "
                "boost my vegetable garden's productivity?")
agriculture_ai = ("In what ways can professional farmers leverage data science, machine learning,"
                  " and large language models (LLMs) to optimize their agricultural practices?")


questions = {
    "crop_rotation": {"prompt": crop_rotation, "topic": "Succession Planting"},
    "bed_planning": {"prompt": bed_planning, "topic": "Bed Planning"},
    "fertilizer": {"prompt": fertilizer, "topic": "Fertilizer"},
    "pests": {"prompt": pests, "topic": "Pests & Diseases"},
    "biodiversity": {"prompt": biodiversity, "topic": "Biodiversity"},
    "open_seeds": {"prompt": open_seeds, "topic": "Open-pollinated Seeds"},
    "composting": {"prompt": composting, "topic": "Composting"},
    "climate": {"prompt": climate, "topic": "Climate change"},
    "gardening_ai": {"prompt": gardening_ai, "topic": "Gardening AI"},
    "agriculture_ai": {"prompt": agriculture_ai, "topic": "Agriculture AI"},
}