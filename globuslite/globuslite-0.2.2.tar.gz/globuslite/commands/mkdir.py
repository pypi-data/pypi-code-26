from globuslite.transfer import get_transfer_client

__all__ = ['mkdir']

def mkdir( endpoint, path, **kwargs ):
    client = get_transfer_client()
    client.operation_ls( endpoint, path, **kwargs )
