prompts = {
    'system_prompt': """Você é um assistente virtual que ajuda tribunais e outros orgões jurídicos em sumarizações de processos legais.
Apenas responda as perguntas em português e jamais use outro idioma.
Responda as pergunta com informações fornecidas no contexto, não crie nenhuma informação.
Caso não encontre informações suficientes para responder a alguma das perguntas, não escreva nada e não se justifique.
Ignore trechos de endereço eletrônico, telefones e assinaturas eletronicas, como "endereço eletrônico http://www.stf.jus.br/portal/autenticacao/autenticarDocumento.asp"
Ignore assinaturas e roda-pés, como "Este documento é cópia do original", etc.
""",
    'system_prompt_eng': """You are a virtual assistant that helps courts and other legal organizations in summarizing legal processes.
Just answer the questions in English and never use another language.
Answer the question with information provided in the context, do not create any information.
""",
}


# --------------------------------------------------------------------------------
# ESTRATÉGIA 2 - USANDO SUMMARIZE TASK PARA CONJUNTOS DE PERGUNTAS DE CADA DOCUMENTO E FORMAR CADA PARÁGRAFO DO RELATÓRIO

pre_prompt_summary_acordao = """
Com base no acórdão recorrido, escreva um parágrafo curto e objetivo em português com as respostas às perguntas abaixo.
ACORDÃO RECORRIDO:\n\n"""
prompt_summary_acordao = """
Usando apenas as partes do acórdão recorrido acima, escreve de maneira sucinta e em apenas um parágrafo em português brasileiro as seguintes informações:
- Escreva um breve resumo sobre o assunto do processo.
- Qual o orgão julgador ou tribunal de justiça que proferiu o acórdão recorrido?
- Se houve reforma ou confirmação de decisão anterior?
- A decisão foi proferida por unanimidade de votos ou por maioria.
- Agravo foi provido ou desprovido?
- Quais foram os fundamentos apresentados pelo relator.

Coloque todas as informações em apenas um parágrafo. Mantenha a resposta em português.
RESUMO:\n"""

pre_prompt_summary_acordao_recurso = """
Com base no acórdão recorrido, escreva um parágrafo curto e objetivo em português com as respostas às perguntas abaixo.
ACORDÃO RECORRIDO:\n\n"""
prompt_summary_acordao_recurso = """
Usando apenas as partes do acórdão recorrido acima, escreve de maneira sucinta e em apenas um parágrafo em português brasileiro as seguintes informações:
- Escreva um breve resumo sobre o assunto do recurso.
- Qual o orgão julgador ou tribunal de justiça que proferiu o acórdão recorrido?
- Se houve reforma ou confirmação de decisão anterior?
- A decisão foi proferida por unanimidade de votos ou por maioria.
- Agravo foi provido ou desprovido?
- Quais foram os fundamentos apresentados pelo relator.

Leve em consideração que o processo se trata de um RECURSO EXTRAORDINARIO e coloque todas as informações em apenas um parágrafo. 

RESUMO:\n"""
pre_prompt_summary_acordao_agravo = """
Com base no acórdão recorrido, escreva um parágrafo curto e objetivo em português com as respostas às perguntas abaixo.
ACORDÃO RECORRIDO:\n\n"""
prompt_summary_acordao_agravo = """
Usando apenas as partes do acórdão recorrido acima, escreve de maneira sucinta e em apenas um parágrafo em português brasileiro as seguintes informações:
- Escreva um breve resumo sobre o assunto do agravo.
- Qual o orgão julgador ou tribunal de justiça que proferiu o acórdão recorrido?
- Se houve reforma ou confirmação de decisão anterior?
- A decisão foi proferida por unanimidade de votos ou por maioria.
- Agravo foi provido ou desprovido?
- Quais foram os fundamentos apresentados pelo relator.

Leve em consideração que o processo se trata de um AGRAVO e coloque todas as informações em apenas um parágrafo.

RESUMO:\n"""
# --------------------------------------------------------------------------------
pre_prompt_summary_ementa = """
Com base no acórdão recorrido fornecido abaixo, encontre e transcreva a ementa do acórdão recorrido.
ACORDÃO RECORRIDO:\n\n
"""
prompt_summary_ementa = """
Usando apenas as partes do acórdão recorrido fornecido, encontre no texto e transcreva a ementa completo do acórdão recorrido.
Transcreva exatamente como ela aparece no texto.

EMENTA:\n
"""
# --------------------------------------------------------------------------------
pre_prompt_summary_recurso = """
Com base no recurso extraordinário, escreva um parágrafo curto e objetivo em português com as respostas às perguntas abaixo.
RECURSO EXTRAORDINÁRIO:\n\n
"""
prompt_summary_recurso = """
Usando apenas as partes do recurso extraordinário acima, escreve de maneira sucinta e em apenas um parágrafo as seguintes informações:
- Quais os pedidos formulados no recurso. Inclua no texto os artigos (art.), incisos (inc.) e alíneas e respectivos dispositivos

RESPOSTA:\n"""
# --------------------------------------------------------------------------------
pre_prompt_summary_admissibilidade = """
Com base na decisão de admissibilidade do recurso extraordinário, escreva um parágrafo curto e objetivo em português com as respostas às perguntas abaixo.
DECISÃO DE ADMISSIBILIDADE:\n\n
"""
prompt_summary_admissibilidade = """
Usando apenas as partes da decisão de admissibilidade do recurso extraordinário acima, escreva de maneira sucinta e em apenas um parágrafo as seguintes informações:
- Com qual fundamento o recurso extraordinário foi interposto e quais os dispositivos indicados como violados. Inclua no texto os artigos (art.), incisos (inc.), alíneas e respectivos dispositivos'
- Quais as contrarrazões apresentadas pelo relator.
- Qual foi o juízo de admissibilidade do recurso extraordinário (admissão ou inadmissão) e quais os seus fundamentos. Inclua no texto os fundamentos apresentados pelo juízo de admissibilidade quando houver (matéria infraconstitucional, súmulas do STF ou STJ etc.)
"""
# --------------------------------------------------------------------------------
pre_prompt_summary_embargos = """
Com base na decisão de admissibilidade do recurso extraordinário, escreva um parágrafo curto e objetivo em português com as respostas às perguntas abaixo.
DECISÃO DE ADMISSIBILIDADE:\n\n
"""
prompt_summary_embargos = """
Usando apenas as partes da decisão de admissibilidade do recurso extraordinário acima, escreva em português brasileiro e de maneira sucinta se os embargos de declaração opostos contra o acórdão foram aceitos ou negados?

RESPOSTA:\n"""




hypothetical_ementa_prompt_org = """
A ementa de um acórdão é o resumo inicial do conteúdo do acórdão. Abaixo seguem alguns exemplos de ementas de outros acórdãos:
EXEMPLO 1:
APELAÇÃO CRIMINAL—EMBRIAGUEZ AO VOLANTE (ART. 306, §1°, inciso IDO CTB) — RECURSO EXCLUSIVO DA DEFESA — PRELIMINAR DE NULIDADE POR AUSÊNCIA DE PROPOSTA DE ANPP E SURSIS — INEXISTENTE — RÉU QUE NÃO ATENDE AOS REQUISITOS LEGAIS PARA OS CITADOS BENEFÍCIOS. PLEITO ABSOLUTÓRIO, TÃO SOMENTE. QUANTO AO DELITO TIPIFICADO NO ART. 306, DO CTB — INACOLHIDO — DELITO COMETIDO NA VIGÊNCIA DA LEI 12.670/2012 - CONCENTRAÇÃO DE ÁLCOOL SUPERIOR A 0,3 MILIGRAMAS POR LITRO DE AR EXPELIDO DOS PULMÕES — ESTADO DE EMBRIAGUEZ COMPROVADO PELOS DEPOIMENTOS DOS POLICIAIS MILITARESE CAPACIDADE PSICOMOTORA ALTERADA EM RAZÃO DA INFLUÊNCIA DO ÁLCOOL - CONDENAÇÃO MANTIDA — PREQUESTIONAMENTO IMPOSSIBILIDADE. RECURSO CONHECIDO E DESPROVIDO.

EXEMPLO 2:
AGRAVO EM EXECUÇÃO PENAL — PROGRESSÃO DE REGIME PRISIONAL — PLEITO QUE AINDA NÃO FOI OBJETO DE APRECIAÇÃO PERANTE O JUIZO DE PRIMEIRO GRAU — IMPOSSIBILIDADE DE IMEDIATA ANÁLISE NESTA INSTÂNCIA, SOB PENA DE SUPRESSÃO DE UM GRAU DE JURISDIÇÃO — REQUISITO OBJETIVO QUE, DE TODO MODO, NÃO SE ENCONTRA PREENCHIDO RECURSO DE AGRAVO DESPROVIDO.

EXEMPLO 3:
DIREITO PROCESSUAL CIVIL. AGRAVO INTERNO NA APELAÇÃO CÍVEL. PRELIMINAR. NÃO CONHECIMENTO PARCIAL DO RECURSO. VIOLAÇÃO AO PRINCIPIO DA DIALETICIDADE. PRELIMINAR ACOLHIDA. PRELIMINAR. NULIDADE DO JULGAMENTO MONOCRÁTICO. INCORRÊNCIA. APLICABILIDADE DO ARTIGO 932, DO CÓDIGO DE PROCESSO CIVIL. RECURSO PARCIALMENTE CONHECIDO E IMPROVIDO.

EXEMPLO 4:
APELAÇÃO TRÁFICO DE DROGAS. Preliminares Nulidade da diligência diante da ausência de autorização judicial, bem como por ter se baseado em denúncia anônima – Inocorrência. Existência de justa causa para a realização da medida Crime permanente Agentes policiais que, ademais, adotaram outras diligências para a averiguação da denúncia anônima recebida Preliminares rejeitadas - Mérito - Autoria e materialidade delitivas nitidamente delineadas nos autos Firmes e seguras palavras dos agentes estatais Depoimentos que se revestem de fé-pública, estando corroborados pelo restante do conjunto probatório Ausência de provas de que teriam intuito de prejudicar o réu. Desnecessidade de comprovação de atos de comércio Crime de conteúdo variado Pena e regime que ficam mantidos. Recurso desprovido.


Com base nesses exemplos, escreva uma possível ementa do acórdão recorrido.
Inclua apenas informações presentes no resumo do acordão abaixo:
RESUMO DO ACORDÃO RECORRIDO:
{0}

EMENTA:\n"""


extract_prompt = """
A ementa de um acórdão é o resumo inicial do conteúdo do acórdão. Abaixo seguem alguns exemplos de ementas de outros acórdãos:
EXEMPLO 1:
APELAÇÃO CRIMINAL—EMBRIAGUEZ AO VOLANTE (ART. 306, §1°, inciso IDO CTB) — RECURSO EXCLUSIVO DA DEFESA — PRELIMINAR DE NULIDADE POR AUSÊNCIA DE PROPOSTA DE ANPP E SURSIS — INEXISTENTE — RÉU QUE NÃO ATENDE AOS REQUISITOS LEGAIS PARA OS CITADOS BENEFÍCIOS. PLEITO ABSOLUTÓRIO, TÃO SOMENTE. QUANTO AO DELITO TIPIFICADO NO ART. 306, DO CTB — INACOLHIDO — DELITO COMETIDO NA VIGÊNCIA DA LEI 12.670/2012 - CONCENTRAÇÃO DE ÁLCOOL SUPERIOR A 0,3 MILIGRAMAS POR LITRO DE AR EXPELIDO DOS PULMÕES — ESTADO DE EMBRIAGUEZ COMPROVADO PELOS DEPOIMENTOS DOS POLICIAIS MILITARESE CAPACIDADE PSICOMOTORA ALTERADA EM RAZÃO DA INFLUÊNCIA DO ÁLCOOL - CONDENAÇÃO MANTIDA — PREQUESTIONAMENTO IMPOSSIBILIDADE. RECURSO CONHECIDO E DESPROVIDO.

EXEMPLO 2:
AGRAVO EM EXECUÇÃO PENAL — PROGRESSÃO DE REGIME PRISIONAL — PLEITO QUE AINDA NÃO FOI OBJETO DE APRECIAÇÃO PERANTE O JUIZO DE PRIMEIRO GRAU — IMPOSSIBILIDADE DE IMEDIATA ANÁLISE NESTA INSTÂNCIA, SOB PENA DE SUPRESSÃO DE UM GRAU DE JURISDIÇÃO — REQUISITO OBJETIVO QUE, DE TODO MODO, NÃO SE ENCONTRA PREENCHIDO RECURSO DE AGRAVO DESPROVIDO.

EXEMPLO 3:
APELAÇÃO TRÁFICO DE DROGAS. Preliminares Nulidade da diligência diante da ausência de autorização judicial, bem como por ter se baseado em denúncia anônima – Inocorrência. Existência de justa causa para a realização da medida Crime permanente Agentes policiais que, ademais, adotaram outras diligências para a averiguação da denúncia anônima recebida Preliminares rejeitadas - Mérito - Autoria e materialidade delitivas nitidamente delineadas nos autos Firmes e seguras palavras dos agentes estatais Depoimentos que se revestem de fé-pública, estando corroborados pelo restante do conjunto probatório Ausência de provas de que teriam intuito de prejudicar o réu. Desnecessidade de comprovação de atos de comércio Crime de conteúdo variado Pena e regime que ficam mantidos. Recurso desprovido.

EXEMPLO 4:
PENAL E PROCESSO PENAL. CRIME DE FALSIFICAÇÃO DE DOCUMENTO PÚBLICO.
AUSÊNCIA DE CORRELAÇÃO ENTRE A DENÚNCIA E A SENTENÇA.
INOBSERVÂNCIA DA MUTATIO LIBELLI. ABSOLVIÇÃO. DELITOS DE FALSA
IDENTIDADE E DE USO DE DOCUMENTO FALSO. MATERIALIDADE E AUTORIA
COMPROVADAS. DOSIMETRIA. CONFISSÃO ESPONTÂNEA DE TODOS OS DELITOS.
INOCORRÊNCIA. PENAS DE RECLUSÃO E DETENÇÃO. NATUREZAS DISTINTAS.
CONCURSO MATERIAL DE CRIMES. REQUISITOS PREENCHIDOS.
PARCIAL PROVIMENTO.

EXEMPLO 5:
PROCESSUAL CIVIL E PREVIDENCIÁRIO. AGRAVO DE INSTRUMENTO. CUMPRIMENTO DE SENTENÇA. DESCONTO DOS VALORES RECEBIDOS DE AUXÍLIO-ACIDENTE. POSSIBILIDADE.
- A Primeira Seção do Superior Tribunal de Justiça, no julgamento do Recurso Especial Repetitivo 1.296.673/MG, de Relatoria do Ministro Herman Benjamin, firmou entendimento no sentido de que a cumulação do auxílio-acidente com aposentadoria é possível, desde que a eclosão da lesão incapacitante e a concessão da aposentadoria tenham ocorrido antes de 11/11/1997, data de edição da Medida Provisória 1.596-14/97, posteriormente convertida na Lei 9.528/1997.
- Obrigatoriedade de que tanto a lesão incapacitante quanto a concessão da aposentadoria tenham ocorrido antes de 11/11/1997 , a fim de possibilitar a cumulação.
- In casu, a lesão incapacitante ocorreu em 17/08/1994, todavia a aposentadoria por tempo de contribuição foi concedida a partir de 17/02/2011, ou seja, bem após a edição da Lei 9.528/1997, portanto vedada a cumulação pleiteada.
- Agravo de instrumento improvido.

------------------------------------------------

Levando em consideração apenas o texto do acordão abaixo, transcreva a ementa exatamente como ela aparece no texto. Caso não encontre, não escreva nada e não se justifique.
TEXTO DO ACORDÃO:\n"""


hypothetical_ementa_prompt = """
A ementa de um acórdão é o resumo inicial do conteúdo do acórdão. Abaixo seguem alguns exemplos de ementas de outros acórdãos a partir de seus respectivos resumos:

RESUMO DO ACORDÃO RECORRIDO:
O acórdão recorrido foi proferido pelo Supremo Tribunal Federal (STF) e versa sobre um recurso de apelação cível. A decisão foi proferida por unanimidade de votos e confirmou a decisão anterior, que era favorável à parte appellante. O relator, Desembargador Expedito Ferreira, apresentou argumentos relativos à ausência de interesse público para a intervenção no feito, tanto pela natureza da lide quanto pela qualidade da parte, e à falta de matéria que justifique a intervenção ministerial nessa segunda instância. O acordo foi provido.
EMENTA:
APELAÇÃO CÍVEL. AÇÃO DE CONSTITUIÇÃO DE SERVIDÃO ADMINISTRATIVA COM PEDIDO LIMINAR DE IMISSÃO NA POSSE INAUDITA ALTERA PARS. AUSÊNCIA DE INTERESSE PÚBLICO PARA INTERVENÇÃO NO FEITO, QUER PELA NATUREZA DA LIDE, QUER PELA QUALIDADE DA PARTE. NÃO INTERVENÇÃO.

RESUMO DO ACORDÃO RECORRIDO:
O acórdão recorrido foi proferido pelo Supremo Tribunal Federal (STF), órgão julgador máximo do Brasil. O assunto do acórdão refere-se a um recurso extraordinário contra uma decisão da 12ª Vara Criminal de São Paulo, que condenou o réu a 5 anos de reclusão por crime previsto na Lei n. 8.137/90. A decisão do STF confirmou a decisão da vara criminal e mantém a pena privativa de liberdade de 5 anos, além de multa e restritivas de direitos. A decisão foi proferida por unanimidade de votos, com o relator Ministro Paulo Gustavo Guedes Fontes. Os fundamentos apresentados pelo relator são a existência de reincidência, uma vez que o réu já havia sido condenado anteriormente por crime similar, e a confissão espontânea do réu, que foi considerada como atenuante da pena.
EMENTA: 
DIREITO PENAL. APELAÇÃO CRIMINAL. APROPRIAÇÃO INDÉBITA PREVIDENCIÁRIA. SONEGAÇÃO DE CONTRIBUIÇÃO PREVIDENCIÁRIA. PRESCRIÇÃO DA PRETENSÃO PUNITIVA NÃO OCORRIDA. PRELIMINAR REJEITADA. MATERIALIDADE E AUTORIA DELITIVAS COMPROVADAS. DOLO GENÉRICO DEMONSTRADO. INEXIGIBILIDADE DE CONDUTA DIVERSA. ART. 168-A, §1o DO CÓDIGO PENAL. FALÊNCIA. OCORRÊNCIA. ABSOLVIÇÃO. INAPLICABILIDADE COM RELAÇÃO AO ART. 337-A DO CÓDIGO PENAL. REGIME INICIAL ABERTO. SUBSTITUIÇÃO DA PENA PRIVATIVA DE LIBERDADE POR RESTRITIVAS DE DIREITOS. APELAÇÃO DA DEFESA PARCIALMENTE PROVIDA.

RESUMO DO ACORDÃO RECORRIDO:
O acórdão recorrido foi proferido pelo Tribunal de Justiça do Estado de São Paulo, em Ribeirão Preto, São Paulo. O assunto em disputa é um recurso contra uma decisão de um tribunal inferior que declarou a inexigibilidade de uma dívida e ordenou o pagamento de danos morais. A decisão foi reformada, declarando a inexigibilidade da dívida.
A decisão foi proferida por unanimidade de votos, com o relator Marco Gozzo. Os fundamentos apresentados pelo relator incluem a interpretação de que a responsabilidade da instituição financeira é objetiva, e que a fixação de R$ 8.000,00 para reparação do dano moral é razoável.
EMENTA:
AÇÃO DECLARATÓRIA C.C PEDIDO DE INDENIZAÇÃO POR DANOS MORAIS. Sentença que julgou improcedentes os pedidos iniciais. Insurgência da demandante. DANOS MORAIS. Não observados. Inscrição do nome da requerente no rol dos maus pagadores não comprovada. Por outro lado, o cadastro da dívida na plataforma “Serasa Limpa Nome”, de acesso exclusivo da consumidora, para fins de negociação, não configura danos morais. Decisão reformada nesse ponto.

RESUMO DO ACORDÃO RECORRIDO:
O acórdão recorrido foi proferido pelo Tribunal de Justiça do Distrito Federal e dos Territórios, 8ª Turma Cível, em Brasília (DF), em 07/11/2019. O assunto do acórdão refere-se a um recurso contra a sentença prolatada pela Juíza da Sexta Vara da Fazenda Pública do Distrito Federal, que indeferiu pedidos de retificação de informações de créditos e débitos nos Livros Fiscais Eletrônicos - LFE, referentes aos períodos de março/2016 a abril/2016. O recurso foi interposto por Lojas Renner S.A.
O acórdão confirma a decisão anterior, mantendo a indeferida dos pedidos de retificação. O Relator sustenta que a apelante, Lojas Renner S.A., não possui direito líquido e certo para afastar o parágrafo 6º do artigo 54 do Regulamento do ICMS.
EMENTA:
CONSTITUCIONAL E TRIBUTÁRIO. APELAÇÃO CÍVEL. MANDADO DE SEGURANÇA. ATO ADMINISTRATIVO. PRESUNÇÃO DE LEGALIDADE. PROVA PRÉ-CONSTITUÍDA. INDISPENSABILIDADE. LIVROS FISCAIS ELETRÔNICOS. ESCRITURAÇÃO. INADIMPLEMENTO. ÔNUS DA OMISSÃO. CONTRIBUINTE. ICMS. NÃO-CUMULATIVIDADE. ALEGAÇÃO DE DESCUMPRIMENTO. INADMISSIBILIDADE.

RESUMO DO ACORDÃO RECORRIDO:
O acórdão recorrido foi proferido pelo Tribunal de Justiça do Estado de Sergipe, em 17 de fevereiro de 2023. O assunto do acórdão é um recurso extraordinário contra a decisão da Vara Criminal da Comarca de Moita Bonita/SE, que condenou o réu José Eduardo Santana dos Santos por cometer o crime de embriaguez ao volante, previsto no art. 306, § 1°, inciso I do CTB. A decisão do Tribunal de Justiça do Estado de Sergipe foi por unanimidade de votos, mantendo a sentença objurgada e negando o provimento do recurso. O relator, Ana Lúcia Freire de Anjos, argumentou que a condição de embriaguez do réu foi comprovada pelos depoimentos dos policiais militares e pela concentração de álcool superior a 0,3 miligramas por litro de ar expelido dos pulmões, e que a Lei 12.670/2012 é aplicável ao caso.
EMENTA: 
APELAÇÃO CRIMINAL —EMBRIAGUEZ AO VOLANTE (ART. 306, §1°, inciso IDO CTB) — RECURSO EXCLUSIVO DA DEFESA — PRELIMINAR DE NULIDADE POR AUSÊNCIA DE PROPOSTA DE ANPP E SURSIS — INEXISTENTE — RÉU QUE NÃO ATENDE AOS REQUISITOS LEGAIS PARA OS CITADOS BENEFÍCIOS. PLEITO ABSOLUTÓRIO, TÃO SOMENTE. QUANTO AO DELITO TIPIFICADO NO ART. 306, DO CTB — INACOLHIDO — DELITO COMETIDO NA VIGÊNCIA DA LEI 12.670/2012 — CRIME DE PERIGO ABSTRATO — CONCENTRAÇÃO DE ÁLCOOL SUPERIOR A 0,3 MILIGRAMAS POR LITRO DE AR EXPELIDO DOS PULMÕES — ESTADO DE EMBRIAGUEZ COMPROVADO PELOS DEPOIMENTOS DOS POLICIAIS MILITARESE CAPACIDADE PSICOMOTORA ALTERADA EM RAZÃO DA INFLUÊNCIA DO ÁLCOOL - CONDENAÇÃO MANTIDA — PREQUESTIONAMENTO IMPOSSIBILIDADE - RECURSO CONHECIDO E DESPROVIDO.

Com base nesses exemplos, escreva uma possível ementa do acórdão recorrido cujo resumo é apresentado abaixo
RESUMO DO ACORDÃO RECORRIDO:
{0}

EMENTA:\n"""


prompt_acordao = {
    'pre_prompt_summary': pre_prompt_summary_acordao,
    'prompt_summary': prompt_summary_acordao
}
prompt_acordao_recurso = {
    'pre_prompt_summary': pre_prompt_summary_acordao_recurso,
    'prompt_summary': prompt_summary_acordao_recurso
}
prompt_acordao_agravo = {
    'pre_prompt_summary': pre_prompt_summary_acordao_agravo,
    'prompt_summary': prompt_summary_acordao_agravo
}
prompt_ementa = {
    'pre_prompt_summary': pre_prompt_summary_ementa,
    'prompt_summary': prompt_summary_ementa,
    'hypothetical_ementa_prompt': hypothetical_ementa_prompt,
    'extract_prompt': extract_prompt
}
prompt_recurso = {
    'pre_prompt_summary': pre_prompt_summary_recurso,
    'prompt_summary': prompt_summary_recurso
}
prompt_admissibilidade = {
    'pre_prompt_summary': pre_prompt_summary_admissibilidade,
    'prompt_summary': prompt_summary_admissibilidade
}
prompt_embargos = {
    'pre_prompt_summary': pre_prompt_summary_embargos,
    'prompt_summary': prompt_summary_embargos
}

