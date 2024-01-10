from loguru import logger
from h2o_wave import ui

import os


async def long_process_dialog(q):
    logger.info("")

    q.page["meta"].dialog = ui.dialog(
        title=q.client.waiting_dialog,
        items=[ui.image(title="", path=q.app.load, width="550px"),],
        blocking=True
    )
    await q.page.save()
    q.page["meta"].dialog = None


def heap_analytics() -> ui.inline_script:

    if "HEAP_ID" not in os.environ:
        return
    heap_id = os.getenv("HEAP_ID")
    script = f"""
window.heap=window.heap||[],heap.load=function(e,t){{window.heap.appid=e,window.heap.config=t=t||{{}};var r=document.createElement("script");r.type="text/javascript",r.async=!0,r.src="https://cdn.heapanalytics.com/js/heap-"+e+".js";var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(r,a);for(var n=function(e){{return function(){{heap.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}},p=["addEventProperties","addUserProperties","clearEventProperties","identify","resetIdentity","removeEventProperty","setEventProperties","track","unsetEventProperty"],o=0;o<p.length;o++)heap[p[o]]=n(p[o])}};
heap.load("{heap_id}"); 
    """

    return ui.inline_script(content=script)