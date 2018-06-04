from bl_product_amaz.database import DataBase
from bl_product_amaz.amz_sub_attrs import AMZ_sub_attrs

class AMZ_title_dic(DataBase):
    def __init__(self):
        super(AMZ_title_dic,self).__init__()
        self.amz_title_dic = self.db.amz_title_dic

    def get_title_dic_database(self, offset=0, limit=100):
        query = {}
        word_dic = []

        try:
            r = self.amz_title_dic.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for word in list(r):
            del word['_id']
            word_dic.append(word)

        return word_dic

    def get_dic_by_sub_attr_id(self, sub_attr_id, offset=0, limit=100):
        query={}
        query['sub_attr_id'] = sub_attr_id

        try:
            r = self.amz_title_dic.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        return list(r)

    def get_words_by_sub_attr_id(self, sub_attr_id, offset=0, limit=50):
        query = {}
        query['sub_attr_id'] = sub_attr_id
        title_dic = []

        try:
            r = self.amz_title_dic.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for word in list(r):
            title_dic.append(word['sub_attr_dic_word'])

        return title_dic

    def get_dic_word_value_by_sub_attr_word(self, sub_attr_word):
        query = {}
        query['sub_attr_dic_word'] = sub_attr_word

        try:
            r = self.amz_title_dic.find_one(query)
        except Exception as e:
            print(e)

        return r

    def add_count_by_sub_attr_dic_word(self, sub_attr_dic_word, count_up_num):
        query = {}
        query['sub_attr_dic_word'] = sub_attr_dic_word

        try:
            r = self.amz_title_dic.update(query, {'$inc': {'count': count_up_num}}, upsert=False, multi=False)
        except Exception as e:
            print(e)


    def reset_count_to_zero_by_sub_attr_id(self, sub_attr_id):
        query = {}
        query['sub_attr_id'] = sub_attr_id

        try:
            r = self.amz_title_dic.update(query, {'$set': {'count': int(0)}}, upsert=False, multi=True)
        except Exception as e:
            print(e)


    def add_title_dic_word(self, sub_attr_id, word):
        query = {}
        query['sub_attr_dic_word'] = word
        query1 = {}
        query1['sub_attr_id'] = sub_attr_id
        api_instance = AMZ_sub_attrs()

        try:
            r = self.amz_title_dic.find_one(query)
        except Exception as e:
            print(e)

        try:
            r1 = api_instance.get_sub_attr_by_sub_attr_id(sub_attr_id)
        except Exception as e:
            print(e)


        if r == None:
            if r1 != None:
                query['sub_attr_id'] = sub_attr_id
                query['count'] = int(0)
                try:
                    r1 = self.amz_title_dic.insert(query)
                except Exception as e:
                    print(e)
            else:
                print("sub_attr_id is not enrolled! Please check again")
        else:
            print("Already enrolled title word! Please check aggin")