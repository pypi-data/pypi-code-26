from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import pymongo


class DBCopier:
    """ Three operations are possible:
    - send DB to remote server from localhost
    - retrieve copy all collections of DB to localhost from remote server
    - clone database on local server
    """

    def __init__(self, remote=None):
        self.set_remote(remote)

    def set_remote(self, remote):
        """ Format for remote:
        [username:password@]host1[:port1]
        i.e. mongodb://[username:password@]host1[:port1] but without the mongodb://
        """
        if not remote:
            return

        self.full_remote = remote
        print("Remote is set: " + self.full_remote)

        if '@' in remote:
            user, remote = remote.split('@', 1)
            if ':' not in user:
                user += ':'
            self.user, self.pwd = user.split(':', 1)

        self.remote = remote

    def local(self, src, dest, drop=True):
        client = pymongo.MongoClient()
        if drop and dest in client.database_names():
            print("Dropping collection ...")
            client.drop_database(dest)

        print("Copying " + src + " to " + dest + " locally ...")
        client.admin.command('copydb', fromdb=src, todb=dest)

    @staticmethod
    def row_copy(src, dest, dbname, drop=True):
        """
        Copy each row in the collection
        :param src: The source (from) DB name
        :param dest: The destination (to) DB name
        :param dbname:
        :param drop:
        :return:
        """
        db = src.get_database(dbname)
        dbdest = dest.get_database(dbname)

        if drop:
            for collname in dbdest.collection_names():
                if 'system.' not in collname.lower():
                    print("Dropping collection ...")
                    dbdest.drop_collection(collname)

        print("Running row copy ...")
        progress = 1
        for collname in db.collection_names():
            print("." * progress)
            progress += 1
            coll = db.get_collection(collname)
            targ = dbdest.get_collection(collname)
            rows = coll.find({})
            for row in rows:
                targ.insert(row)

    def to_remote(self, dbname, remote=None, drop=True):
        """
        Copy a local DB to the remotely hosted DB.
        :param dbname: The local DB name to copy
        :param remote: The remote URL + DB name e.g. "mongodb://saltminers:pytester@ds023108.mlab.com:23108/test_reference"
        :param drop: Drop collection (defaults to True)
        :return: No return - side effect is copy from local to remote
        """
        print("Copy from local to remote")

        self.set_remote(remote)

        dest = pymongo.MongoClient(self.full_remote)
        if dest:
            print("Remote connected ...")

        src = pymongo.MongoClient()
        if src:
            print("Local connected ...")

        self.row_copy(src, dest, dbname)

    def from_remote(self, dbname, remote=None, drop=True):
        """
        Copy a remote DB to the locally hosted DB.
        :param dbname: The local DB name to copy
        :param remote: The remote URL + DB name e.g. "mongodb://saltminers:pytester@ds023108.mlab.com:23108/test_reference"
        :param drop: Drop collection (defaults to True)
        :return: No return - side effect is copy from local to remote
        """
        print("Copy from remote to local")

        self.set_remote(remote)

        src = pymongo.MongoClient(self.full_remote)
        if src:
            print("Remote connected ...")

        dest = pymongo.MongoClient()
        if dest:
            print("Local connected ...")

        self.row_copy(src, dest, dbname)

    def list_collections(self):
        db = pymongo.MongoClient(self.full_remote)
        # return db.getCollectionNames()
        return db.collection_names()

#
# if __name__ == '__main__':
#     dataStore = DataStore()
#
#     theApp = DbDocCopyApp()
#     theApp.run()
