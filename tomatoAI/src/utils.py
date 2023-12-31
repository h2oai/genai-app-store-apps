import os
import hashlib

from h2o_wave import ui


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
            ui.choice(name="Aw/As - Wet and dry or savanna climate", label="Aw/As - Wet and dry or savanna climate")
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
            ui.choice(name="Csa - Hot-summer Mediterranean climate", label="Csa - Hot summer Mediterranean climate"),
            ui.choice(name="Csb - Warm-summer Mediterranean climate", label="Csb - Warm summer Mediterranean climate"),
            ui.choice(name="Cwa - Monsoon-influenced humid subtropical climate",
                      label="Cwa - Monsoon-influenced humid subtropical climate"),
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
                      label="Dwc - Subarctic or boreal climate with dry winters"),
            ui.choice(name="Dwd - Subarctic or boreal climate with extremely dry winters",
                      label="Dwd: Subarctic or boreal climate with extremely dry winters"),
            ui.choice(name="Dsa - Hot summer continental or hemiboreal climate with dry summers",
                      label="Dsa - Hot summer continental or hemiboreal climate with dry summers"),
            ui.choice(name="Dsb - Warm summer continental or hemiboreal climate with dry summers",
                      label="Dsb - Warm summer continental or hemiboreal climate with dry summers"),
            ui.choice(name="Dsc - Subarctic or boreal climate with dry summers",
                      label="Dsc - Subarctic or boreal climate with dry summers")
        ]
    elif climate_zone == "Polar":
        choices += [
            ui.choice(name="ET - Tundra climate", label="ET - Tundra climate"),
            ui.choice(name="EF - Ice cap or ice sheet climate", label="EF - Ice cap or ice sheet climate"),
        ]
    else:
        choices = []
    return choices


def get_vegetable_choices():
    choices = [
        ui.choice(name="Potato", label="Potato"),
        ui.choice(name="Tomato", label="Tomato"),
        ui.choice(name="Bell_pepper", label="Bell pepper"),
        ui.choice(name="Egg_plant", label="Egg plant"),
        ui.choice(name="Hot_pepper", label="Hot pepper"),
        ui.choice(name="Zucchini", label="Zucchini"),
        ui.choice(name="Cucumber", label="Cucumber"),
        ui.choice(name="Pumpkin", label="Pumpkin"),
        ui.choice(name="Watermelon", label="Watermelon"),
        ui.choice(name="Broccoli", label="Broccoli"),
        ui.choice(name="Cabbage", label="Cabbage"),
        ui.choice(name="Cauliflower", label="Cauliflower"),
        ui.choice(name="Kale", label="Kale"),
        ui.choice(name="Radish", label="Radish"),
        ui.choice(name="Peas", label="Peas"),
        ui.choice(name="Beans", label="Beans"),
        ui.choice(name="Lentils", label="Lentils"),
        ui.choice(name="Chickpeas", label="Chickpeas"),
        ui.choice(name="Soybeans", label="Soybeans"),
        ui.choice(name="Onions", label="Onions"),
        ui.choice(name="Garlic", label="Garlic"),
        ui.choice(name="Leek", label="Leek"),
        ui.choice(name="Shallot", label="Shallot"),
        ui.choice(name="Chives", label="Chives"),
        ui.choice(name="Lettuce", label="Lettuce"),
        ui.choice(name="Carrots", label="Carrots"),
        ui.choice(name="Beets", label="Beets"),
        ui.choice(name="Spinach", label="Spinach"),
        ui.choice(name="Marigold", label="Marigold"),
        ui.choice(name="Corn", label="Corn"),
    ]
    return choices
