from star_builder import Driver


class MongoDriver(Driver):

    def __init__(self, col):
        self.col = col

    async def find_by(self, **kwargs):
        projection = kwargs.pop("projection", {})
        projection["_id"] = 0
        async for doc in self.col.find(kwargs, projection):
            yield doc

    async def find_by_id(self, id):
        projection = {"_id": 0}
        return await self.col.find_one({"id": id}, projection)

    async def remove(self, doc):
        return await self.col.remove(**doc.to_json())

    async def update(self, doc):
        return await self.col.replace_one({"id": doc.id}, doc)

    async def save(self, doc):
        return await self.col.insert(doc.to_json())
