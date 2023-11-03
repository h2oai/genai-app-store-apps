from h2o_wave import Q, app, data, handle_on, main, on, site, ui
import pandas as pd


async def loading(q):
    dialog_text = q.client.texts['dialog']
    q.page['meta'].dialog = ui.dialog(title=dialog_text['title'], blocking=True, items=[
        ui.progress(label=dialog_text['label'], caption=dialog_text['caption'], name='progress'),
    ])
    await q.page.save()

async def loading_home(q):
    dialog_text = q.client.texts['dialog_home']
    q.page['meta'].dialog = ui.dialog(title=dialog_text['title'], blocking=True, items=[
        ui.progress(label=dialog_text['label'], caption=dialog_text['caption'], name='progress'),
    ])
    await q.page.save()
    
def ui_table_from_df(df: pd.DataFrame,
                     name: str,
                     sortables: list = None,
                     filterables: list = None,
                     searchables: list = None,
                     icons: dict = None,
                     progresses: dict = None,
                     tags: dict = None,
                     min_widths: dict = None,
                     max_widths: dict = None,
                     link_col: str = None,
                     multiple: bool = False,
                     groupable: bool = False,
                     downloadable: bool = False,
                     resettable: bool = False,
                     height: str = None,
                     checkbox_visibility: str = None) -> ui.table:

    if len(df) == 0:
        table = ui.table(
            name='name',
            columns=[ui.table_column(name='-', label='-', link=False)],
            rows=[ui.table_row(name='-', cells=[str('Nenhum dado encontrado!')])])
        return table

    if not sortables:
        sortables = []
    if not filterables:
        filterables = []
    if not searchables:
        searchables = []
    if not icons:
        icons = {}
    if not progresses:
        progresses = {}
    if not tags:
        tags = {}
    if not min_widths:
        min_widths = {}
    if not max_widths:
        max_widths = {}

    cell_types = {}
    for col in icons.keys():
        cell_types[col] = ui.icon_table_cell_type(color=icons[col]['color'])
    for col in progresses.keys():
        cell_types[col] = ui.progress_table_cell_type(
            color=progresses[col]['color'])
    for col in tags.keys():
        cell_types[col] = ui.tag_table_cell_type(name="tag_" + col,
                                                 tags=tags[col]['tags'])

    columns = [
        ui.table_column(
            name=str(x),
            label=str(x),
            sortable=True if x in sortables else False,
            filterable=True if x in filterables else False,
            searchable=True if x in searchables else False,
            cell_type=cell_types[x] if x in cell_types.keys() else None,
            cell_overflow='wrap',
            min_width=min_widths[x] if x in min_widths.keys() else None,
            max_width=max_widths[x] if x in max_widths.keys() else None,
            link=True if x == link_col else False,
        ) for x in df.columns.values
    ]

    table = ui.table(name=name,
                     columns=columns,
                     rows=[
                         ui.table_row(name=str(i),
                                      cells=[
                                          str(df[col].values[i])
                                          for col in df.columns.values
                                      ]) for i in range(df.shape[0])
                     ],
                     multiple=multiple,
                     groupable=groupable,
                     downloadable=downloadable,
                     resettable=resettable,
                     height=height,
                     checkbox_visibility=checkbox_visibility)
    return table


def get_body(q):
    questions_data = q.client.texts['questions_data']
    title = q.client.texts['table_header']
    subtitle = q.client.texts['table_subtitle']
    caption = f"""

| {title}...          |
|:--------------------------------------------------------| """ 
    for i in questions_data['Question']:
        caption += f"\n| {i} |"
    category = subtitle
    image = q.app.backgroud
    return caption, category, image


async def get_questions(q):
    text_heading = "<font size=4><b>{}</b></font>"
    data = q.client.texts['questions_data']
    table_name = q.client.texts['table_name']
    initial_petition = q.client.texts['initial_petition']
    df = pd.DataFrame(data)
    df.rename(columns={'Question': table_name}, inplace=True)
    print('q.client.path', q.client.path)
    q.client.remote_path, = await q.site.upload([q.client.path])
    print('q.client.remote_path', q.client.remote_path)
    min_widths = {table_name: '350px'}
    items = [
        ui_table_from_df(df, name='questions', sortables=[table_name], link_col=table_name, min_widths=min_widths, height= '250px'),
        ui.text(text_heading.format(initial_petition)),
        ui.text(f"""<object data="{q.client.remote_path}" type="application/pdf" width="100%" height="450px"></object>""")
        
    ]
    return items

