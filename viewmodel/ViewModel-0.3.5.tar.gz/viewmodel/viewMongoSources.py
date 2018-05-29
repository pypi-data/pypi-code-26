#!/usr/bin/env python3
"""
class defintions for sources used when accessing mongodb sources from views
import as ViewModelDB

provides a 'baseDB' object as a connection to mongo.
baseDB.db is the access to the database
This could be upgraded to provide fault tolerance in future.
"""

import pymongo
from .viewModel import DBSource, ActionType
from objdict import ObjDict

class DBMongoSource(DBSource):
    """ for sources direct to a collection"""
    def __init__(self, nm, collection, row_id, embed=False):
        if not embed: # name already set
            self.collect_name = nm # same
        if hasattr(collection, 'find_one_and_delete'):
            pass # stop false detect!
            #if collection.name not in('Student2s','Students'):
            #    import pdb; pdb.set_trace()

        elif hasattr(collection, 'baseDB'): # duck check for wrapped
            self.thedb = collection.baseDB
            self.raw_collect = collection
            collection = None #self.thedb.db.get_collection(nm)
        super().__init__(nm, collection, row_id)

    @property
    def row_source(self):
        if self._row_source is None:
            self._row_source = self.thedb.db.get_collection(self.collect_name)
        return self._row_source

    @staticmethod
    def map_change(chng):
        """ substitute '.'(dotted) keys with sub items 
        """

        for k, v in list(chng.items()): #iterate orinal list
            if '.' in k:
                del chng[k]
                basek = k.split('.')[0]
                base = chng.get(basek, {})
                chng[basek] = base
                for kn in k.split('.')[1:]:
                    base[kn] = v
                    basek = kn
                    base = base.get(kn, {})
                    v = base

        return chng

    def apply_changes_to_dbsource(self, view, idx_, change, tbl, action_type=None):

        def re_key(tbl, idx, change_dict):
            #if tbl == 'members.cards':
            #    import pdb; pdb.set_trace()
            if '.' not in tbl:
                return change_dict
 
            key_start = "{0}.{1}.".format(tbl.split('.', 1)[1], idx)
            return {key_start+key:val
                    for key, val in change_dict.items()
                   }

        def check_error(rc):
            if hasattr(rc, 'raw_result'):
                raw = rc.raw_result
                if not raw['ok']:
                    raise ValueError('mongo update fail')
                pass
            elif False: #isinstance(rc,ObjectID):
                #case insert.... but this code should be in viewMongoDB.py
                valid = u.is_valid
                if True: #not rc.isvalid:
                    raise ValueError('mongo insert fail')
            else:
                pass #import pdb; pdb.set_trace()

        src = view.maptbl_(tbl) #if self.joins_ else self.dbRowSrc
        rawrow = view.dbRows_[idx_]
        row = rawrow[tbl] #if self.joins_ else rawrow
        row_id = row.get('_id', self.row_id)

        if row_id is None and row:
            pass  # import pdb; pdb.set_trace()

        if action_type == ActionType.Delete:
            if '.' in tbl:
                # case 1/2: delete the nested data
                if 'key' not in row:
                    print("WARNING: No `key` in row, can't do the deletion")
                    return

                if 'id' in row['key']:
                    key_name = 'key.id'
                    key_value = row['key']['id']
                elif 'sqlid' in row['key']:
                    key_name = 'key.sqlid'
                    key_value = row['key']['sqlid']

                _, sub_column_name = tbl.split('.', 1)

                src.update_one(
                    {'_id': row_id},
                    {'$pull': {sub_column_name: {key_name: key_value}}}
                )
            else:
                # case 2/2: delete the normal data
                src.delete_one({'_id': row_id})
        elif action_type == ActionType.Insert and not row_id:
            u = src.insert(self.map_change(change))
            check_error(u)
            if '_id' in change:
                new_id = change['_id']
                view.dbRows_[idx_][tbl]['_id'] = new_id
                for join_link in self.join_links:
                    ins_id = new_id
                    if '.' in join_link:
                        join_link,fld = join_link.split('.')
                        tmpobj = view[idx_][join_link].value
                        tmpobj[fld] = new_id
                        ins_id = tmpobj

                    view[idx_][join_link].value = ins_id
            # add id to this rec....
            # follow join instructions (from _sources)
        else:
            update={'$set': re_key(tbl, idx_, change)}
            filter_=dict(_id=row_id)
            u=src.update_one(filter_,update)
            check_error(u)
            view.log_journal()


class DBMongoEmbedSource(DBMongoSource):
    """ for sources embedded inside a document"""
    def __init__(self, db, nm):
        self.thedb = db.baseDB
        self.collect_name = nm.split('.', 1)[0]
        #collection = db.baseDB.db.get_collection(tblcore)
        super().__init__(nm, None, None, embed=True)

    def map_src(self, src):
        """ exactly like super() version,  but skips 2
          maps a 'src' string to return dictionary names
          currently simply assumes first link is source and correct
          so discards first link"""
        return src.split('.')[2:]
