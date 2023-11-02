# Make Your Own Home Listing

Automatically create customized real estate listings for your home.

## Local Development
```shell script
python3.8 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/wave run src/app.py
```

export H2OGPTE_API_TOKEN=""
export H2OGPTE_URL="https://**.h2ogpte.h2o.ai"

export THEME="winter-is-coming"
export LOGO="https://h2o.ai/content/experience-fragments/h2o/us/en/site/header/master/_jcr_content/root/container/header_copy/logo.coreimg.svg/1696007565253/h2o-logo.svg"

## Deploy in the AI Cloud

### Secrets
```
h2o secret create h2ogpt-oss -l h2ogpte-key="" -l h2ogpte-url="https://***.h2ogpte.h2o.ai"
```

### Alias
alias should be `make-home-listing.location.h2o.ai`