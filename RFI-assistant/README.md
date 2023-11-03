# Automate Request for Information(RFI) using LLMs
Based on relevant company documents provided we can use LLMs to generate answers for questions in RFI documents.

## Local Development
```shell script
make clean
make setup
make run
```

## Set Env Variables
```shell script
export H2OGPTE_API_TOKEN="" 

export H2OGPTE_URL="https://**.h2ogpte.h2o.ai"
```
## Deploy in the AI Cloud

### App Secrets

```shell script
h2o secret create h2o-rfi-qa -l h2ogpte-key="" -l h2ogpte-url="https://***.h2ogpte.h2o.ai"
```

## App Defaults

- Default collection name is "<b>H2O_DEMO_RFI</b>" to be used in H2O Enterprise GPT
- Default doc URLs ingested as the part of above collection are:
  - https://h2o.ai/blog/2022/the-bond-market-ai-how-marketaxess-brings-it-all-together/
  - https://h2o.ai/platform/ai-cloud/managed/
  - https://docs.h2o.ai/haic-documentation/overview/what-is-h2o-ai-cloud/
  - https://docs.h2o.ai/h2o-llmstudio/


## App Workflow

### Upload Sources
This feature enables users to view the current list of documents in a collection that LLMs use to answer RFI queries. Disabled for demo!

### Upload RFI Questionnaire
This feature automates the RFI answering process. Users can upload an Excel file with a mandatory "Question" field. The LLM models use this to provide answers, which appear in an editable table for user review. Users can modify the answers in the table before downloading them.

  - Sample URL: https://raw.githubusercontent.com/narasimhard/demo-data/main/RFIQueriesLLM.xlsx

### Chat 
This feature allows users to interact directly with LLM models.

