import os
import pandas as pd
from h2ogpte import H2OGPTE

client = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))

questions = []
for chat_session in client.list_recent_chat_sessions(0, 100000):
    if chat_session.collection_name is None:
        collection = "None"
    else:
        collection = chat_session.collection_name

    for message in client.list_chat_messages(chat_session.id, 0, 1000)[::-1]:

        if message.reply_to is None:
            question_id = message.id
            question = message.content
        elif message.reply_to == question_id:
            questions.append([collection, question, message.content])

df = pd.DataFrame(questions, columns=["Collection", "Question", "Answer"])
df.to_csv("questions.csv", index=False)




