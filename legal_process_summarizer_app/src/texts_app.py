texts_app_eng = {
    'title':'Legal Process Summarizer',
    'subtitle': 'LLM and GenAI applied to legal processes',
    'first_rows':[
                ["Welcome! I am Virtual Legal Assistant and I am here to help you summarize and interpret legal processes", False],
            ],
    'header':{
        'chat_page_button':'Chat with the process',
        'voltar':'Back',
    },
    'process_filter':'Process selection for analysis',
    'process_number':'Choose an existing process',
    'process_number_placeholder':'Process number',
    'back_botton':'Clear selection',
    'submit_process':'Choose process',
    'file_upload':'Upload a new process (zip)',
    'submit_zip_file':'Upload a new process',
    'dialog':{
        'title':'Processing and indexing the documents of the process...',
        'caption':'Please wait...',
        'label':'Indexing the chosen process...'},
    'dialog_home':{
        'title':'Adapting the existing document collections...',
        'caption':'Please wait...',
        'label':'Processing the collections...'},
    'error_message':'Please, select a process or upload a new one before proceeding',
    'error_message_upload':'Please, select a process to upload',
    'dialog_upload':'Please, inform the number of the process you are uploading',
    'docs_indexed':'**Legal Documents** Indexed',
    'steps_texts':{
        'step_0':'Indexing the legal process documents...',
        'step_1':'Searching for references and analyzing the questions...',
        'step_2':'Building the final report...',
        'docs':'💡 {0} documents correctly indexed',
        'perguntas':'💡 12 questions analyzed while building the report',
        'resumo_botao':'Report & Analysis'
    },
    'references':{
        'caption':'Explore the references used to build the report',
        'title':'**Topics explored to build the report** 📄',
        'dropdown':'Select a topic',
        'caption_close':'Close the references',
        'reference_number':'**Reference {0}**',
        'relevance':'**Document:** {0} | **Relevance:** {1}%',
        'sidebar_subtext':'Area dedicated to the references used to answer the questions.',
    },
    'topic_labels':{
            'Orgão julgador, decisão e fundamentos apresentados e relatados no acordão recorrido': 'Judging court, decision and grounds presented and reported in the appealed ruling',
            'Transcrição literal da ementa': 'Transcript of the summary of the ruling',
            'Decisão dos embargos de declaração': 'Decision on the Amendment of Judgment request',
            'Pedidos e argumentos do recurso extraordinário': 'Requests and arguments for the extraordinary appeal',
            'Decisão de admissibilidade do recurso extraordinário': 'Decision on the admissibility of the extraordinary appeal',
    },
    'init_prompt': "Thank you for choosing the process **{0}**.\n Feel free to ask questions about the process.",
}


texts_app_pt = {
    'title':'Sumarizador de Processos Jurídicos',
    'subtitle': 'LLM e GenAI aplicados a processos jurídicos',
    'first_rows':[
                ["Olá! Eu sou a Assistente Virtual Jurídica e estou aqui para ajudá-lo a resumir e interpretar processos jurídicos", False],
            ],
    'header':{
        'chat_page_button':'Converse com o processo',
        'voltar':'Voltar',
    },
    'process_filter':'Seleção de processos para análise',
    'process_number':'Escolha um processo existente',
    'process_number_placeholder':'Número do processo',
    'back_botton':'Limpar seleção',
    'submit_process':'Escolher processo',
    'file_upload':'Carregar um novo processo (zip)',
    'submit_zip_file':'Carregar um novo processo',
    'dialog':{
        'title':'Processando e indexando os documentos do processo...',
        'caption':'Por favor, aguarde...',
        'label':'Indexando o processo escolhido...'},
    'dialog_home':{
        'title':'Adaptando as coleções de documentos existentes...',
        'caption':'Por favor, aguarde...',
        'label':'Processando as coleções...'},
    'error_message':'Por favor, selecione um processo ou carregue um novo antes de prosseguir',
    'error_message_upload':'Por favor, selecione um processo para carregar',
    'dialog_upload':'Por favor, informe o número do processo que você está carregando',
    'docs_indexed':'**Documentos Jurídicos** Indexados',
    'steps_texts':{
        'step_0':'Indexando os documentos do processo jurídico...',
        'step_1':'Buscando referências e analisando as perguntas...',
        'step_2':'Construindo o relatório final...',
        'docs':'💡 {0} documentos corretamente indexados',
        'perguntas':'💡 12 perguntas analisadas durante a construção do relatório',
        'resumo_botao':'Relatório & Análise'
    },
    'references':{
        'caption':'Explore as referências utilizadas para construir o relatório',
        'title':'**Tópicos explorados para construir o relatório** 📄',
        'dropdown':'Selecione um tópico',
        'caption_close':'Fechar as referências',
        'reference_number':'**Referência {0}**',
        'relevance':'**Documento:** {0} | **Relevância:** {1}%',
        'sidebar_subtext':'Área dedicada às referências utilizadas para responder às perguntas.',
    },
    'topic_labels':{
        'Orgão julgador, decisão e fundamentos apresentados e relatados no acordão recorrido': 'Orgão julgador, decisão e fundamentos apresentados e relatados no acordão recorrido',
        'Transcrição literal da ementa': 'Transcrição literal da ementa',
        'Decisão dos embargos de declaração': 'Decisão dos embargos de declaração',
        'Pedidos e argumentos do recurso extraordinário': 'Pedidos e argumentos do recurso extraordinário',
        'Decisão de admissibilidade do recurso extraordinário': 'Decisão de admissibilidade do recurso extraordinário',
    },
    'init_prompt': "Obrigado por escolher o processo **{0}**.\n Sinta-se à vontade para fazer perguntas sobre o processo.",
}