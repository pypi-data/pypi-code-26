

class CatalogService:
    def __init__(self, provider):
        self.provider = provider

    def list_open_clusters(self):
        return self.provider.list_open_clusters()

    def list_stars(self, coord):
        return self.provider.list_stars(coord)
