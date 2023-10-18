from h2ogpte import H2OGPTE
import os

connect = {
    "address": os.getenv("H2OGPTE_URL"),
    "api_key": os.getenv("H2OGPTE_API_TOKEN"),
}

h2ogpte = H2OGPTE(address=connect["address"], api_key=connect["api_key"])

# This assumes you don't care about descriptions, update with the Collection Title: URL for any you want
collections_to_injest = {
    "H2O Wave Blogs": "https://wave.h2o.ai/blog",
    "H2O.ai Web Site": "https://www.h2o.ai/",
    "H2O Driverless AI Docs": "https://docs.h2o.ai/driverless-ai/1-10-lts/docs/userguide/index.html",
    "H2O Wave Docs": "https://wave.h2o.ai/",
    "H2O LLM Studio Docs": "https://docs.h2o.ai/h2o-llmstudio/",
    "H2O DocumentAI Docs": "https://docs.h2o.ai/h2o-document-ai/",
    "H2O FeatureStore Docs": "https://docs.h2o.ai/featurestore/",
    "H2O MLOps Docs": "https://docs.h2o.ai/mlops/",
    "H2O AppStore Docs": "https://docs.h2o.ai/h2o-ai-cloud/get-started/what-is-ai-app-store",
    "H2O Model Security": "https://docs.h2o.ai/wave-apps/h2o-model-security/",
}

for collection_name in collections_to_injest.keys():
    collection_id = h2ogpte.create_collection(
        name=collection_name,
        description=""
    )
    h2ogpte.ingest_website(
        collection_id=collection_id,
        url=collections_to_injest[collection_name]
    )

for c in h2ogpte.list_recent_collections(0, 1000):
    print(c.id, c.name, c.document_count)
