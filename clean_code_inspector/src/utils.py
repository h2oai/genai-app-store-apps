import os
import hashlib

from h2o_wave import ui
from typing import List


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


def get_method_level_rules() -> List[ui.choice]:
    choices = [
        ui.choice(name="Single Responsibility Principle (SRP)", label="Single Responsibility Principle (SRP)"),
        ui.choice(name="Descriptive Naming", label="Descriptive Naming"),
        ui.choice(name="Method length", label="Method length"),
        ui.choice(name="Method parameters", label="Method parameters"),
        ui.choice(name="Error handling", label="Error handling"),
    ]
    return choices


def get_class_level_rules() -> List[ui.choice]:
    choices = [
        ui.choice(name="Class naming", label="Class naming"),
        ui.choice(name="Class size", label="Class size"),
        ui.choice(name="Encapsulation", label="Encapsulation"),
        ui.choice(name="Inheritance", label="Inheritance"),
        ui.choice(name="Docstrings", label="Docstrings")
    ]
    return choices


def get_concatenated_str(list_of_str: List[str]) -> str:
    if len(list_of_str) > 0:
        concatenation = list_of_str[0]
        for n in range(1, len(list_of_str)):
            concatenation += ", "
            concatenation += list_of_str[n]
    else:
        concatenation = None
    return concatenation


def get_code_file(filename: str):
    with open(f"static/{filename}", 'r') as file:
        code_example = file.read()
    return code_example


def get_example_code_choices() -> List[ui.choice]:
    choices = [
        ui.choice(name="bad_quality_python_code.txt", label="bad_quality_python_code.txt"),
        ui.choice(name="bad_quality_java_code.txt", label="bad_quality_java_code.txt"),
    ]
    return choices
