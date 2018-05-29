from bson.objectid import ObjectId
from bl_db_product_amz_best.database import DataBase

class Products(DataBase):
  def __init__(self):
    super(Products, self).__init__()
    self.products = self.db.products

  def get_products_by_node_id(self, node_id, offset=0, limit=100):
      query = {}

      if node_id is not None:
          query['NodeId'] = node_id

      try:
          r = self.db.products.find(query).skip(offset).limit(limit)
      except Exception as e:
          print(e)

      return list(r)

  def add_product(self, product):
    object_id = None
    # query = {'node_id': product.get('NodeId'),
    #          'title': product.get('Title'),
    #          'asin': product.get('Asin'),
    #          'url': product.get('url')}

    query = product

    try:
      r = self.products.update_one(query,
                                   {"$set": product},
                                   upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      product_id = str(r.raw_result['upserted'])

    return product_id