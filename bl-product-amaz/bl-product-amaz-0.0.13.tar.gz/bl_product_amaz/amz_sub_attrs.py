from bl_product_amaz.database import DataBase

class AMZ_sub_attrs(DataBase):
    def __init__(self):
        super(AMZ_sub_attrs,self).__init__()
        self.amz_sub_attrs = self.db.amz_sub_attrs

    def get_sub_attr_dataset(self, offset=0,limit=0):
        query = {}
        sub_attrs = []

        try:
            r = self.amz_sub_attrs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for sub_attr in list(r):
            del sub_attr['_id']
            sub_attrs.append(sub_attr)

        return sub_attrs


    def get_sub_attr_by_sub_attr_id(self, sub_attr_id):
        query = {}
        query['sub_attr_id'] = sub_attr_id

        try:
            r = self.amz_sub_attrs.find_one(query)
        except Exception as e:
            print(e)

        if r == None:
            return r
        else:
            del r['_id']

        return r


    def add_sub_attr(self, sub_attr_id, sub_attr_kr_name, sub_attr_us_name):
        query = {}
        query['sub_attr_id'] = sub_attr_id
        r = self.amz_sub_attrs.find_one(query)

        if r == None:
            try:
                query['sub_attr_kr_name'] = sub_attr_kr_name
                query['sub_attr_us_name'] = sub_attr_us_name
                query['condition']= ""
                r = self.amz_sub_attrs.insert(query)
            except Exception as e:
                print(e)
        else:
            print("Already enrolled sub_attr_id! Please check again")

