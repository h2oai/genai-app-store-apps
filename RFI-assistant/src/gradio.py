import ast
import os
import traceback
from enum import Enum
from typing import List, Union
from loguru import logger
import json

from h2o_wave import main, app, Q, ui, data
from h2ogpte import H2OGPTE
asserts = True


def get_client(host:str, api_key:str = None):
    logger.debug(f"The host URL is {host}")
    client = H2OGPTE(address=host, api_key=api_key)
    return client

def get_collection_id(model_client: H2OGPTE, langchain_mode: str = "H2O_DEMO_RFI", collection_id=None):
    if collection_id:
        try:
            model_client.get_collection(collection_id)
            return collection_id
        except:
            logger.debug(f"Collection ID {collection_id} does not exist, create a new one!")

    collection_id = None

    res = model_client.list_recent_collections(0, 50000)
    for collection in res:
        if collection.name == langchain_mode:
            collection_id = collection.id
            break
    
    if collection_id is None:
        collection_id = model_client.create_collection(name=langchain_mode, description='Created the collection for H2O RFI App')
        upload_default_docs(model_client._address, model_client._api_key, collection_id)
    return collection_id

def get_sources(model_host: str = None, host_api: str = None, langchain_mode: str = "H2O_DEMO_RFI"):
    sources = []
    model_client = get_client(host=model_host, api_key=host_api)
    collection_id = get_collection_id(model_client, langchain_mode)
    
    if collection_id:
        try:
            sources = model_client.list_documents_in_collection(collection_id, 0, 500)
        except:
            pass
    
    return sources

def get_chat_session(model_client: H2OGPTE = None, collection_id: str = None):
    res = model_client.create_chat_session(collection_id)
    return res

def ask_query(
          model_host: str,
          host_api: str,
          langchain_mode: str,
          instruction: str = None,
          timeout: float = 9000) -> str:
    """
    Query using H2OGPTE Collection
    """
    model_client = get_client(host=model_host, api_key=host_api)
    collection_id = get_collection_id(model_client, langchain_mode)
    chat_session_id = get_chat_session(model_client, collection_id)

    try:
        with model_client.connect(chat_session_id) as session:
            reply = session.query(instruction, timeout=timeout)
            response = reply.content
            references, raw_references = get_chat_sources(model_host, host_api=host_api, message_id=reply.id)
        return response, references, raw_references
    except Exception as e:
        logger.debug(f"Exception occured while querying Question: {instruction}, here is the exception {e}")
        return "None"

def get_chat_sources(model_host: str,
                    host_api: str,
                    message_id: str = None):
    model_client = get_client(host=model_host, api_key=host_api)
    sources = model_client.list_chat_message_references(message_id)
    result = ""

    for src in sources[:15]:
        pages = set()
        selections = json.loads(src.pages)["selections"]
        for selection in selections:
            pages.add(selection["page"])
        result += f"• {src.document_name} Pages: {list(pages)} - Score: {round(float(src.score), 2)}<br />"
    if result != "":
        result = "<br /><br /><b>References: </b><br />" + result

    return result, sources

def upload_data(model_host: str, 
                host_api: str,
                file: Union[List[str], str] = None,
                url: str = None,
                collection_id: str = None):
    # try:
    model_client = get_client(host=model_host, api_key=host_api)
    if url:
        res = model_client.ingest_website(collection_id=collection_id, url = url)
    else:
        logger.debug(f"The path to the file is {file}")
        file_name = file.split("/")[-1]
        with open(file, 'rb') as f:
            user_file = model_client.upload(f'{file_name}', f)
        
        res = model_client.ingest_uploads(collection_id, [user_file])
    
    if len(res.errors) == 0:
        return True
    else:
        return False

def upload_default_docs(model_host: str, host_api: str, collection_id: str):
    try:
        with open('./static/demo/default_docs.json') as f:
            def_urls = json.load(f)
            for url in def_urls["ingest_docs"]:
                res = upload_data(model_host= model_host, 
                            host_api=host_api, 
                            url=url, 
                            collection_id= collection_id)
                if res is False:
                    logger.debug(f"Error occured during default file upload of: {url}")
    except Exception as e:
        logger.debug(f"Error occured during default file upload: {e}")