prompt_topic = """
what are the {count} main topics in this collect
"""

prompt_question = """
Generate a new {modifier} question about {topic} for me from this collection and do not provide the answer
"""

prompt_feedback = """
Is this "{answer}" a good answer to the question: {question}
"""

prompt_best_answer = """
What would be a good short answer to the question: {question}?
"""

prompt_modifiers = [
    'multiple choice', 'easy', 'challenging', 'open ended', 'obscure', 'obvious'
]