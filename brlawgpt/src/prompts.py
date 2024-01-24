prompts_pt = {
    'system_prompt': """Você é um assistente virtual chamado BrLawGPT.
Apenas responda as perguntas em Português e jamais use outro idioma.
Responda as pergunta com informações fornecidas no contexto, não crie nenhuma informação.
Se não tiver informações suficientes para responder à sua pergunta, informe em português sobre as informações que estão faltando para fornecer uma resposta completa.""",
    "pre_prompt_summary":"Usando apenas os trechos do documento abaixo, faça um resumo que melhor descreva o assunto da petição inicial e os pedidos do autor. Não adicione nenhum fato não descrito no texto. Use apenas português e não use nenhuma palavra em inglês.",
    "prompt_summary": "Descreva o assunto e os fatos descritos pelo autor da petição em um resumo em português.",
    'stf_tema_prompt': """Usando apenas os fatos de uma petição inicial descritos abaixo, responda a pergunta.\n\nFATOS DA PETIÇÃO:\n{0}.\n\nQuais são os temas do STF mais relacionados aos fatos da petição inicial? Escolha apenas os temas relacionados diretamente à petição inicial limitado em 3 temas e ignore o restante.""",
    'peticao_prompt': """Responda apenas usando os trechos acima da petição inicial.\n\nPERGUNTA:{0} \n\nRESPOSTA:"""
}

prompts_eng = {
    'system_prompt': """You are a virtual assistant called BrLawGPT.
Please answer in English.
Answer the question with information provided in the context, do not create any information.
If you do not have enough information to answer your question, inform in english about the information that is missing to provide a complete answer.""",
    "pre_prompt_summary":"Using only the document chunks below, make a summary that best describes the subject of the initial petition and the author's requests. Do not add any facts not described in the text.\n",
    "prompt_summary": "Describe the subject and the facts described by the petitioner in a summary in English.",
    'stf_tema_prompt': """Using only the facts of an initial petition described below, answer the question.\n\nPETITION FACTS:\n{0}.\n\nWhat are the most related STF themes to the facts of the initial petition? Choose only the themes directly related to the initial petition limited to 3 themes and ignore the rest.""",
    'peticao_prompt': """Answer only using the chunks above from the initial petition.\n\nQUESTION:{0} \n\nANSWER:"""
}


sum_check = ["dê-me um resumo", "resumo", "resuma", "resuma este documento", "resuma isto",
            "dê-me um breve resumo", "resuma este pdf", "resuma este arquivo","faça um resumo da petição inicial",
            "faça um resumo", "faça um resumo dos fatos descritos na petição inicial",
            'gimme a summary', 'give me a summary', 'summarize this', 'summarize this pdf', 'summarize this file',
            'summarize the facts described in the initial petition']

stf_temas_check = ["tema do stf", "temas do stf", "tese do stf", "teses do stf", "tese do supremo", "teses do supremo",
                    "supreme court theme", "supreme court themes", "supreme court thesis", "supreme court theses", "brazilian supreme court"]