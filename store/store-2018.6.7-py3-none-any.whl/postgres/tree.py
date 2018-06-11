import collections
import json

from pony.orm import Required, Optional, db_session, select

from store.postgres.postgres import PostgresStore
from store.postgres.util import FrozenJSON


class TreeStore(PostgresStore):

    def __init__(self, data):
        data['unique'] = True
        data['extra'] = {
            'level': Required(int, index=True),
            'index': Required(int, index=True),
            'weight': Required(float, index=True)
        }
        super(TreeStore, self).__init__(data)
        key = data.get('key')
        self.key = str(key)

    def create(self, key, value, pid=None, level=0, index=0):
        '''
            tree = {
               "value": { },
               "sub":   {
                   "a":  {
                        "c": {
                        }

                         },
                   "b":  {
                         }
               }
            }

        '''
        node_value = value.get('val')
        node_weight = value.get('wgt', 0)
        node_level = value.get('lev', level)
        node_id = super(TreeStore, self).create(key, node_value, pid=pid, level=node_level, index=0, weight=node_weight)

        node_sub = value.get('sub')
        if node_sub:
            index = 0
            for k, v in node_sub.items():
                self.create(key + '.' + k, v, pid=node_id, level=level + 1, index=index)
                index += 1

    def read(self, key):
        result = {}
        elem = super(TreeStore, self).read(key, filters=["level", "weight", "index"])
        if elem:
            id_ = elem.get('id')
            key = elem.get("key")
            value = elem.get("value")
            weight = elem.get("weight")
            index = elem.get("index")
            level = elem.get("level")

            result["val"] = value
            result["wgt"] = weight
            result["idx"] = index
            result["lev"] = level
            result["key"] = key

            elem_keys = self.read_sub(pid=id_)
            if elem_keys and len(elem_keys) > 0:
                result["sub"] = [self.read(e) for e in elem_keys]
            return result

    @db_session
    def read_sub(self, pid):
        elems = select(e for e in self.Store if e.pid.id == pid)[:]
        if elems:
            return [e.key for e in elems]

    def dfs(self, key, func):
        tree = self.read(key)
        if tree:
            tree = FrozenJSON(tree)
            if tree.val:
                func(tree)
                if tree.sub:
                    for e in tree.sub:
                        self.dfs(e.key, func)

    def bfs(self, key, func):
        tree = self.read(key)
        if tree:
            tree = FrozenJSON(tree)
            queue = collections.deque([tree])
            while queue:
                node = queue.popleft()
                func(node)
                if node.sub:
                    for node in node.sub:
                        queue.append(node)


if __name__ == '__main__':
    st = TreeStore({'name': 'new_store', "table": "test"})


    # st.create('hello', {
    #     "val": {"a":"b"},
    #     "sub": {
    #         "world1": {"val": "haha1", "sub": {
    #             "wd1": {"val": "hehe1"},
    #             "wd2": {"val": "hehe2"},
    #         }},
    #         "world2": {"val": "haha2"}
    #     }
    # })
    # data = st.read("hello")
    # data = st.children("hello")
    # data = st.siblings("hello.world1")
    # print(json.dumps(data, indent=2))
    def test(node):
        # print(tree.json)
        print(' '*2*node.lev, node.val)
        # print(type(tree))
        # print(tree.wgt, tree.key, tree.val, tree.lev, '....')


    st.bfs("hello", test)

    # st.create('hello', {
    #     "val": 100,
    #     "sub": {
    #         "world1": {"val": 200, "sub": {
    #             "wd1": {"val": 300},
    #             "wd2": {"val": 301},
    #         }},
    #         "world2": {"val": 201}
    #     }
    # })
