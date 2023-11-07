from h2ogpte import H2OGPTE
import logging
import os, glob
import requests
import datetime
import json

logging.basicConfig(level=logging.INFO)

class H2OGPTEClient:
    def __init__(self, address, api_key):
        self.address = address
        self.api_key = api_key
        self.client = H2OGPTE(address=self.address, api_key=self.api_key)

    def create_collection(self, name, description):
        logging.info(f'Creating collection {name}')
        collection_id = None
        recent_collections = self.client.list_recent_collections(0, 1000)
        for c in recent_collections:
            if c.name == name:
                collection_id = c.id
                logging.info(f'Collection {name} already exists')
                break

        if collection_id is None:
            collection_id = self.client.create_collection(
                name=name,
                description=description,
            )
            logging.info(f'Collection {name} created')
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
        logging.info(f"Num of colletions already created: {len(existing_collections)}")
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(existing_collections, json_file, indent=4)
        logging.info(f"Collection {collection_id} saved")
        return

    def drop_all_collections(self, collection_id = None):
        if collection_id:
            self.client.delete_collection(collection_id)
        else:
            while True:
                collections = self.client.list_recent_collections(0, 100)
                if len(collections) == 0:
                    break
                collection_ids = [c.id for c in collections]
                self.client.delete_collections(collection_ids)
        return     

    def drop_collections_no_temas(self):
        logging.info(f'Dropping all old collections created except temas_stf')
        json_file_path = "./collection_list.json"
        try:
            with open(json_file_path, "r") as json_file:
                existing_collections = json.load(json_file)
        except FileNotFoundError:
            existing_collections = []
        
        collections_h2ogpte = self.client.list_recent_collections(0, 100)
        collections_h2ogpte_ids = [c.id for c in collections_h2ogpte if c.name != 'temas_stf']
        for collection in existing_collections:
            collection_id = collection['collection_id']
            n_days = (datetime.datetime.now() - datetime.datetime.strptime(collection['creation_date'], '%Y-%m-%d %H:%M:%S.%f')).days
            if collection['collection_id'] in collections_h2ogpte_ids and n_days >= 1:
                self.drop_all_docs(collection['collection_id'])
                self.client.delete_collections([collection['collection_id']])
                existing_collections.remove(collection)
                logging.info(f'Collection {collection_id} deleted')

        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(existing_collections, json_file, indent=4)
        return

    def drop_all_docs(self, collection_id):
        logging.info(f'Dropping all docs from collection {collection_id}')
        while True:
            docs = self.client.list_documents_in_collection(collection_id, 0, 1000)
            if len(docs) == 0:
                break
            doc_ids = [d.id for d in docs]
            self.client.delete_documents_from_collection(collection_id, doc_ids)
            self.client.delete_documents(doc_ids)
        return

    def ingest_filepath(self, filepath, collection_id):
        filename = str(filepath).split('/')[-1]
        logging.info(f'Ingesting file {filename}')
        documents = self.client.list_documents_in_collection(collection_id, 0, 1000)
        document_ids = [d.id for d in documents if d.name == filename]
        if len(document_ids) == 0:
            with open(filepath, 'rb') as f:
                doc = self.client.upload(filename, f)
            self.client.ingest_uploads(collection_id, [doc])
            logging.info(f'File {filename} ingested')
        else:
            logging.info(f'File {filename} already ingested')

        chunks = self._get_collection_chunks(collection_id)
        return chunks
    
    def ingest_url(self, url, collection_id):
        filename = url.split("/")[-1]
        documents = self.client.list_documents_in_collection(collection_id, 0, 1000)
        document_ids = [d.id for d in documents if d.name == filename]
        if len(document_ids) == 0:
            self.client.ingest_website(collection_id, url)
            logging.info(f'File {filename} ingested')
        else:
            logging.info(f'File {filename} already ingested')
        
        chunks = self._get_collection_chunks(collection_id)
        return chunks
    
    def _get_collection_chunks(self, collection_id):
        chunk_sizes = 80
        while True:
            chunks_ids = list(range(1, int(chunk_sizes)))
            try:
                chunks = self.client.get_chunks(collection_id, chunks_ids)
                break
            except:
                chunk_sizes = int(chunk_sizes*0.9)
                print(f'chunk_sizes: {chunk_sizes}')

        chunks = [c.text for c in chunks]
        chunks = [text.replace('\n', ' ') for text in chunks]
        return chunks
    
    def ingest_file_folder(self, folder, collection_id):
        from tqdm import tqdm
        logging.info(f'Ingesting folder {folder}')
        filespaths = glob.glob(f'./{folder}/*.pdf')
        docs_to_upload = []
        documents = self.client.list_documents_in_collection(collection_id, 0, 1000)
        doc_names = [d.name for d in documents]
        logging.info('Uploading files')
        for filepath in tqdm(filespaths):
            filename = filepath.split('/')[-1]
            if filename not in doc_names:
                with open(filepath, 'rb') as f:
                    doc = self.client.upload(filename, f)
                docs_to_upload.append(doc)

        if len(docs_to_upload) > 0:
            logging.info('Ingesting files to H2OGPTe')
            self.client.ingest_uploads(collection_id, docs_to_upload)
        return


class QnAManager:
    def __init__(self, client, llm, collection_peticao_id, collection_stf_id):
        self.client = client.client
        self.llm = llm
        self.collection_peticao_id = collection_peticao_id
        self.collection_stf_id = collection_stf_id
        self.system_prompt = """Você é um assistente virtual chamado BrLawGPT.
Apenas responda as perguntas em português e jamais use outro idioma.
Responda as pergunta com informações fornecidas no contexto, não crie nenhuma informação.
Se não tiver informações suficientes para responder à sua pergunta, informe em português sobre as informações que estão faltando para fornecer uma resposta completa.
"""
        self.system_prompt_eng = """You are a virtual assistant called BrLawGPT.
Please answer in English.
Answer the question with information provided in the context, do not create any information.
If you do not have enough information to answer your question, inform in Portuguese about the information that is missing to provide a complete answer.
"""
    def _translate_pt_to_eng(self, text):
        logging.info(f'Translating text to English')
        logging.info(f'Text: {text}')
        chat_args = {
            "system_prompt": self.system_prompt_eng,
            "question": f"""{text}\n\nTranslate the text above to English.""",
            "llm": self.llm,
        }
        response = self._answer_question(chat_args)
        logging.info(f'Response: {response}')
        return response
    
    def _translate_eng_to_pt(self, text):
        logging.info(f'Translating text to Portuguese')
        logging.info(f'Text: {text}')
        chat_args = {
            "system_prompt": self.system_prompt,
            "question": f"""{text}\n\nApenas traduza o texto acima para o português brasileiro sem adicionar nenhuma informação.""",
            "llm": self.llm,
        }
        response = self._answer_question(chat_args)
        logging.info(f'Response: {response}')
        return response
    
    def _answer_question(self, chat_args):
        try:
            response = self.client.answer_question(**chat_args).content
        except:
            response = 'Not able to construct an answer at the moment. Please contact the app administrators.'
        return response
    
    def _summarize_content(self, chat_args):
        try:
            response = self.client.summarize_content(**chat_args).content
        except:
            response = 'Not able to construct an answer at the moment. Please contact the app administrators.'
        return response

    def _chat(self, question_prompt, summary, open_question, stf_check):
        chat_args = {
            "system_prompt": self.system_prompt,
            "question": question_prompt,
            "llm": self.llm,
            }
        if stf_check == True:
            logging.info(f'Finding Supreme Court Theme')
            response = self._get_tema(summary)
        elif open_question == True:
            logging.info(f'Open question')
            response = self._answer_question(chat_args)
        else:
            logging.info(f'Pesquisando na peticao inicial')
            prompt = f"""Responda apenas usando os trechos acima da petição inicial.\n\nPERGUNTA:{question_prompt} \n\nRESPOSTA:"""
            context = self._search_peticao(question_prompt)
            chat_args['text_context_list'] = context
            chat_args['question'] = prompt
            response = self._answer_question(chat_args)
        return response
        
    def _search_peticao(self, question_prompt):
        question_vectors = self.client.encode_for_retrieval([question_prompt])
        results = self.client.match_chunks(self.collection_peticao_id, question_vectors, [], 0, 5)
        results = [result.text for result in results]
        results = [result.replace('\n', ' ') for result in results]
        for result in results:
            print(result, flush=True)
        return results
    
    def _get_tema(self, summary):
        prompt_setter = f"""Usando apenas os fatos de uma petição inicial descritos abaixo, responda a pergunta.\n\nFATOS DA PETIÇÃO:\n{summary}"""
        prompt = f"""{prompt_setter}\n\nQuais são os temas do STF mais relacionados aos fatos da petição inicial? Escolha apenas os temas relacionados diretamente à petição inicial limitado em 3 temas e ignore o restante."""

        question_vectors = self.client.encode_for_retrieval([prompt])
        results = self.client.match_chunks(self.collection_stf_id, question_vectors, [], 0, 5)
        for result in results:
            print(result, flush=True)
        results = [result.text for result in results]
        results = [result.replace('\n', ' ') for result in results]
        chat_args = {
                    "system_prompt": self.system_prompt,
                    "text_context_list": ['\n'.join(results)],
                    "question": prompt,
                    "llm": self.llm,
                }
        response = self._answer_question(chat_args)
        return response
    
    def _get_full_summary(self, chunks):
        full_context = ['\n'.join(chunks)]
        size = len(full_context[0].split(' '))
        logging.info(f"Chunk Size: {size}")
        chat_args = {
                    "system_prompt": self.system_prompt,
                    "pre_prompt_summary":"Usando apenas os trechos do documento abaixo, faça um resumo que melhor descreva o assunto da petição inicial e os pedidos do autor. Não adicione nenhum fato não descrito no texto.\n",
                    "text_context_list": full_context,
                    "prompt_summary": "Descreva o assunto e os fatos descritos pelo autor da petição em um resumo em português brasileiro.",
                    "docs_token_handling":'split_or_merge',#"chunk",
                    "llm": self.llm,
                }
        final_summary = self._summarize_content(chat_args)
        return final_summary

    def _check_history(self, filename, json_file_path, sum_check, delete_old):
        check_exist = False
        res=''
        with open(json_file_path, "r") as json_file:
            existing_data = json.load(json_file)
        print("Num of histories: ", len(existing_data))
        for hist in existing_data:
            if hist['filename']==f"""{filename}""":
                if hist['user_question'].lower() in sum_check:
                    if delete_old:
                        existing_data.remove(hist)
                        check_exist = False
                        print("Num of histories after removal: ",len(existing_data))

                    if delete_old==False:
                        summary_task = False
                        print('Summary exists for this file, fetching from history.')
                        res = hist['llm_resp']
                        check_exist = True
                        break
        return check_exist, res

    def answer_question(self, q, question_prompt, pdfs=None, doc_chunks=[]):
        is_english = q.client.language == 'en'
        sum_check = ["dê-me um resumo", "resumo", "resuma", "resuma este documento", "resuma isto",
                    "dê-me um breve resumo", "resuma este pdf", "resuma este arquivo","faça um resumo da petição inicial",
                    "faça um resumo", "faça um resumo dos fatos descritos na petição inicial",
                    'gimme a summary', 'give me a summary', 'summarize this', 'summarize this pdf', 'summarize this file',
                    'summarize the facts described in the initial petition']
        
        stf_temas_check = ["tema do stf", "temas do stf", "tese do stf", "teses do stf", "tese do supremo", "teses do supremo",
                           "supreme court theme", "supreme court themes", "supreme court thesis", "supreme court theses", "brazilian supreme court"]
        stf_temas_check_func = lambda x: any([i in x.lower() for i in stf_temas_check])

        summary_task, delete_old, open_ques = False, False, False

        start_dir = "./"
        history_file = "history.json"
        json_file_path = None
        for root, dirs, files in os.walk(start_dir):
            if history_file in files:
                json_file_path = os.path.join(root, history_file)
                print("File found at:", json_file_path)
                break

        if question_prompt.lower()[-6:]==" --new":
            question_prompt = question_prompt.strip(" --new")
            delete_old = True
        if question_prompt.lower()[-5:]=="--new":
            question_prompt = question_prompt.strip("--new").strip(" ")
            delete_old = True
        if question_prompt.lower()[-7:]==" --open":
            question_prompt = question_prompt.strip(" --open")
            open_ques = True
        if question_prompt.lower()[-6:]=="--open":
            question_prompt = question_prompt.strip("--open").strip(" ")
            open_ques = True

        filename = pdfs[0]
        if question_prompt.lower() in sum_check:
            print(f'Summarizing file: {pdfs[0]}')
            check_exist, res = self._check_history(filename, json_file_path, sum_check, delete_old)
            if check_exist==False:
                res = self._get_full_summary(doc_chunks)
                if not res.startswith('Not able to construct an answer at the moment. Please contact the app administrators.'):
                    summary_task = True
            prmpt = question_prompt
            cfg = dict()
            cfg['filename'] = f"""{pdfs[0]}"""
            cfg['user_question'] = f"""{question_prompt}"""
            cfg['llm_resp'] = f"""{res.replace('"', "'")}"""
            cfg['llm_prompt'] = f"""{prmpt.replace('"', "'")}"""
            cfg['created'] = str(datetime.datetime.now())
            res = self._translate_pt_to_eng(res) if is_english else res
        elif stf_temas_check_func(question_prompt):
            print(f'Summarizing file: {pdfs[0]}')
            check_exist, summary = self._check_history(filename, json_file_path, sum_check, delete_old)
            if check_exist==False:
                summary = self._get_full_summary(doc_chunks)
                if not summary.startswith('Not able to construct an answer at the moment. Please contact the app administrators.'):
                    summary_task = True
            res = self._chat(question_prompt, open_question=open_ques, summary=summary, stf_check=True)
            res = self._translate_pt_to_eng(res) if is_english else res
            cfg = dict()
            cfg['filename'] = f"""{pdfs[0]}"""
            cfg['user_question'] = 'faça um resumo'
            cfg['llm_resp'] = f"""{summary.replace('"', "'")}"""
            cfg['llm_prompt'] = f"""{"faça um resumo".replace('"', "'")}"""
            cfg['created'] = str(datetime.datetime.now())
        else:
            summary = ''
            question_prompt = self._translate_eng_to_pt(question_prompt) if is_english else question_prompt
            res = self._chat(question_prompt, open_question=open_ques, summary=summary, stf_check=False)
            res = self._translate_pt_to_eng(res) if is_english else res

        if summary_task:
            try:
                print("Num of histories before adding new summary: ",len(existing_data))
                existing_data.append(cfg)
                with open(json_file_path, "w", encoding="utf-8") as json_file:
                    json.dump(existing_data, json_file, indent=4)
                print("Num of histories after adding new summary: ", len(existing_data))
            
            except:
                try:
                    with open(json_file_path, "r") as json_file:
                        existing_data = json.load(json_file)
                except FileNotFoundError:
                    existing_data = []
                
                existing_data.append(cfg)
                with open(json_file_path, "w", encoding="utf-8") as json_file:
                    json.dump(existing_data, json_file, indent=4)
        return res

