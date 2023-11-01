texts_app_ptbr = {
    'title':'BrLawGPT - LLM aplicado ao direito',
    'subtitle': 'Criando e usando o Brazilian LawGPT - LLM dedicado em interpretar documentos jurídicos',
    'first_rows':[
                ["Bem-vindo! Sou o Brazilian LawGPT", False],
                ["Você pode fazer perguntas sobre o documento", False],
                ["Faça perguntas gerais adicionando --open flag no final", False], 
                [" - exemplo: qual é o modelo LLM? --open ", False],
                [" - Faça um resumo da petição inicial", False],
            ],
    'sidebar':{
        'label':'Upload Petição Inicial',
        'heading':'Faça o upload da Petição Inicial',
        'heading_2':'Faça upload com URL',
        'label_2':'Insira a URL do documento',
        'button':'Enviar'},
    'questions_data':{'Question': [
            'Qual o tema do STF que mais se assemelha ao resumo da petição?',
            'Faça um resumo dos fatos descritos na petição inicial',
            'Qual o assunto da petição inicial?',
        ]},
    'table_name':'Perguntas',
    'table_header':'Algumas possíveis questões que podem ser perguntadas',
    'table_subtitle':'Análise de Petição Inicial',
    'initial_petition':'Petição Inicial',
    'dialog':{
        'title':'Adaptando seu dataset...',
        'caption':'Por favor, aguarde...',
        'label':'Processando e indexando a petição inicial...'},
    'dialog_home':{
        'title':'Adaptando as coleções de documentos ja existentes...',
        'caption':'Por favor, aguarde...',
        'label':'Processando as coleções...'},
}

texts_app_en = {
    'title':'BrLawGPT - LLM applied to Legal Documents',
    'subtitle': 'Creating and using the Brazilian LawGPT - LLM dedicated to interpreting legal documents',
    'first_rows':[
                ["Welcome! I'm the Brazilian LawGPT", False],
                ["You can ask questions about the document", False],
                ["Ask general questions by adding the --open flag at the end", False], 
                [" - example: what is the LLM model? --open ", False],
                [" - Summarize the initial petition", False],
            ],
    'sidebar':{
        'label':'Upload Initial Petition',
        'heading':'Upload the Initial Petition',
        'heading_2':'Upload through a URL',
        'label_2':'Insert the document URL',
        'button':'Submit'},
    'questions_data':{'Question': [
            'What is the theme of the Brazlian Supreme Court that is most similar to the petition?',
            'Summarize the facts described in the initial petition',
            'What is the subject of the initial petition?',
        ]},
    'table_name':'Questions',
    'table_header':'Some possible questions that can be asked',
    'table_subtitle':'Initial Petition Analysis',
    'initial_petition':'Initial Petition',
    'dialog':{
        'title':'Adapting your dataset...',
        'caption':'Please wait...',
        'label':'Processing and indexing the initial petition...'},
    'dialog_home':{
        'title':'Adapting the existing document collections...',
        'caption':'Please wait...',
        'label':'Processing the collections...'},
}