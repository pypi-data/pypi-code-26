from . import catalog_service
from . import sample_catalog_provider

from . import data

def hello_universe():
    return "Hello universe!"


provider = sample_catalog_provider.SampleCatalogProvider()
Catalog = catalog_service.CatalogService(provider)
