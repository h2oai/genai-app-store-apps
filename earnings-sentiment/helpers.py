import bs4 as bs
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly import io as pio
import requests
from io import StringIO



def plot_sentiment_stars(ratings_table):
    
    plot_data = []
    for _, row in ratings_table.iterrows():

        rating = int(row.Rating.strip())
        plot_data = plot_data + [{'Quarter': row.Quarter, 
                                  'Rating': i, 
                                  'Color': str(rating)} 
                                 for i in range(1, rating + 1)]


    plot_data = pd.DataFrame(plot_data).sort_values(by="Quarter")
    
    fig = px.scatter(plot_data, x="Quarter", y="Rating", color="Color", width=1000, height=250,
                    labels=dict(Rating="", Quarter=""),
                     color_discrete_map={
                        "1": "red",
                        "2": "orange",
                        "3": "yellow",
                        "4": "yellowgreen",
                        "5": "green"},
                    )

    fig.update_traces(
        marker=dict(size=30, symbol="star", line=dict(width=2, color="DarkSlateGrey")),
        selector=dict(mode="markers")
    )

    fig.update_yaxes(showticklabels=False, showgrid=False, )
    fig.update_xaxes(showgrid=False)
    fig.update_layout(showlegend=False,
                      margin=dict(l=10, r=10, t=10, b=10),
                      paper_bgcolor='rgb(255, 255, 255)',
                      plot_bgcolor='rgb(255, 255, 255)',
                     )
    
    
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)
    
    return html


def plot_gauge(sentiment):
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 4,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {'axis': {'range': [1, 5]}},
        title = {'text': "Overall Rating"}))

    fig.update_traces(
        marker=dict(size=30, symbol="star", line=dict(width=2, color="DarkSlateGrey")),
        selector=dict(mode="markers")
    )

    fig.update_yaxes(showticklabels=False, showgrid=False, )
    fig.update_xaxes(showgrid=False)
    fig.update_layout(showlegend=False, 
                      margin=dict(l=10, r=10, t=10, b=10),
                      paper_bgcolor='rgb(255, 255, 255)',
                      plot_bgcolor='rgb(255, 255, 255)',
                     )
    
    
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)
    
    return html


def read_markdown(md):
    md_pd = pd.read_csv(StringIO(md),  sep='|').dropna(axis=1, how='all').iloc[1:]

    return md_pd


def get_ratings_table(transcripts):
    ratings_table = []
    for v in transcripts.values():
        ratings_table = ratings_table + [read_markdown(v.get('ratings_table'))]
    ratings_table = pd.concat(ratings_table)
    ratings_table['Quarter'] = list(transcripts.keys())
    ratings_table = ratings_table.rename(columns={i: i.strip() for i in ratings_table.columns})

    ratings_table = ratings_table[['Quarter', 'Rating', 'Reason for Rating']]

    return ratings_table


def get_close_price():

    df = pd.read_csv("./static/daily_stock_price.csv")
    df['Date'] = pd.to_datetime(df.Date)
    df['Quarter'] = pd.PeriodIndex(df.Date, freq='Q')
    df['Quarter'] = df.Quarter.astype(str).str.replace("Q", " Q")

    agg_df = df.groupby("Quarter")['Close'].mean().reset_index()

    return agg_df



def get_num_stats(df, num_col, target_col):
    
    agg_data = df.groupby(target_col).agg({
        num_col: ['min', 
                  lambda x: x.quantile(0.25), 
                  lambda x: x.quantile(0.5), 
                  lambda x: x.quantile(0.75),
                 'max']})
    
    agg_data = agg_data.reset_index()
    agg_data.columns = list(map(''.join, agg_data.columns.values))
    
    agg_data.columns = [target_col] + ['low', 'q1', 'q2', 'q3', 'high']
    
    return agg_data


def get_speakers(url, company):
    url_link = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    file = bs.BeautifulSoup(url_link.text, "lxml")
    
    out = {}
    for p in file.select('p'):
        previous_h2 = p.find_previous('h2')
        if previous_h2 is None:
            h2_text = "None"
        else:
            h2_text = previous_h2.text
            
        if 'Call participants' in h2_text:
            out.setdefault(h2_text, []).append(p.text)
            
            
    speakers = out.get(list(out.keys())[0])
    
    results = []
    for i in speakers:
        res = i.split(" -- ")
        if len(res) == 2:
            results = results + [{'speaker': res[0], 'company': company, 'title': res[1]}]
        elif len(res) == 3:
            results = results + [{'speaker': res[0], 'company': res[1], 'title': res[2]}]
    
    results = pd.DataFrame(results)
    results['image'] = 'BLAH'
    results.iloc[results.speaker == "Raj Subramaniam", -1] = 'https://www.fedex.com/content/dam/fedex/us-united-states/about-us/images/2023/Raj_Circle_Headshot_100KB.jpg'
    results.iloc[results.speaker == "John Dietrich", -1] = 'https://www.fedex.com/content/dam/fedex/us-united-states/About/upload/John_Dietrich_Headshot_100KB_3.jpg'
    results.iloc[results.speaker == "Brie Carere", -1] = 'https://www.fedex.com/content/dam/fedex/us-united-states/About/upload/Brie_Carere_Circle_Headshot_2_100KB.jpg'

    return results
    

def get_speaker_stats(url, chunks, company):
    speaker_stats = []
    for v in chunks.values():
        if (v.get('defensiveness') is not None) & (v.get('sentiment') is not None):
            speaker_stats = speaker_stats + [{'speaker': v.get('speaker').split(" -- ")[0], 
                                              'word_count': len(v.get('text').split()),
                                              'defensiveness': float(v.get('defensiveness').get('Rating')),
                                              'sentiment': float(v.get('sentiment').get('Rating'))
                                             }]

    speaker_stats = pd.DataFrame(speaker_stats)
    speaker_stats = speaker_stats.groupby('speaker').agg(
        {'word_count': "sum", 
         'defensiveness': "mean", 
         'sentiment': "mean"}
    ).reset_index()

    speakers = get_speakers(url, company)
    speakers = speakers.merge(speaker_stats, how='left', on=['speaker'])
    
    return speakers

def sentiment_icon(rating):
        if rating >= 4:
            return "Emoji2"
        elif rating >= 3:
            return "EmojiNeutral"
        else:
            return "Sad"
        
def sentiment_color(rating):
    if rating >= 4:
        return "$green"
    elif rating >= 3:
        return "$orange"
    else:
        return "$red"
    
def sentiment_text(rating):
    if rating == 5:
        return "Very Positive"
    elif rating == 4:
        return "Moderately Positive"
    elif rating == 3:
        return "Neutral"
    elif rating == 2:
        return "Moderately Negative"
    else:
        return "Very Negative"
    
def defense_icon(rating):
    if rating >= 3:
        return "WarningSolid"
    elif rating >= 2:
        return "Warning"
    else:
        return "CirclePlus"

def defense_color(rating):
    if rating >= 3:
        return "$red"
    elif rating >= 2:
        return "$orange"
    else:
        return "$green"
    
def defense_text(rating):
    if rating == 3:
        return "Very Defensive"
    elif rating == 2:
        return "Somewhat Defensive"
    else:
        return "Not Defensive"