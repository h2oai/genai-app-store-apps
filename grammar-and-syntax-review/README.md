# Grammar and Syntax Review

Get feedback and improvements on emails, web copy, and more!

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
h2o secret create grammar-syntax-and-review -l h2ogpte-key="" -l h2ogpte-url="https://***.h2ogpte.h2o.ai"
```

### Alias
alias should be `content-review.location.h2o.ai`
