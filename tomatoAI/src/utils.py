import os
import hashlib

from h2o_wave import ui, Q


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


def get_climate_subzone(climate_zone: str):
    choices = []
    if climate_zone == "Tropical":
        choices += [
            ui.choice(name="Af - Rainforest climate", label="Af - Rainforest climate"),
            ui.choice(name="Am - Monsoon climate", label="Am - Monsoon climate"),
            ui.choice(name="Af - Wet and dry or savanna climate", label="Af - Wet and dry or savanna climate")
        ]
    elif climate_zone == "Dry":
        choices += [
            ui.choice(name="BWh - Hot desert climate", label="BWh - Hot desert climate"),
            ui.choice(name="BWk - Cold desert climate", label="BWk - Cold desert climate"),
            ui.choice(name="BSh - Hot semi-arid climate", label="BSh - Hot semi-arid climate"),
            ui.choice(name="BSk - Cold semi-arid climate", label="BSk - Cold semi-arid climate")
        ]
    elif climate_zone == "Temperate":
        choices += [
            ui.choice(name="Cfa - Humid subtropical climate", label="Cfa - Humid subtropical climate"),
            ui.choice(name="Cfb - Oceanic or maritime climate", label="Cfb - Oceanic or maritime climate"),
            ui.choice(name="Cfc - Subpolar oceanic climate", label="Cfc - Subpolar oceanic climate"),
            ui.choice(name="Cfc - Subpolar oceanic climate", label="Cfc - Subpolar oceanic climate"),
            ui.choice(name="Cwa - Monsoon-influenced humid subtropical climate",
                      label="Cwa - Monsoon-influenced humid subtropical climate"),
            ui.choice(name="Cwb - Subtropical highland climate",
                      label="Cwb - Subtropical highland climate"),
        ]
    elif climate_zone == "Continental":
        choices += [
            ui.choice(name="Dfa - Hot summer continental or hemiboreal climate",
                      label="Dfa - Hot summer continental or hemiboreal climate"),
            ui.choice(name="Dfb - Warm summer continental or hemiboreal climate",
                      label="Dfb - Warm summer continental or hemiboreal climate"),
            ui.choice(name="Dfc - Subarctic or boreal climate",
                      label="Dfc - Subarctic or boreal climate"),
            ui.choice(name="Dwa - Hot summer continental or hemiboreal climate with dry winters",
                      label="Dwa - Hot summer continental or hemiboreal climate with dry winters"),
            ui.choice(name="Dwb - Warm summer continental or hemiboreal climate with dry winters",
                      label="Dwb - Warm summer continental or hemiboreal climate with dry winters"),
            ui.choice(name="Dwc - Subarctic or boreal climate with dry winters",
                      label="Dwc - Subarctic or boreal climate with dry winters")
        ]
    elif climate_zone == "Polar":
        choices += [
            ui.choice(name="ET - Tundra climate", label="ET - Tundra climate"),
            ui.choice(name="EF - Ice cap or ice sheet climate", label="EF - Ice cap or ice sheet climate"),
        ]
    else:
        choices = []
    return choices
