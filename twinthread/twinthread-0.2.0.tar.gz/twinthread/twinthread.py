def fetch(token):
    print("Fetching data...")
    from azure.storage.common import CloudStorageAccount
    import pandas as pd
    import os
    X = token.split(",")
    X[3] = X[3] + "=="
    (blob, container, name, key) = X
    account = CloudStorageAccount(account_name=name, account_key=key)
    service = account.create_block_blob_service()
    service.get_blob_to_path(container, blob, "tempfile")
    print("Parsing data...")
    data = pd.read_csv("tempfile")
    os.remove("tempfile")
    from IPython.display import clear_output
    clear_output()
    return data
