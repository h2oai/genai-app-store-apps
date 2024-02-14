from h2o_wave import ui
from src.gradio import ask_query
import asyncio
import pandas as pd
import json 
import validators
import wget
# import fitz
import os
import hashlib
from h2o_wave import Q
from loguru import logger

def format_sources(src_list: list):
    result = ""
    for item in src_list:
        result += f"• {item}\n"
    if result != "":
        result = "\n\n<b>Sources:</b>\n" + result

    return result


def format_docs_table(docs_list: list):
    ind = 0
    result = []
    for item in docs_list:
        result.append(
            ui.table_row(name=f'{ind}', cells=[f'{ind}', f"{item.name}", f"{item.type}", f"{item.status}"])
        )
        ind += 1

    return result

async def get_rfi_response(q:Q, file_path: str, model_host: str, host_api: str, langchain_mode: str):
    ind = 0
    result = []
    columns= []
    rows=[]
    df = None

    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    
    # for q in df['Question'].values:
    # df[["Response", "References"]] = df['Question'].apply(lambda x: ask_query(x, model_client, chat_session_id), result_type='expand')
    references = []
    responses = []
    for query in df['Question'].values:
        
        res, ref, _ = await q.run(ask_query, model_host=model_host, 
                                    host_api=host_api, 
                                    langchain_mode=langchain_mode,
                                    instruction=query)

        responses.append(res)
        references.append(ref)
    
    df["Response"] = responses
    df["References"] = references
    # Add Review Status
    df["Review Status"] = ["PENDING"]*len(df)

    if df is not None:
        for col in df.columns:
            if col == "Question":
                columns.append(ui.table_column(name=f'{col}', label=f'{col}', sortable=True, link=True, searchable=True, 
                                               min_width='450px', cell_overflow="wrap"))
            elif col == "References":
                columns.append(ui.table_column(name=f'{col}', label=f'{col}', sortable=True, link=False, searchable=True, 
                                               min_width='550px', cell_overflow="wrap", cell_type=ui.markdown_table_cell_type(target='_blank')))
            elif col == "Review Status":
                columns.append(ui.table_column(name='review', label='Review Status', cell_type=ui.tag_table_cell_type(name='tags', tags=[
                        ui.tag(label='PENDING', color='#D2E3F8', label_color='#053975'),
                        ui.tag(label='DONE', color='$mint'),
                        ]))
                    )
            else:
                columns.append(ui.table_column(name=f'{col}', label=f'{col}', sortable=True, link=False, searchable=True, 
                                               min_width='550px', cell_overflow="wrap"))
        
        for i, row in df.iterrows():
            _tmp = row.values.tolist()
            rows.append(ui.table_row(name=str(i), cells=_tmp))
    
    return columns, rows, df

def edit_rfi(df: pd.DataFrame, idx: int):
    query = df.loc[int(idx), 'Question']
    response = df.loc[int(idx), 'Response']
    return query, response

def update_rfi(df: pd.DataFrame, idx: int, updated_res: str):
    review_idx = int(idx)
    df.at[review_idx, 'Response'] = updated_res
    df.at[review_idx, 'Review Status'] = 'DONE'
    
    rows = []
    for i, row in df.iterrows():
        _tmp = row.values.tolist()
        if review_idx == i:
            _tmp[-1] = 'DONE'

        rows.append(ui.table_row(name=str(i), cells=_tmp))
    
    return rows

# def highlight_pdf(file_path: str, src_markers: list, chat_message_id: str):
#     markers = []

#     for ref in src_markers:
#         markers.append(ref.json())
    
#     _process_pdf_with_annotations(file_path, markers, chat_message_id)

# def _create_polygon_annotation(page, selection):
#     points = [(coord["x"], coord["y"]) for coord in selection["polygons"]]
#     annot = page.add_polygon_annot(points)
#     annot.set_colors(stroke=(1, 1, 1), fill=(1.0, 1.0, 0.0))
#     annot.set_opacity(0.4)
#     annot.update()

# def _process_pdf_with_annotations(file_path, markers: list, doc_id: str):
#     for i, marker in enumerate(markers):
#         pdf_document = fitz.open(file_path)
#         marker = json.loads(marker)
#         selections = json.loads(marker["pages"])["selections"]
#         for selection in selections:
#             page_number = selection["page"] - 1
#             page = pdf_document.load_page(page_number)
#             page.set_rotation(0)
#             _create_polygon_annotation(page, selection)
#         pdf_document.save(f"{doc_id}_{i}.pdf")
#     pdf_document.close()


def heap_analytics(userid, event_properties=None) -> ui.inline_script:

    if "HEAP_ID" not in os.environ:
        return
    heap_id = os.getenv("HEAP_ID")
    script = f"""
window.heap=window.heap||[],heap.load=function(e,t){{window.heap.appid=e,window.heap.config=t=t||{{}};var r=document.createElement("script");r.type="text/javascript",r.async=!0,r.src="https://cdn.heapanalytics.com/js/heap-"+e+".js";var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(r,a);for(var n=function(e){{return function(){{heap.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}},p=["addEventProperties","addUserProperties","clearEventProperties","identify","resetIdentity","removeEventProperty","setEventProperties","track","unsetEventProperty"],o=0;o<p.length;o++)heap[p[o]]=n(p[o])}};
heap.load("{heap_id}"); 
    """

    if userid is not None:  # is OIDC Enabled? we do not want to identify all non-logged in users as "none"
        identity = hashlib.sha256(userid.encode()).hexdigest()
        script += f"heap.identify('{identity}');"

    if event_properties is not None:
        script += f"heap.addEventProperties({event_properties})"

    return ui.inline_script(content=script)

def validate_url(url):
    if validators.url(url):
        return True 
    else:
        return False

def download_and_read(url, output_path):
    # Check if the URL is valid
    if not validate_url(url):
        logger.debug("Invalid URL.")
        return None
    
    # Check if the file is a CSV or Excel
    if not url.strip().lower().endswith(('.csv', '.xlsx')):
        logger.debug("File is not a CSV or Excel file.")
        return None
    elif url.strip().lower().endswith('.csv'):
        file_type = '.csv'
    else:
        file_type = '.xlsx'

    # Download the file using wget
    try:
        filename = wget.download(url, out=f"{output_path}")
        return filename
    except Exception as e:
        logger.debug("Error downloading the file:", e)
        return None
