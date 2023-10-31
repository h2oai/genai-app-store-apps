from loguru import logger
from h2o_wave import on, ui

import os
import hashlib


def clear_cards(q):
    for c in q.client.cards:
        del q.page[c]
    q.client.cards = []


@on()
async def close_dialog(q):
    logger.info("")
    q.page["meta"].dialog = None


async def long_process_dialog(q, title=None):
    logger.info("")
    if title is None:
        title = q.client.waiting_dialog
    q.page["meta"].dialog = ui.dialog(
        title=title,
        items=[ui.image(title="", path=q.app.load, width="550px"),],
        blocking=True
    )
    await q.page.save()
    q.page["meta"].dialog = None


def missing_required_variable_dialog(q, variable):
    logger.info("")

    if q.client[convert_title_to_variable_name(variable)] is None or q.client[convert_title_to_variable_name(variable)] == "":
        q.page["meta"].dialog = ui.dialog(
            title=f"Missing {variable}!",
            items=[
                ui.message_bar(type="error", text=f"{variable} is required for the next step."),
                ui.buttons(justify="end", items=[ui.button(name="close_dialog", label="Close", primary=True)])
            ]
        )
        return True
    else:
        return False


def convert_title_to_variable_name(title):
    logger.info("")
    return "_".join(word.replace(",", "").replace("&", "").lower() for word in title.split(" "))


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