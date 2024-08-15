# Automatic Slideshow Generator

Wave goodbye to hours of tedious manual edits and hello to effortless brilliance! With the Automatic Slideshow Generator, transform any topic into a polished, comprehensive slideshow in just seconds. Plus, you can tailor your presentation with your choice of bullet points and slides, ensuring it fits your exact needs.

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

## Set Env Variables
```shell script
export H2OGPTE_API_TOKEN="" 

export H2OGPTE_URL="https://**.h2ogpte.h2o.ai"
```
## Deploy in the AI Cloud

### App Secrets

```shell script
h2o secret create h2o-slideshow -l h2ogpte-key="" -l h2ogpte-url="https://***.h2ogpte.h2o.ai"
```

Note: The h2o cli is required to create secret keys. Learn more [here](https://h2oai.github.io/h2o-ai-cloud/developerguide/cli).


Once the virtual environment is setup and active, run:

```sh
wave run app.py
```

Which will start a Wave app at <http://localhost:10101>.