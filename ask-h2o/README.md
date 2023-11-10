# Ask H2O

This app connects to a specific user in H2OGPTE who has collections of public documentation about H2O.ai.

The end user can select the collection of documents they are interested in and then ask questions about those documents.

## Available Collections
Use the [Setup Script](src/setup-h2ogpte.py) to import any series of website into a single collection to use in this app.

## Local Development
```shell script
 python3.8 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/wave run src/app.py
```

export H2OGPTE_API_TOKEN=""
export H2OGPTE_URL="https://**.h2ogpte.h2o.ai"

export PRIMARY_COLOR="#FEC925"
export SECONDARY_COLOR="#E8E5E1"
export LOGO="https://h2o.ai/content/experience-fragments/h2o/us/en/site/header/master/_jcr_content/root/container/header_copy/logo.coreimg.svg/1696007565253/h2o-logo.svg"

## Deploy in the AI Cloud

### Secrets
```
internal secret create ask-h2o -l h2ogpte-key="" -l h2ogpte-url="https://***.h2ogpte.h2o.ai"
```

### Alias
alias should be `ask-h2o.location.h2o.ai`
