### Study Partner Wave App
App to use h2ogpt to create question off of a document collection that can be answer and feedback can be given in real time. 

#### Setup
See .env-example for needed values and fill in and make a copy to source.

````commandline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
source .env-playground
````

Run Locally
```commandline
wave run src/app.py
```


Deployment
```commandline
h2o secret create study_partner -l h2ogpt-key="" -l h2ogpt-url="https://gpt.h2o.ai"
```

![Example1](static/example1.png)

![Example2](static/example2.png)
