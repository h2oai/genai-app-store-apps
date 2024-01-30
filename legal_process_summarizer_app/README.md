# Legal Process Summarization
Build legal reports on appeal processes from court legal documents and decisions

## About this App:
This app aims to be able to summarize entire legal processes based on documents such as:
- Instrument Appeals
- Special Appeals
- Extraordinary Appeals
- Court Decisions
- Among others ..

### Features
- Summarization of legal processes using LLM and GenAI
- Backend orchestration using H2OGPTe


## Local Development
```shell script
python3.8 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/wave run src/app.py
```

export H2OGPTE_API_TOKEN=""
export H2OGPTE_URL="https://**.h2ogpte.h2o.ai"


## Deploy in the AI Cloud

### Secrets
```
h2o secret create company-information-at-a-glance -l h2ogpte-key="" -l h2ogpte-url="https://***.h2ogpte.h2o.ai"
```