from bl_product_amaz.database import DataBase
from bl_product_amaz.amz_title_dic import AMZ_title_dic

class AMZ_attrs(DataBase):
    def __init__(self):
        super(AMZ_attrs, self).__init__()
        self.amz_attrs = self.db.amz_attrs


    def get_attr_dataset(self, offset=0, limit=100):
        query = {}
        attrs = []

        try:
            r = self.amz_attrs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for attr in list(r):
            del attr['_id']
            attrs.append(attr)

        return attrs

    def get_attr_by_attr_id(self, attr_id):
        query = {}
        query['attr_id'] = attr_id
        attrs = []

        try:
            r = self.amz_attrs.find_one(query)
        except Exception as e:
            print(e)
        if r == None:
            return r
        else:
            del r['_id']

        return r

    def get_attr_kr_name_by_attr_id(self, attr_id):
        query = {}
        query['attr_id'] = attr_id

        try:
            r = self.amz_attrs.find_one(query)
        except Exception as e:
            print(e)

        return r['attr_kr_name']

    def get_title_dic_by_attr_id(self, attr_id):
        query = {}
        title_dic = []
        query['attr_id'] = attr_id
        api_instance = AMZ_title_dic()


        try:    # get sub_attr_id
            r = self.amz_attrs.find_one(query)
            for sub_attr_id in r['sub_attr_ids']:
                try:    # get title_dic by sub_attr_id
                    offset = 0
                    limit = 50
                    while True:

                        res = api_instance.get_words_by_sub_attr_id(sub_attr_id,
                                                                      offset=offset,
                                                                      limit=limit)
                        if limit > len(res):
                            break
                        else:
                            offset = offset + limit
                    title_dic.extend(res)
                except Exception as e:
                    print(e)



        except Exception as e:
            print(e)

        return title_dic


    def get_sub_attr_by_attr_id(self, attr_id):
        query = {}
        query['attr_id'] = attr_id
        sub_attr_list = []

        try:
            r = self.amz_attrs.find_one(query)
            for sub_attr_id in r['sub_attr_ids']:
                sub_attr_query = {}
                sub_attr_query['sub_attr_id'] = sub_attr_id
                try:
                    r1 = self.db.amz_sub_attrs.find_one(sub_attr_query)
                    sub_attr_dic = {'sub_attr_id': sub_attr_id,
                                    'sub_attr_kr_name': r1['sub_attr_kr_name'],
                                    'sub_attr_us_name': r1['sub_attr_us_name']}
                    sub_attr_list.append(sub_attr_dic)
                except Exception as e:
                    print(e)

        except Exception as e:
            print(e)

        return sub_attr_list


    def add_attr(self, attr_id, attr_kr_name, attr_us_name):
        attr = {}
        attr['attr_id'] = attr_id
        attr['attr_kr_name'] = attr_kr_name
        attr['attr_us_name'] = attr_us_name
        attr['sub_attr_ids'] = []
        query= {}
        query['attr_id'] = attr_id

        try:
            r = self.amz_attrs.find_one(query)
        except Exception as e:
            print(e)
        if r == None:
            try:
                r = self.amz_attrs.insert(attr)
            except Exception as e:
                print(e)
        else:
            print("attr_id is already enrolled! Please check again")


    def update_sub_attr_ids(self, attr_id, sub_attr_id):
        query = {}
        query['attr_id'] = attr_id

        try:
            res = self.amz_attrs.find_one(query)
        except Exception as e:
            print(e)

        if res != None:
            sub_attrs = res['sub_attr_ids']
            if sub_attr_id not in sub_attrs:
                sub_attrs.append(sub_attr_id)

            try:
                res = self.amz_attrs.update(query, {'$set': {'sub_attr_ids': sub_attrs}}, upsert=False, multi=False)

            except Exception as e:
                print(e)
        else:
            print("attr_id is not enrolled! Please check again")



