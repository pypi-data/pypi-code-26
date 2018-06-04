from bl_product_amaz.database import DataBase
from bson.objectid import ObjectId

class US_btgs(DataBase):
    def __init__(self):
        super(US_btgs, self).__init__()
        self.us_btgs = self.db.us_btgs

    def get_btg_dataset(self, offset=0, limit=100):
        query = {}
        btgs = []

        try:
            r = self.us_btgs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for btg in list(r):
            del btg['_id']
            btgs.append(btg)

        return btgs

    def get_btg_by_node_id(self, node_id):
        query = {}
        query['node_id'] = node_id

        try:
            r = self.us_btgs.find_one(query)
        except Exception as e:
            print(e)

        if r == None:
            return  r
        else:
            del r['_id']

        return r

    def get_node_name_by_node_id(self, node_id):
        query ={}
        query['node_id']

        try:
            r = self.us_btgs.find_one(query)
        except Exception as e:
            print(e)

        if r == None:
            return r
        else:
            del r['id']

        return r


    def get_attrs_by_node_id(self, node_id):
        query = {}
        query['node_id'] = node_id
        attr_list = []

        try:
            r = self.us_btgs.find_one(query)
        except Exception as e:
            print(e)

        for attr in r['attr_ids']:
            attrs_query = {}
            attrs_query['attr_id'] = attr
            try:
                r1 = self.db.amz_attrs.find_one(attrs_query)
                attr_dic = {attr : r1['attr_kr_name']}
                attr_list.append(attr_dic)
            except Exception as e:
                print(e)

        return attr_list

    def update_attr_id_by_node_id(self, node_id, attr_id):
        query = {}
        query['node_id'] = node_id

        try:
            res = self.us_btgs.find_one(query)
        except Exception as e:
            print(e)

        attrs = res['attr_ids']
        if attr_id not in attrs:
            attrs.append(attr_id)

        try:
            res = self.us_btgs.update(query, {'$set': {'attr_ids': attrs}}, upsert=False, multi=False)

        except Exception as e:
            print(e)


