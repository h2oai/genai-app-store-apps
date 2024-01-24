from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage
import logging
import os, glob
import asyncio
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
        return
    
    def ingest_url(self, url, collection_id):
        filename = url.split("/")[-1]
        documents = self.client.list_documents_in_collection(collection_id, 0, 1000)
        document_ids = [d.id for d in documents if d.name == filename]
        if len(document_ids) == 0:
            self.client.ingest_website(collection_id, url)
            logging.info(f'File {filename} ingested')
        else:
            logging.info(f'File {filename} already ingested')
        return
    
    def _get_collection_chunks(self, collection_id):
        chunk_sizes = 80
        while True:
            chunks_ids = list(range(1, int(chunk_sizes)))
            try:
                chunks = self.client.get_chunks(collection_id, chunks_ids)
                break
            except:
                chunk_sizes = int(chunk_sizes*0.9)

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
    def __init__(self, client, llm, collection_peticao_id, collection_stf_id, language):
        from .prompts import prompts_pt, prompts_eng
        self.client = client.client
        self.llm = llm
        self.collection_peticao_id = collection_peticao_id
        self.collection_stf_id = collection_stf_id
        self.prompts = prompts_pt if language == 'ptbr' else prompts_eng
        self.language = language
        self.json_file_path = "./history.json"
    
    def _summarize_content(self, summarize_args):
        try:
            response = self.client.summarize_document(**summarize_args).content
        except Exception as e:
            logging.warning(f'Error: {e}')
            response = 'Not able to construct an answer at the moment. Please contact the app administrators.'
        return response

    async def _chat(self, q, question_prompt, open_question, stf_check):
        if stf_check == True:
            logging.info(f'Finding Supreme Court Theme')
            response = await self.stream_answer(q, question_prompt, rag_type="rag", stf_check=True)
        elif open_question == True:
            logging.info(f'Open question')
            response = await self.stream_answer(q, question_prompt, rag_type="llm_only", stf_check=False)
        else:
            logging.info(f'Searching for answer in the petition')
            response = await self.stream_answer(q, question_prompt, rag_type="rag", stf_check=False)
        return response
    
    def _get_full_summary(self, collection_id):
        logging.info('Summarizing task')
        documents = self.client.list_documents_in_collection(collection_id, offset=0, limit=99)
        doc = documents[0]
        summarize_args = {
                    "system_prompt": self.prompts['system_prompt'],
                    "pre_prompt_summary": self.prompts['pre_prompt_summary'],
                    "prompt_summary": self.prompts['prompt_summary'],
                    "sampling_strategy": "first+last",
                    "llm": self.llm,
                    "document_id": doc.id,
                    "max_num_chunks": 20,
                }
        final_summary = self._summarize_content(summarize_args)
        return final_summary

    def _check_history(self, filename, delete_old):
        check_exist = False
        res=''
        with open(self.json_file_path, "r") as json_file:
            existing_data = json.load(json_file)
        for hist in existing_data:
            if hist['filename']==f"""{filename}""" and hist['language']==self.language:
                if delete_old:
                    existing_data.remove(hist)
                    check_exist = False

                if delete_old==False:
                    logging.info('Summary exists for this file, fetching from history...')
                    res = hist['summary']
                    check_exist = True
                    break
        return check_exist, res
    
    def chat_session_stream(self, q, prompt, rag_type="rag", stf_check=False):
        """
        Send the user's message to the LLM and save the response
        """
        def stream_response(message):
            """
            This function is called by the blocking H2OGPTE function periodically
            """
            q.client.chatbot_interaction.update_response(message, q)

        collection = self.collection_peticao_id
        if stf_check == True: collection = self.collection_stf_id
        chat_session_id = self.client.create_chat_session(collection)
        args = {
            "system_prompt": self.prompts['system_prompt'],
            "message": prompt,
            "timeout": 60,
            "callback": stream_response,
            "llm": self.llm,
            'rag_config':{"rag_type": rag_type}
            }
        with self.client.connect(chat_session_id) as session:
            session.query(**args)
        self.client.delete_chat_sessions([chat_session_id])

    async def stream_updates_to_ui(self, q, chatbot_name):
        while q.client.chatbot_interaction.responding:
            q.page[chatbot_name].data[-1] = [q.client.chatbot_interaction.content_to_show, False]
            await q.page.save()
            await q.sleep(0.1)

        q.page[chatbot_name].data[-1] = [q.client.chatbot_interaction.content_to_show, False]
        await q.page.save()

    async def stream_answer(self, q, question_prompt, rag_type="rag", stf_check=False):
        q.client.chatbot_interaction = ChatBotInteraction(user_message=question_prompt, q=q)
        q.page['card_1'].data += [q.client.chatbot_interaction.content_to_show, False]
        try:
            update_ui = asyncio.ensure_future(self.stream_updates_to_ui(q, 'card_1'))
            await q.run(self.chat_session_stream, q, question_prompt, rag_type, stf_check)
            await update_ui
            response = q.client.chatbot_interaction.content_to_show
            return response
        except Exception as e:
            logging.warning(f'Error: {e}')
            update_ui.cancel()
            response = 'Not able to construct an answer at the moment. Please contact the app administrators.'
            q.page['card_1'].data[-1] = [response, False]
            await q.page.save()
            return response

    async def answer_question(self, q, question_prompt, filename):
        from .prompts import sum_check, stf_temas_check
        stf_temas_check_func = lambda x: any([i in x.lower() for i in stf_temas_check])
        sum_check_func = lambda x: any([i in x.lower() for i in sum_check])
        summary_task, delete_old, open_ques = False, False, False
        if question_prompt.lower()[-5:]=="--new":
            question_prompt = question_prompt.strip("--new").strip(" ")
            delete_old = True
        if question_prompt.lower()[-6:]=="--open":
            question_prompt = question_prompt.strip("--open").strip(" ")
            open_ques = True

        cfg = dict()
        cfg['filename'] = str(filename)
        cfg['language'] = self.language
        cfg['created'] = str(datetime.datetime.now())
        if sum_check_func(question_prompt) and not stf_temas_check_func(question_prompt):
            q.page['card_1'].data += ["<img src='{}' height='40px'/>".format(q.app.loader), False]
            await q.page.save()
            check_exist, res = self._check_history(filename, delete_old)
            if check_exist==False:
                res = self._get_full_summary(self.collection_peticao_id)
                if not res.startswith('Not able to construct an answer at the moment.'):
                    summary_task = True
            cfg['summary'] = res.replace('"', "'")
            q.page['card_1'].data[-1] = [res, False]
            await q.page.save()
        elif stf_temas_check_func(question_prompt):
            check_exist, summary = self._check_history(filename, delete_old)
            if check_exist==False:
                summary = self._get_full_summary(self.collection_peticao_id)
                if not summary.startswith('Not able to construct an answer at the moment.'):
                    summary_task = True
            question_prompt = self.prompts['stf_tema_prompt'].format(summary)
            res = await self._chat(q, question_prompt, open_question=open_ques, stf_check=True)
            cfg['summary'] = summary.replace('"', "'")
        else:
            question_prompt = self.prompts['peticao_prompt'].format(question_prompt)
            res = await self._chat(q, question_prompt, open_question=open_ques, stf_check=False)

        if summary_task:
            with open(self.json_file_path, "r") as json_file:
                existing_data = json.load(json_file)
            existing_data.append(cfg)
            logging.warning(f"cfg: {cfg}")
            with open(self.json_file_path, "w", encoding="utf-8") as json_file:
                json.dump(existing_data, json_file, indent=4)
        return res



class ChatBotInteraction:
    def __init__(self, user_message, q) -> None:
        self.user_message = user_message
        self.responding = True
        self.llm_response = ""
        self.content_to_show = "<img src='{}' height='40px'/>".format(q.app.loader)

    def update_response(self, message, q):
        if isinstance(message, ChatMessage):
            self.content_to_show = message.content
            self.responding = False
        elif isinstance(message, PartialChatMessage):
            if message.content not in ["#### No RAG (LLM only):\n", "#### LLM Only (no RAG):\n"]:
                self.llm_response += message.content
                self.content_to_show = self.llm_response