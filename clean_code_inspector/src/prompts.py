from h2o_wave import Q

from src.utils import get_concatenated_str


def get_system_prompt() -> str:
    system_prompt = ("Assume the role of a Python clean code expert, offering clear guidance and easily digestible "
                     "explanations to novice Python developers. While you can provide general advice on clean code "
                     "principles, your detailed assistance is limited to the class or method level of Python code. If "
                     "presented with code of other programming languages, kindly communicate your expertise on "
                     "Python code.")
    return system_prompt


def get_default_prompt(q: Q) -> str:
    if q.client.user_code == "" or q.client.user_code is None:
        prompt = "Could you provide guidance on clean code principles in Python? "
    else:
        prompt = f"Would you be able to offer guidance on clean code principles for my Python code? "
    return prompt


async def expand_prompt(q: Q, prompt: str) -> str:
    expansion = (
        f"Validate if the provided code is Pytho code and ensure it is exclusive to Python. If not, ask "
        f"to provide Python-specific code instead. ")

    await get_level_rules(q)
    if q.client.method_checks or q.client.class_checks:
        expansion += f"Highlight the exact clean code principles that are not adhered "
        if q.client.method_checks:
            expansion += f"on the method-level: {q.client.method_checks} "
        if q.client.class_checks:
            expansion += f"on the class-level: {q.client.class_checks} "
        expansion += (f". Improve the code and display an improvement or the code only once using black box format "
                      f"with ```python backticks. ")
    else:
        expansion += "The user forgot to pick clean code principles. Remind them to do so. "
    prompt += expansion
    return prompt


def get_context(q: Q):
    if q.client.user_code is None:
        context = ["The developer has forgotten to provide the relevant code snippet. Please remind them to do so."]
    else:
        context = [
            f"The code to be analyzed is as follows: ```python{q.client.user_code}```"]
    return context


async def get_level_rules(q: Q):
    q.client.method_checks = None
    if q.client.method_level_checks is not None:
        q.client.method_checks = get_concatenated_str(q.client.method_level_checks)

    q.client.class_checks = None
    if q.client.class_level_checks is not None:
        q.client.class_checks = get_concatenated_str(q.client.class_level_checks)
