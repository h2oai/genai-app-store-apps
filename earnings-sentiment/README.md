# Earnings Sentiment

The goal of this application is to showcase how H2O Gen AI can be used to analyze earnings calls.  

The application is currently hardcoded to showcase the results from the [FEDEX Earnings Call of 2024 Q1](https://www.fool.com/earnings/call-transcripts/2023/09/20/fedex-fdx-q1-2024-earnings-call-transcript/).

If you wish to run this on a different earnings call, review the data_prep.ipynb notebook to see how the ./static/chunked_transcript.json and ./static/all_transcripts.json data was created.

## Running the app

Make sure you have activated a Python virtual environment with `h2o-wave` installed.

If you haven't created a python env yet, simply run the following command (assuming Python 3.7 is installed properly).

For MacOS / Linux:

```sh
python3 -m venv venv
source venv/bin/activate
pip install h2o-wave
```

For Windows:

```sh
python3 -m venv venv
venv\Scripts\activate
pip install h2o-wave
```

Once the virtual environment is setup and active, run:

```sh
wave run app.py
```

Which will start a Wave app at <http://localhost:10101>.
