import os

from h2ogpte import H2OGPTE

client = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))

# documents_in_collections = [document.id
#                             for collection in client.list_recent_collections(0, 10000)
#                             for document in client.list_documents_in_collection(collection.id, 0, 100000)]
#
# all_documents = [document.id for document in client.list_recent_documents(0, 100000)]
#
# stranded_documents = [document for document in all_documents if document not in documents_in_collections]
#
# print(len(all_documents), len(documents_in_collections), len(stranded_documents))
#
# client.delete_documents(stranded_documents)


collections_to_ingest = {
    "h2oGPTe Documentation": "https://docs.h2o.ai/enterprise-h2ogpte/v1.4.11",
    "LLM Studio Documentation": "https://docs.h2o.ai/h2o-llmstudio/",
    "Eval Studio Documentation": "https://docs.h2o.ai/eval-studio-docs/",
    "Label Genie Documentation": "https://docs.h2o.ai/wave-apps/h2o-label-genie/",

    "Driverless AI Documentation": "https://docs.h2o.ai/driverless-ai/1-10-lts/docs/userguide/index.html",
    "H2O-3 Documentation": "https://docs.h2o.ai/h2o/latest-stable/h2o-docs/index.html",
    "Sparking Water Documentation": "https://docs.h2o.ai/sparkling-water/3.5/latest-stable/doc/index.html",
    "Hydrogen Torch Documentation": "https://docs.h2o.ai/h2o-hydrogen-torch",
    "Document AI Documentation": "https://docs.h2o.ai/h2o-document-ai/",

    "MLOps Documentation": "https://docs.h2o.ai/mlops/",

    "AI App Store Documentation": "https://docs.h2o.ai/h2o-ai-cloud/get-started/what-is-ai-app-store",
    "Wave Documentation": "https://wave.h2o.ai/",

    "H2O AI Cloud Documentation": "https://docs.h2o.ai/haic-documentation/",
    "Notebook Labs Documentation": "https://docs.h2o.ai/notebook/",
    "AI Engine Manager Documentation": "https://docs.h2o.ai/ai-engine-manager/",

    "H2O.ai Website": "https://www.h2o.ai/",

    "Feature Store Documentation": "https://docs.h2o.ai/featurestore/",
    "Enterprise Steam Documentation": "https://docs.h2o.ai/steam/index.html",
    "Enterprise Puddle Documentation": "https://docs.h2o.ai/puddle-release/latest-stable/docs/userguide/html/index.html",

}

for c in client.list_recent_collections(0, 1000):
    print(c.id, c.name, c.document_count)

for collection_name in collections_to_ingest.keys():
    print(f"Starting {collection_name}")
    collection_id = client.create_collection(
        name=collection_name, description=""  # AI will generate this
    )
    client.ingest_website(
        collection_id=collection_id, url=collections_to_ingest[collection_name], follow_links=True
    )

for c in client.list_recent_collections(0, 1000):
    print(c.id, c.name, c.document_count)
