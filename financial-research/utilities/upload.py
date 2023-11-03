import os
import time

from h2ogpte import H2OGPTE

h2ogpte = {
    "address": os.getenv("H2OGPTE_URL"),
    "api_key": os.getenv("H2OGPTE_API_TOKEN"),
}
h2ogpte = H2OGPTE(address=h2ogpte["address"], api_key=h2ogpte["api_key"])

collections = h2ogpte.list_recent_collections(0, 1000)

paths_to_dir = ['./data']

col_list = {}
for c in collections:
    if c.name in col_list:
        print("Duplicate " + c.name)
    col_list[c.name] = 1
    # print("Added "+c.name+" to dict\n")
col_list['.DS_Store'] = 1

for p in paths_to_dir:
    for l in sorted(os.listdir(p)):
        collection_name = os.path.splitext(l)[0]  # Remove extension
        print(collection_name)
        if collection_name not in col_list:
            description = os.path.splitext(l)[0]
            print("Uploading " + p + "/" + l + "\r")
            start = time.time()
            collection_id = h2ogpte.create_collection(name=collection_name, description=description)
            f = open(p + '/' + l, 'rb')
            uf = h2ogpte.upload(p + '/' + l, f)
            h2ogpte.ingest_uploads(collection_id, [uf])
            end = time.time()
            print("Uploaded  " + p + "/" + l + "  " + str(int(end - start)) + " secs \n")
