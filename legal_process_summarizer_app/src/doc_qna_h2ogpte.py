from h2ogpte import H2OGPTE
import datetime
import json
import fitz
import asyncio
from loguru import logger
from .prompts import *
from .page_dashboard import get_status


class H2OGPTEClient:
    def __init__(self, address, api_key):
        self.address = address
        self.api_key = api_key
        self.client = H2OGPTE(address=self.address, api_key=self.api_key)

    def create_collection(self, name, description):
        logger.info(f'Creating collection {name}')
        collection_id = None
        recent_collections = self.client.list_recent_collections(0, 1000)
        for c in recent_collections:
            if c.name == name:
                collection_id = c.id
                logger.info(f'Collection {name} already exists')
                break

        if collection_id is None:
            collection_id = self.client.create_collection(
                name=name,
                description=description,
            )
            logger.info(f'Collection {name} created')
            self._save_collection_id(collection_id)
        return collection_id
    
    def _save_collection_id(self, collection_id):
        creation_dict = dict()
        creation_dict['collection_id'] = collection_id
        creation_dict['creation_date'] = str(datetime.datetime.now())
        json_file_path = "./collection_list.json"
        with open(json_file_path, "r") as json_file:
            existing_collections = json.load(json_file)

        existing_collections.append(creation_dict)
        logger.info(f"Num of colletions already created: {len(existing_collections)}")
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(existing_collections, json_file, indent=4)
        logger.info(f"Collection {collection_id} saved")
        return

    def drop_all_collections(self, collection_id = None):
        if collection_id:
            self.client.delete_collections([collection_id])
        else:
            while True:
                collections = self.client.list_recent_collections(0, 100)
                if len(collections) == 0:
                    break
                collection_ids = [c.id for c in collections]
                self.client.delete_collections(collection_ids)
        return     

    def drop_all_docs(self, collection_id):
        logger.info(f'Dropping all docs from collection {collection_id}')
        while True:
            docs = self.client.list_documents_in_collection(collection_id, 0, 1000)
            if len(docs) == 0:
                break
            doc_ids = [d.id for d in docs]
            self.client.delete_documents_from_collection(collection_id, doc_ids)
            self.client.delete_documents(doc_ids)
        self.drop_all_collections(collection_id)
        return

    def list_all_docs(self, collection_id):
        logger.info(f'Listing all docs from collection {collection_id}')
        docs = self.client.list_documents_in_collection(collection_id, 0, 1000)
        doc_id_dict = {d.name: d.id for d in docs}
        return doc_id_dict

    def ingest_filepath(self, filepath, collection_id):
        filename = str(filepath).split('/')[-1]
        logger.info(f'Ingesting file {filename}')
        documents = self.client.list_documents_in_collection(collection_id, 0, 1000)
        document_ids = [d.id for d in documents if d.name == filename]
        if len(document_ids) == 0:
            with open(filepath, 'rb') as f:
                doc = self.client.upload(filename, f)
            self.client.ingest_uploads(collection_id, [doc])
            logger.info(f'File {filename} ingested')
        else:
            logger.info(f'File {filename} already ingested')
        return
    
    async def ingest_url(self, url, collection_id):
        filename = url.split("/")[-1]
        documents = self.client.list_documents_in_collection(collection_id, 0, 1000)
        document_ids = [d.id for d in documents if d.name == filename]
        if len(document_ids) == 0:
            self.client.ingest_website(collection_id, url)
            logger.info(f'File {filename} ingested')
        else:
            logger.info(f'File {filename} already ingested')
        
        chunks = self._get_collection_chunks(collection_id)
        return chunks
    
    def _get_collection_chunks(self, collection_id):
        chunk_sizes = 200
        while True:
            chunks_ids = list(range(1, int(chunk_sizes)))
            try:
                chunks = self.client.get_chunks(collection_id, chunks_ids)
                break
            except:
                chunk_sizes = int(chunk_sizes*0.9)
                print(f'chunk_sizes: {chunk_sizes}')
            if chunk_sizes < 1:
                break

        chunks = [c.text for c in chunks]
        chunks = [text.replace('\n', ' ') for text in chunks]
        return chunks



class QnAManager:
    def __init__(self, client, llm):
        from .prompts import prompts
        self.client = client.client
        self.llm = llm
        self._get_history()
        self.cfg = dict()
        self.prompts = prompts
        self.perguntas = {
            1: {'prompts': prompt_acordao,
                'doc_type_source': ['acordao-recorrido'],
                'adjacent_chunks': 1,
                'task': 'summarize',
                'label': 'Orgão julgador, decisão e fundamentos apresentados e relatados no acordão recorrido'},
            2: {'prompts': prompt_ementa,
                'doc_type_source': ['acordao-recorrido'],
                'adjacent_chunks': 1,
                'task': 'ementa',
                'label': 'Transcrição literal da ementa'},
            3: {'prompts': prompt_embargos,
                'doc_type_source': ['acordao-embargos'],
                'adjacent_chunks': 0,
                'task': 'query',
                'label': 'Decisão dos embargos de declaração'},
            4: {'prompts': prompt_recurso,
                'doc_type_source': ['recurso-extraordinario'],
                'adjacent_chunks': 1,
                'task': 'summarize',
                'label': 'Pedidos e argumentos do recurso extraordinário'},
            5: {'prompts': prompt_admissibilidade,
                'doc_type_source': ['decisao-admissibilidade'],
                'adjacent_chunks': 1,
                'task': 'query',
                'label': 'Decisão de admissibilidade do recurso extraordinário'},
        }
        self.respostas_perguntas = []

    def _get_history(self):
        import os
        start_dir = "./"
        history_file = "history.json"
        json_file_path = None
        for root, dirs, files in os.walk(start_dir):
            if history_file in files:
                json_file_path = os.path.join(root, history_file)
                break
        if json_file_path is None:
            json_file_path = os.path.join(start_dir, history_file)
            with open(json_file_path, "w") as json_file:
                json.dump([], json_file)
        self.history_file_path = json_file_path

    def _answer_question(self, chat_args):
        try:
            response = self.client.answer_question(**chat_args).content
        except Exception as e:
            logger.warning(f"Error answering question: {e}")
            response = 'It was not possible to build an answer at the moment. Please, contact the application administrators.'
        return response
    
    def _summarize_content(self, chat_args):
        try:
            response = self.client.summarize_content(**chat_args).content
        except Exception as e:
            logger.warning(f"Error summarizing content: {e}")
            response = 'It was not possible to build an answer at the moment. Please, contact the application administrators.'
        return response
    
    def _translate_eng_to_pt(self, text):
        logger.info(f'Translating text to Portuguese')
        logger.info(f'Text: {text}')
        chat_args = {
            "system_prompt": self.prompts['system_prompt'],
            "question": f"""{text}\n\nApenas traduza o texto acima para o português brasileiro sem adicionar nenhuma informação.""",
            "llm": self.llm,
        }
        response = self._answer_question(chat_args)
        logger.info(f'Response: {response}')
        return response
    
    def _translate_pt_to_eng(self, text):
        logger.info(f'Translating text to English')
        logger.info(f'Text: {text}')
        chat_args = {
            "system_prompt": self.prompts['system_prompt_eng'],
            "question": f"""{text}\n\nTranslate the text above to English. \nTRANSLATION:""",
            "llm": self.llm,
        }
        response = self._answer_question(chat_args)
        logger.info(f'Response: {response}')
        return response

    def _get_adjecent_chunks(self, match_list, collection_id, n=1):
        adjacent_chunks_ids = []
        adjacent_chunks = []
        id_list = [int(match.id) for match in match_list]
        for id in id_list:
            min_id, max_id = max(0, id - n), id + n
            adjacent_chunks_ids.append([x for x in range(min_id, max_id + 1)])
        for chunk_group in adjacent_chunks_ids[:5]:
            try:
                adjacent_chunks.append(self.client.get_chunks(collection_id, chunk_group))
            except:
                if type(chunk_group[1]) == int: chunk_group[1] = [chunk_group[1]]
                logger.warning(f"Error retrieving adjacent chunks")
                logger.warning(f"chunk_group[1]: {chunk_group[1]}")
                adjacent_chunks.append(self.client.get_chunks(collection_id, chunk_group[1]))
        logger.debug(f"Adjacent chunks retrieved: {adjacent_chunks_ids}")
        return adjacent_chunks

    def _search_match(self, collection_processo_id, question_prompt, filter_doc=[]):
        question_vectors = self.client.encode_for_retrieval([question_prompt])
        results_semantic = self.client.match_chunks(collection_processo_id, question_vectors, filter_doc, 0, 5)
        results_lexical = self.client.search_chunks(collection_processo_id, question_prompt, filter_doc, 0, 5)
        hybrid_matches = self._weighted_reciprocal_rank([results_lexical, results_semantic], [0.50, 0.50])
        return hybrid_matches
    
    def _weighted_reciprocal_rank(self, doc_lists, weights, c: float = 60):
        all_documents = set()
        for doc_list in doc_lists:
            for doc in doc_list:
                all_documents.add(doc.id)

        rrf_score_dic = {doc: 0.0 for doc in all_documents}
        for doc_list, weight in zip(doc_lists, weights):
            for rank, doc in enumerate(doc_list, start=1):
                rrf_score = weight * (1 / (rank + c))
                rrf_score_dic[doc.id] += rrf_score

        sorted_documents = sorted(
            rrf_score_dic.keys(), key=lambda x: rrf_score_dic[x], reverse=True
        )

        page_content_to_doc_map = {
            doc.id: doc for doc_list in doc_lists for doc in doc_list
        }
        sorted_docs = [
            page_content_to_doc_map[page_content] for page_content in sorted_documents
        ]
        for i, m in enumerate(sorted_docs):
            m.score = str("%.4f" % (1 - i / len(sorted_docs)))
        return sorted_docs[:3]
    
    def _update_context(self, q, context, label):
        q.client.contexto_processo[label] = context
        return
    
    def _treat_context_list(self, context_list):
        context = []
        for context_i in context_list:
            result = ' '.join([result.text.replace('\n', ' ') for result in context_i])
            context.append(result)
        return context

    def _check_history(self, processo, pergunta):
        check_exist = False
        context = []
        context_full = []
        res=''
        with open(self.history_file_path, "r") as json_file:
            existing_data = json.load(json_file)
        for hist in existing_data:
            if hist['processo']==f"""{processo}""" and hist.get(pergunta) is not None:
                res = hist[pergunta]['response']
                context = hist[pergunta]['context']
                context_full = hist[pergunta]['context_full']
                check_exist = True
                break
        return check_exist, res, context, context_full
    
    def _update_history(self, q):
        logger.debug(f"Updating history...")
        with open(self.history_file_path, "r") as json_file:
            existing_data = json.load(json_file)
        for hist in existing_data:
            if hist['processo']==f"""{q.client.process_selected}""" and hist['llm']==self.llm:
                existing_data.remove(hist)
                break
        existing_data.append(self.cfg)
        with open(self.history_file_path, "w", encoding="utf-8") as json_file:
            json.dump(existing_data, json_file, indent=4)
        return

    def _remove_single_word_newlines(self, text):
        import re
        cleaned_text = re.sub(r'\s*\n(\w+\.?)\n\s*', r' \1 ', text)
        return cleaned_text
    
    def prepare_question_context(self, q, collection_processo_id, pergunta_dict):
        filter_docs = [q.client.doc_type_dict[doc_type] for doc_type in pergunta_dict['doc_type_source'] if q.client.doc_type_dict.get(doc_type) is not None]
        filter_docs = sum(filter_docs, [])
        hybrid_matches = self._search_match(collection_processo_id, pergunta_dict['prompts']['prompt_summary'], filter_doc=filter_docs)
        context_list = self._get_adjecent_chunks(hybrid_matches, collection_processo_id, n=pergunta_dict['adjacent_chunks'])
        context_full = self._treat_context_list(context_list)
        refs = [ref.json() for ref in hybrid_matches[:3]]
        return refs, context_full
    
    async def _perform_task(self, q, pergunta_dict, collection_processo_id):
        task = pergunta_dict['task']
        check_exist, response, context, context_full = self._check_history(q.client.process_selected, pergunta_dict['label'])
        if check_exist:
            logger.info(f"Resposta para '{pergunta_dict['label']}' já existe no histórico...")
            await asyncio.sleep(2)
            return check_exist, response, context, context_full
        
        context, context_full = self.prepare_question_context(q, collection_processo_id, pergunta_dict)
        if task == 'query':
            chat_args = {
                "system_prompt": self.prompts['system_prompt'],
                "text_context_list": context_full,
                "question": pergunta_dict['prompts']['prompt_summary'],
                "llm": self.llm,
                "llm_args": {
                    'max_new_tokens': 200,
                }
            }
            return check_exist, self._answer_question(chat_args), context, context_full
        elif task == 'summarize':
            chat_args = {
                "system_prompt": self.prompts['system_prompt'],
                "pre_prompt_summary": pergunta_dict['prompts']['pre_prompt_summary'],
                "text_context_list": context_full,
                "prompt_summary": pergunta_dict['prompts']['prompt_summary'],
                "docs_token_handling":'chunk',
                "llm": self.llm,
                "llm_args": {
                    'max_new_tokens': 500,
                }
            }
            return check_exist, self._summarize_content(chat_args), context, context_full
        
    async def _hyde_ementa(self, q, pergunta_dict):
        check_exist, response, context, context_full = self._check_history(q.client.process_selected, 'hyde_ementa')
        q.page["main_infos"].progress_perguntas.caption = '{}%'.format('40')
        await q.page.save()
        if check_exist:
            logger.info(f"Resposta para '{pergunta_dict['label']}' já existe no histórico...")
            await asyncio.sleep(2)
            return response
        resumo_acordao = ' '.join(self.respostas_perguntas)
        chat_args_hy_ementa = {
            "system_prompt": self.prompts['system_prompt'],
            "question": pergunta_dict['prompts']['hypothetical_ementa_prompt'].format(resumo_acordao),
            "llm": self.llm,
        }
        logger.info('Gerando uma ementa hipotética...')
        hypothetical_ementa = self._answer_question(chat_args_hy_ementa)
        hypothetical_ementa = 'EMENTA: AGRAVO - AGRAVO DE INSTRUMENTO - APELAÇÃO - DECISÃO - RECURSO - PROVIDO - ' + hypothetical_ementa
        logger.debug(f"\EMENTA HIPOTÉTICA: \n{hypothetical_ementa}\n")
        return hypothetical_ementa
    

    async def _perform_ementa_task(self, q, pergunta_dict, collection_processo_id):
        hypothetical_ementa = await self._hyde_ementa(q, pergunta_dict)
        self.cfg['hyde_ementa'] = {'response': hypothetical_ementa, 'context': [], 'context_full': []}
        q.page["main_infos"].progress_perguntas.caption = '{}%'.format('50')
        await q.page.save()
        check_exist, response, context, context_full  = self._check_history(q.client.process_selected, pergunta_dict['label'])
        if check_exist:
            logger.info(f"Resposta para '{pergunta_dict['label']}' já existe no histórico...")
            await asyncio.sleep(2)
            return response, context, context_full

        filter_docs = [q.client.doc_type_dict[doc_type] for doc_type in pergunta_dict['doc_type_source'] if q.client.doc_type_dict.get(doc_type) is not None]
        filter_docs = sum(filter_docs, [])
        hybrid_matches = self._search_match(collection_processo_id, hypothetical_ementa, filter_doc=filter_docs)
        self._update_context(q, hybrid_matches[:3], pergunta_dict['label'])
        context_list = self._get_adjecent_chunks(hybrid_matches[:3], collection_processo_id, n=pergunta_dict['adjacent_chunks'])

        context_full = []
        for context_i in context_list:
            context_full.append(' '.join([self._remove_single_word_newlines(result.text) for result in context_i]))
        logger.debug('\n'.join([f"\nContexto {i}: \n{r}\n{'-'*30}" for i, r in enumerate(context_full)]))

        extract = self.client.extract_data(
            system_prompt=self.prompts['system_prompt'],
            text_context_list=['\n'.join(context_full)],
            pre_prompt_extract=pergunta_dict['prompts']['extract_prompt'],
            prompt_extract="Transcreva a ementa exatamente como ela aparece no texto.\nEMENTA:\n",
            llm =  self.llm,
            llm_args = {
                'temperature': 0.0,
                }
        )
        refs = [ref.json() for ref in hybrid_matches[:3]]
        return extract.content[0].replace('\n', ' '), refs, context_full

    async def iterate_questions(self, q, collection_processo_id):
        total = len(self.perguntas)
        for i, pergunta_dict in self.perguntas.items():
            logger.debug(f"TASK: {pergunta_dict['task']}\nQUESTÃO:\n{pergunta_dict['prompts']['prompt_summary']}\n")
            dict_history = dict()
            if pergunta_dict['task'] == 'ementa':
                response, context, full_context = await self._perform_ementa_task(q, pergunta_dict, collection_processo_id)
                dict_history['response'] = response
                dict_history['context'] = context
                dict_history['context_full'] = full_context
                self.cfg[pergunta_dict['label']] = dict_history
                self.respostas_perguntas.append(f'{i} -    ' + response)
                logger.debug(f"\nResposta: \n{response}\n")
                q.client.contexto_processo[pergunta_dict['label']] = context
                continue
            
            check_exist, response, context, full_context = await self._perform_task(q, pergunta_dict, collection_processo_id)
            progress = int(((i)/total)*100)
            q.page["main_infos"].progress_perguntas.caption = '{}%'.format(progress)
            await q.page.save()
            if (i == 1) and (check_exist == False):
                if 'agravo' in q.client.doc_type_dict.keys(): response = 'Trata-se de agravo de recurso extraordinário. ' + response
                else: response = 'Trata-se de recurso extraordinário. ' + response
            
            dict_history['response'] = response
            dict_history['context'] = context
            dict_history['context_full'] = full_context
            self.cfg[pergunta_dict['label']] = dict_history
            self.respostas_perguntas.append(f'{i} - ' + response)
            logger.debug(f"\nResposta: \n{response}\n")
            q.client.contexto_processo[pergunta_dict['label']] = context
        return

    async def reduce_questions(self, q):
        is_english = q.client.language == 'eng'
        self.cfg['processo'] = f"""{q.client.process_selected}"""
        self.cfg['data'] = str(datetime.datetime.now())
        self.cfg['llm'] = self.llm

        await self.iterate_questions(q, q.client.collection_processo_id)
        final_summary = '\n\n'.join(self.respostas_perguntas)

        last_item_num = max(self.perguntas.keys()) + 1
        await get_status(q, 2)
        await q.page.save()
        final_summary = final_summary + f'\n\n{last_item_num} - É o relatório.'
        self.cfg['final_summary'] = {'response': final_summary, 'context': [], 'context_full': []}
        q.client.current_summary = final_summary
        await asyncio.sleep(2)
        await get_status(q, 3)
        # self._update_history(q)
        self._persist_chat(q, final_summary, user=False)
        final_summary = self._translate_pt_to_eng(final_summary) if is_english else final_summary
        return final_summary

    def _persist_chat(self, q, res, user=False):
        if user:
            res = 'USUÁRIO: \n' + res
        else:
            res = 'STFgpt: \n' + res
        q.client.current_chat = q.client.current_chat + res
    
    def _write_initial_prompt(self, q):
        doc_names = q.client.document_names.keys()
        doc_names = '\n'.join(doc_names)
        h_line = '-'*50
        init_prompt = q.client.texts['init_prompt'].format(q.client.process_selected)
        return init_prompt

    async def answer_question(self, q, question_prompt):
        import re
        is_english = q.client.language == 'eng'
        # question_prompt = self._translate_eng_to_pt(question_prompt) if is_english else question_prompt
        final_prompt = "De acordo com as informações fornecidas e o histórico da conversa abaixo: \n" + q.client.current_chat + '\n Responda a pergunta abaixo: \n\n' + question_prompt

        final_prompt_tokens = re.split('\s+', final_prompt)
        if len(final_prompt_tokens) > 3500:
            final_prompt = ' '.join(final_prompt_tokens[-3500:])

        context = self._search_match(q.client.collection_processo_id, question_prompt)
        refs = [ref.json() for ref in context[:3]]
        q.client.current_context = refs
        system_prompt = self.prompts['system_prompt_eng'] if is_english else self.prompts['system_prompt']
        logger.debug(f"\nPergunta: \n{question_prompt}\n")
        chat_args = {
            "system_prompt": system_prompt,
            "text_context_list": [result.text.replace('\n', ' ') for result in context[:2]],
            "question": final_prompt,
            "llm": self.llm,
            }
        response = self._answer_question(chat_args)
        self._persist_chat(q, question_prompt, user=True)
        return response



class HighlightDocs:
    def __init__(self, process_id):
        self.process_id = process_id
        self.root_path = './processo_highlighted'

    def clean_up(self):
        import shutil
        shutil.rmtree(self.root_path)
        return
    
    def delete_all_files(self):
        import os
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                os.remove(os.path.join(root, file))
        return

    def _create_polygon_annotation(self, page, selection):
        points = [(coord["x"], coord["y"]) for coord in selection["polygons"]]
        annot = page.add_polygon_annot(points)
        annot.set_colors(stroke=(1, 1, 1), fill=(1.0, 1.0, 0.0))
        annot.set_opacity(0.4)
        annot.update()
    
    def _process_pdf_with_annotations(self, q, markers: list):
        marker = json.loads(markers)
        doc = marker["name"]
        doc_path = self.root_path + f"/{doc}"
        logger.info('Opening the document')
        pdf_document = fitz.open(q.client.document_names[doc])
        logger.info('Getting the selections')
        selections = json.loads(marker["pages"])["selections"]
        pages = set([selection["page"] - 1 for selection in selections])
        logger.info('Creating the annotations')
        for selection in selections:
            page_number = selection["page"] - 1
            page = pdf_document.load_page(page_number)
            page.set_rotation(0)
            logger.info(f'Creating the annotation for page {page_number}')
            logger.debug(f'Selection: {selection}')
            self._create_polygon_annotation(page, selection)
        logger.info(f'Creating the new document')
        pages = [int(page) for page in pages]
        doc2 = fitz.open()
        logger.info(f'Inserting the pages: {pages}')
        doc2.insert_pdf(pdf_document, from_page=min(pages), to_page=max(pages))
        logger.info(f'Saving the highlighted document')
        # pdf_document.save(doc_path)
        doc2.save(doc_path)
        pdf_document.close()
        doc2.close()
        return marker["score"], doc_path
    
    def highlight_pdf(self, q, src_markers: list, index: int):
        import os
        logger.info(f'Selecting the markers')
        markers = src_markers[index]
        # logger.info(f'Creating new folder')
        # if not os.path.exists(self.root_path):
        #     os.mkdir(self.root_path)
        # else:
        #     self.clean_up()
        #     os.mkdir(self.root_path)
        score, doc_path = self._process_pdf_with_annotations(q, markers)
        return score, doc_path
    

