import os

from h2ogpte import H2OGPTE

connect = {
    "address": os.getenv("H2OGPTE_URL"),
    "api_key": os.getenv("H2OGPTE_API_TOKEN"),
}

h2ogpte = H2OGPTE(address=connect["address"], api_key=connect["api_key"])

collections_to_ingest = {
    "H2O Driverless AI Docs": "https://docs.h2o.ai/driverless-ai/1-10-lts/docs/userguide/index.html",
    "H2O LLM Studio Docs": "https://docs.h2o.ai/h2o-llmstudio/",
    "H2O Model Security": "https://docs.h2o.ai/wave-apps/h2o-model-security/",
    "H2O Hydrogen Torch": "https://docs.h2o.ai/h2o-hydrogen-torch",
    "H2O DocumentAI Docs": "https://docs.h2o.ai/h2o-document-ai/",
    "H2O FeatureStore Docs": "https://docs.h2o.ai/featurestore/",
    "H2O MLOps Docs": "https://docs.h2o.ai/mlops/",
    "H2O AppStore Docs": "https://docs.h2o.ai/h2o-ai-cloud/get-started/what-is-ai-app-store",
    "H2O Wave Docs": "https://wave.h2o.ai/",
    "H2O.ai Web Site": "https://www.h2o.ai/",
}

for c in h2ogpte.list_recent_collections(0, 1000):
    print(c.id, c.name, c.document_count)

for collection_name in collections_to_ingest.keys():
    print(f"Starting {collection_name}")
    collection_id = h2ogpte.create_collection(
        name=collection_name, description=""  # AI will generate this
    )
    h2ogpte.ingest_website(
        collection_id=collection_id, url=collections_to_ingest[collection_name]
    )

for c in h2ogpte.list_recent_collections(0, 1000):
    print(c.id, c.name, c.document_count)
