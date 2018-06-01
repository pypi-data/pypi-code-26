from globuslite.transfer import get_transfer_client

__all__ = ['ls']

def ls( endpoint, path ):
    client = get_transfer_client()
    return client.operation_ls( endpoint, path=path )

