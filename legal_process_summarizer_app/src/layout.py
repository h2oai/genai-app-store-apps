from h2o_wave import Q, ui, data
import toml
import os
import hashlib
from .constants import *


text_heading = "<font size=4><b>{}</b></font>"

themes = [ui.theme(
        name='app-theme',
        primary='#FEC828', 
        text='#1B4F72',
        card='#FDFEFE',
        page='#D0D3D4',
        )]

async def layout(q: Q, zones_content: list = None):
    q.app.toml = toml.load("app.toml")
    zones = [
        ui.zone(name="zone_0", direction="row", size="12%"),
        ui.zone(name="zone_1", direction="row", size="80%", zones=zones_content),
        ui.zone(name="zone_2", direction="row", size="8%"),
    ]
    q.page["meta"] = ui.meta_card(
        box="",
        themes=themes,
        theme="app-theme",
        animate=True,
        stylesheet=ui.inline_stylesheet(get_style()),
        script=heap_analytics(
            userid=q.auth.subject,
            event_properties=f"{{"
            f"version: '{q.app.toml['App']['Version']}', "
            f"product: '{q.app.toml['App']['Title']}'"
            f"}}",
            ),
        layouts=[ui.layout(
            breakpoint="xl",
            width="95%",
            zones=zones
            )],
    )
    q.page["card_2"] = ui.footer_card(
        box="zone_2",
        caption=f"© 2024 powered by {COMPANY}GPT",
    )
    await q.page.save()


async def get_header_card(q):
    sec_image_resize = (SEC_IMAGE_DIM[0]*FACTOR_SEC_IMAGE, SEC_IMAGE_DIM[1]*FACTOR_SEC_IMAGE)
    sec_image = f'<center><img style="width:{sec_image_resize[0]}px;height:{sec_image_resize[1]}px;" src="{q.app.sec_image}"/></center>'
    languages_menu = ui.menu(
            label=q.client.language_flag,
            items=[
                ui.command(name='portuguese', label='Portuguese 🇧🇷'),
                ui.command(name='english', label='English 🇺🇸'),
            ])
    items = [ui.markup(sec_image), languages_menu]
    q.page["header"] = ui.header_card(
        box="zone_0",
        title=q.client.texts['title'],
        subtitle=q.client.texts['subtitle'],
        color='transparent',
        image=q.app.logo,
        items=items,
        secondary_items=get_sec_header_items(q)
    )


def get_sec_header_items(q, path: str = None):
    if path == 'highlight':
        return [
            ui.inline([
                ui.text('Process: **{}**'.format(q.client.process_selected)),
                ui.buttons([
                    ui.button(
                        name='home',
                        label='Home', primary=False,),
                    ui.button(
                        name='chat_page_button',
                        label=q.client.texts['header']['chat_page_button'], primary=True)
                ], justify='center')
            ], direction='column', align='center'
            )]
    elif path == 'chat':
        return [
            ui.inline([
                ui.text('Process: **{}**'.format(q.client.process_selected)),
                ui.button(
                    name='voltar',
                    label=q.client.texts['header']['voltar'], primary=False)
            ], direction='column', align='center'
            )]
    elif q.client.process_selected == None:
        return []
    else:
        return []
    
# -------------------------------

def get_style():
    factor = 0.18
    icon_dim = (LOGO_DIM[0]*factor, LOGO_DIM[1]*factor)
    style = """
div[data-test="home"] > div{
    display: flex;
    align-self: center;
    border-radius: 13px;
    justify-content: center;
    margin: auto;
}
div[data-test="zone_1_1_1"] > div{
    border-radius: 15px;
    margin-right: 5px;
    margin-bottom: 5px;
}
div[data-test="main_infos"] > div:nth-child(1) > div:nth-child(n+3):nth-child(-n+6){
    margin-top: 12px;
    margin-bottom: 12px;
}
div[data-test="zone_1_1_2"] > div{
    border-radius: 15px;
    margin-top: 5px;
    margin-right: 5px;
}
div[data-test="zone_1_2"] > div{
    border-top-left-radius: 15px;
    border-bottom-left-radius: 15px;
    margin-left: 5px;
    margin-right: 0px;
    border-right: 0.3px dashed #454545;
}
div[data-test="chat_sidebar"] > div{
    border-radius: 15px;
    margin-right: 5px;
}
div[data-test="chat_content"] > div{
    border-radius: 15px;
    margin-left: 5px;
}
div[data-test="zone_1_3"] > div{
    border-top-right-radius: 15px;
    border-bottom-right-radius: 15px;
    margin-left: 0px;
    margin-right: 5px;
    background-color: #FEF9E7;
}
button[data-test="referencias"]{
    border-radius: 30px;
    margin-top: 380px;
    margin-left: 0px;
    margin-right: 0px;
    color: #B7950B;
    background-color: transparent;
}
button[data-test="referencias"]:hover{
    background-color: #FEC828;
    border: 1px dashed #FEC828;
    color: #FEF9E7;
}
button[data-test="fechar_referencias"]{
    border-radius: 30px;
    margin-top: 380px;
    margin-left: 0px;
    margin-right: 0px;
    color: #B7950B;
    background-color: transparent;
}
button[data-test="fechar_referencias"]:hover{
    background-color: #FEC828;
    border: 1px dashed #FEC828;
    color: #FEF9E7;
}
div[data-test="zone_1_4"] > div{
    margin-left: 0px;
    margin-right: 0px;
    border-right: 0.3px dashed #454545;
}
div[data-test="selecao_processos"] > div{
    display: flex;
    align-items: center;
    background-color: rgba(253,254,254,0.05);
}
div[data-test="selecao_processos"] > div:nth-child(1) > div:nth-child(1){
    filter: drop-shadow(1px 1px 4px rgba(0,0,0,0.2));
}
div[data-test="selecao_processos"] > div:nth-child(1) > div:nth-child(2){
    margin-top: 20px;
    margin-bottom: 70px;
}
div[data-test="selecao_processos"] > div:nth-child(1) > div:nth-child(5){
    margin-top: 70px;
    margin-bottom: 70px;
}
div[data-test="header"] > div:nth-child(2) {
    filter: drop-shadow(1px 1px 1px rgba(0,0,0,0.3));
}
div[data-test="header"] > div:nth-child(3) {
    filter: drop-shadow(1px 1px 1px rgba(0,0,0,0.3));
}
div[data-test="header"] > div:nth-child(1) > div{
    font: small-caps bold large New Century Schoolbook;
    filter: drop-shadow(1px 1px 1px rgba(0,0,0,0.8));
}
button[data-test="chat_page_button"]{
  border-radius: 20px;
  background-color: #FEC828;
  border: 1px solid #FEC828;
  color: white;
  text-align: center;
  transition: all 0.5s ease;
#   margin-right: 24px;
  opacity: 0.8;
}
button[data-test="chat_page_button"]:after {
  content: "💡";
  position: absolute;
  opacity: 0;
  top: 2px;
  right: 3px;
  transition: 0.5s ease;
}
button[data-test="chat_page_button"]:hover{
  padding-right: 36px;
}
button[data-test="chat_page_button"]:hover:after {
  opacity: 1;
  right: 13px;
}
button[data-test="home"]{
  border-radius: 20px;
  background-color: transparent;
  border: 1px solid #FEC828;
  text-align: center;
  transition: all 0.5s ease;
}
button[data-test="home"]:after {
  content: "🏠";
  position: absolute;
  opacity: 0;
  top: 0px;
  right: 5px;
  transition: 0.5s ease;
}
button[data-test="home"]:hover{
  padding-right: 36px;
  background-color: transparent;
  border: 1px solid #FEC828;
}
button[data-test="home"]:hover:after {
  opacity: 1;
  right: 15px;
}
button[data-test="voltar"]{
  border-radius: 20px;
  background-color: transparent;
  border: 1px solid #FEC828;
  text-align: center;
  transition: all 0.5s ease;
}
button[data-test="voltar"]:after {
  content: "⬅";
  position: absolute;
  opacity: 0;
  top: 5px;
  right: 5px;
  transition: 0.5s ease;
}
button[data-test="voltar"]:hover{
  padding-right: 36px;
  background-color: transparent;
  border: 1px solid #FEC828;
}
button[data-test="voltar"]:hover:after {
  opacity: 1;
  right: 15px;
}
button[data-test="submit_novo_processo"]{
    background-color: transparent;
    border-radius: 20px;
    border: 1px solid #FEC828;
}
button[data-test="submit_novo_processo"]:hover{
    background-color: #FEC828;
    color: white;
}
button[data-test="submit_zip_file"]{
    background-color: transparent;
    border-radius: 20px;
    border: 1px solid #FEC828;
}
button[data-test="submit_zip_file"]:hover{
    background-color: #FEC828;
    color: white;
    opacity: 0.7;
}
button[data-test="resumo_botao"]{
    border-radius: 30px;
    margin-top: 30px;
}
button[data-test="previous_ref"]{
    border-radius: 30px;
    background-color: transparent;
}
button[data-test="previous_ref"]:hover{
    background-color: transparent;
    border: 1px solid #ECF0F1;
}
button[data-test="next_ref"]{
    border-radius: 30px;
    background-color: transparent;
}
button[data-test="next_ref"]:hover{
    background-color: transparent;
    border: 1px solid #ECF0F1;
}
button[data-test="previous_ref_chat"]{
    border-radius: 30px;
    background-color: transparent;
}
button[data-test="previous_ref_chat"]:hover{
    background-color: transparent;
    border: 1px solid #ECF0F1;
}
button[data-test="next_ref_chat"]{
    border-radius: 30px;
    background-color: transparent;
}
button[data-test="next_ref_chat"]:hover{
    background-color: transparent;
    border: 1px solid #ECF0F1;
}
button[data-test="submit_process"]{
    border-radius: 20px;
}
button[data-test="reset"]{
    background-color: transparent;
    border-radius: 20px;
    border: 1px solid #FEC828;
}
button[data-test="reset"]:hover{
    background-color: #FEC828;
    # color: white;
    opacity: 0.7;
}
button[data-test="download_pdf"]{
  border-radius: 30px;
  background-color: transparent;
  border: 1px solid #FEC828;
  text-align: center;
  transition: all 0.5s ease;
  filter: drop-shadow(1px 1px 1px rgba(0,0,0,0.5));
}
button[data-test="download_pdf"]:after {
  content: "📄";
  position: absolute;
  opacity: 0;
  top: 2px;
  right: 0px;
  transition: 0.5s ease;
}
button[data-test="download_pdf"]:hover{
  padding-right: 40px;
  background-color: transparent;
  border: 1px solid #FEC828;
}
button[data-test="download_pdf"]:hover:after {
  opacity: 1;
  right: 15px;
}
"""
    style += """
div[data-test="header"] > div:nth-child(1) > div:nth-child(1){""" + f"""
    width: {icon_dim[0]}px;
    height: {icon_dim[1]}px;
    filter: drop-shadow(1px 1px 1px rgba(0,0,0,0.3));
    padding: 0px;""" + '}'
    return style


# -------------------------------

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

