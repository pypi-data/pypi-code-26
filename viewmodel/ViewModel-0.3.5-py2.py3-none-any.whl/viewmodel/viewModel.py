import logging
import os
from collections import OrderedDict as ODict
from enum import Enum, EnumMeta
from logging.handlers import RotatingFileHandler

from objdict import ObjDict
from viewmodel.viewFields import BaseField, Case, FieldItem, ModelStatus, ActionType

from .viewFields import viewModelDB

Section = Enum('ViewSection', 'all header main footer')
# 'edit' in Case.__members__
# try:
#     import saltMongDB as viewModelDB
# except ImportError:


class ViewModelError(Exception):
    def __init__(self, message, **extras):
        Exception.__init__(self, message)
        self.extras = extras


def get_dict_attr(obj, attr):
    for obj in [obj]+obj.__class__.mro():
        if attr in obj.__dict__:
            return obj.__dict__[attr]
    raise AttributeError


class BaseFieldDict(ODict):
    def __init__(self, *args, **kwargs ):
        super().__init__(*args, **kwargs)

    #code


class PageDict(ODict):
    """ PageDict is a dict of all fields in view, including all rows
    in the view!
    """
    def __init__(self, view, basef, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view = view
        self.main = ODict() #this should be all rows
        self.head = ODict()
        self.foot = ODict()
        cdict = self.main
        self.Section = Section
        self.Case = Case

    def __2call__(self, *args, **kwargs):
        self.view.loop(*args, **kwargs)

    def __call__(self, section=Section.main, case=Case.viewAll):
        view = self.view

        if section in (Section.all, Section.header):
            for name,field in self.head.items():
                if field.cases is None or case in field.cases:
                    yield field

        if section in (Section.all, Section.main):
            doAll = True #- do_all_rows  :was-> = section is not Section.current
            count = len(view.dbRows_)
            # save=view.old_idx_
            for i in range(count):
                for name,field in self.main.items():
                    if field.cases is None or case in field.cases:
                        yield field

        if section in (Section.all, Section.footer):
            for name,field in self.foot.items():
                if field.cases is None or case in field.cases:
                    yield field


class FieldDict(ODict):
    def __init__(self, view, basef, row, *args, **kwargs ):
        super().__init__(*args,**kwargs)
        self.view=view
        self.Case=Case
        for nm,f in basef.items():
            self[nm]=FieldItem(view,f,row)

    def __2call__(self,*args,**kwargs):
        self.view.loop(*args,**kwargs)

    def __call__(self,case=Case.viewAll ):
        view=self.view

        for name,field in self.items():
            if field.cases is None or case in field.cases or case == Case.allFields:
                yield field

    def loopRows(self):
        """ an iterator to set each row in turn as current
        does not actually belong here- but in View itself!
        """
        for i in range(len(self.view.dbRows_)):
            yield ViewRow(self.view, i)


class ViewRow:
    """ the idea is to have a view
    consist, at least logically, of a number of view rows.
    so view[n]  is the nth row:
    .    this would allow an improved interaction through a view
    .    plus allow storing references to a specific row within a view.
    each view could still have a 'default' row which can be set by
    "idx _" as happens currently

    so for example- an actual view could really be a view row
    which returns a new view row object when indexed. the new viewrow object
    would have the same data for all except _idx?  copy object, reset idx?
    would that work? would share rows and fields. what else would not be shared
    so viewObj[1] is copy of view with _idx set to 1?

    this would be neater if what was instanced was::

        view self._idx,self.underlying_view

    """
    def __init__(self, view, row):
        self._view = view
        self._row = row
        self._fields = None
        #self.__json__encode = None

    def __getattr__(self, attr):
        # if bug makes recurse then check attrs are ViewFields!
        if attr in self.fields_:
            return self._view._baseFields[attr].__get__(self._view, None, self._row)
        raise AttributeError('no {} in ViewRow'.format(attr))

    def __setattr__(self, attr, value):
        if attr in ('_view', '_row', '_fields'):
            super().__setattr__(attr, value)
        elif attr in ('idx_',):
            raise AttributeError('Cant set '+ attr)
        elif attr in self.fields_:
            self._view._baseFields[attr].__set__(self._view, value, self._row)
        else:
            raise TypeError('Whoa - ViewRow Attr error')

    @property
    def labelsList_(self):  # this should be deprecated...was a mistake to add here
        return self._view.labelsList_

    @property
    def rowLabel_(self):
        pass

    @property
    def row_idx_(self):
        return self._row

    @property
    def view_(self):
        return self._view

    @property
    def fields_(self):
        if self._fields is None:
            self._fields = FieldDict(self._view, self._view._baseFields, self._row)
        return self._fields

    def __getitem__(self,key):
        return self.fields_[key]

    def delete_(self):
        to_change = self.view_.changes_[self._row]
        to_change.action = ActionType.Delete

        if len(to_change.keys()) == 0:
            for source in self.view_._source_list:
                to_change[source] = {}

    def update_(self):
        self._view.update_()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.update_()

    def __iter__(self):
        return self.fields_()

    def loop_(self, case=Case.viewAll, section=Section.all ):
        # section is an idea - but not yet implemented
        return self.fields_(case=case)
        # group = [self.fields_,self.head,self.main.self.foot][section]
        # for field in group:
        #     if field.cases is None or case in field.cases:
        #         yield field

    def __json__(self, internal=False):
        def jsonval(key):
            if isinstance(self[key].Type, EnumMeta):
                return self[key].value.value
            if internal:
                return self[key].value
            return self[key].strvalue
        keys = self.fields_.keys()
        if self.view_.dbRows_:
            res = ObjDict([(key, jsonval(key)) for key in keys ])
        else:
            res = {}

        if not internal:
            res=str(res)
        return res


class DBSource:
    """
        consists of an ObjDict keyed by what was 'joins', but with an entry for all tables
        with each entry being an object with 'row_source', and 'row_key' attributes.
        row_source - is the previous default_dbRowSrc_  ...the table object for db operations
            row_source set to none should be used to indicate a memory only source
        row_id - None except when view data is embedded in a list within a single
                document, in which case this is the key for the umbrella document

        loader  -  the method to be used to lazy load the data
        join_links  - list of ViewFlds to be updated with _id
    """
    # __keys__ = "full_name row_source row_id"
    loader = None

    def __init__(self, full_name, row_source, row_id):
        self.full_name = full_name
        self._row_source = row_source
        self.row_id = row_id
        self.join_links = []

    def __repr__(self):
        return ('DBSource: {full_name} from {_row_source} id:{row_id} j:{join_links}'
                .format(**vars(self)))
    
    @property
    def row_source(self):
        return None

    def map_src(self, src):
        """ maps a 'src' string to return dictionary names
          currently simply assumes first link is source and correct
          so discards first link"""
        return src.split('.')[1:]

    def apply_changes_to_dbsource(self, view, idx_, change, tbl, action_type=None):
        return # default is to ignore changes


class DBNoSource(DBSource):
    pass


from viewmodel.viewMongoSources import DBMongoSource


class BaseView:
    """
    A view is an object model containing view specific model in addition to potentially one or more database row models.

    Joins views are launched with the base join table or directly. If a view is instanced directly - then 'join' fields
    are not available, and access will be an error.

    As properties of any name can be added and should not collide with ?  # TODO: finish this sentence.

    A view is usually specific to one or more data base rows, but allows for operations (such as 'next') to change the
    database row appearing in the view.

    Views can be input as well as output.

    View field values can be retrieved and set as properties within the view, but can also be accessed from:
    _baseFields {}  class property, is an ordered dict of all 'field' properties sorted by order

    fields_ {}      is an instance object controlling access to odict(property, instance) pairs for accessing:
                    both value and properties of a field

    joins_ {}       if rows are collections built from joins,
                    ObjDict of loaders that contain the actual rows.
                    field searches occur in order of the list

    _sources {}     a new ObjDict of DBSource objects which replaces 'joins' and dbRowSrc

    dbRows_         is a list of rows, with each row an ObjDict keyed by source, containing the values
                    for each source.  Normally values for each source are also an ObjDict, but
                    future types could change this

    There are currently 3 discrete source types available when defining a view:
        - Mongo DB collections (DBMongoSource)
        - Mongo DB embedded collections (DBMongoEmbedSource)
        - in memory i.e. data with no persistent storage (DBNoSource)

    Mongo DB is the main source type for persistent data currently but other source types can be added in the future
    that say, might enable connecting a different type of DB, such Maria DB or the like.

    The general idea is that, on initialisation, each view definition has a 'getRows_' method which, ideally, should be
    passed a dictionary that is used as the filter to get the required data from the collection/table. The first source
    listed in the 'models_' attribute in the view definition is used to set the number of rows and fill in values or
    it sets up other data retrieval methods for on-demand (aka 'lazy' loading) to get the extra/missing data when/if it
    is required. In turn, the second source listed, fills in extra/missing values or it sets up other data retrieval
    methods for on-demand loading, and so on. Each source listed a way of populating the view attributes.

    The first source listed in the 'models_' attribute in the view definition is usually the default or main
    collection/table containing the desired data. This will usually be the direct collection/table reference, for
    example: the device view definition i.e. 'DeviceView', might have this 'models_' attribute:
            models_ = Device

    In this particular case, 'Device' should ideally be a 'DBMongoSource' type. It could otherwise be a set up to be a
    collection emulator, in which case, the following statement would need to be included, before the view definition:
        Devices = viewModelDB.baseDB.db.devices

    Note that the first source listed do not necessarily need to be a source directly pointing to a collection. It can
    be an embedded source type or None, see below.

    If embedded references need to also be listed, for example, for a embedded member devices, then the 'MemberView'
    view definition will need to include 'DBMongoEmbedSource'. For example: the 'models_' attribute might look
    something like this:
           models_ = Members, DBMongoEmbedSource(viewModelDB, "device.id")

    Indeed, if the view requires just the embedded collection then it can be listed alone, for example:
           models_ = DBMongoEmbedSource(viewModelDB, "device.id")

    The third source is 'in memory' and is implemented by setting the models_ attribute to 'None' in the view
    definition:
           models_ = None

    The 'getRows_' method should use a DB find statement similar to the following:
            result = self.default_dbRowSrc_.find(some_filter)
    where 'some_filter' is a dictionary.

    The find method relies on the 'default_dbRowSrc_' property.
    """
    _baseFields = None
    should_journal = False

    def __init__(self, *args, **kwargs):
        self._sources = ObjDict()
        models = kwargs.get('models', getattr(self, 'models_', False))
        if not isinstance(models, (list, tuple)):
            models = [models]
        for model in models:
            if hasattr(model, 'baseDB'):  # ducktype check for collect emulator
                self._sources[model.name] = DBMongoSource(model.name, model, None)
            elif model is None:
                self._sources['__None__'] = DBNoSource('__None__', None, None)
            elif isinstance(model, str) and model[:1] == '_': # txt based one...
                self._sources[model] = DBNoSource(model, None, None)
            elif isinstance(model, DBSource):
                self._sources[model.full_name] = model
            else:
                nm = self.safeName_
                if model is False:
                    error = "View requires 'models_ =' class value, or 'models=' parameter, for "
                    raise TypeError(error + nm)
                else:
                    raise TypeError('Invalid type for model (within models) in '+ nm)

        self.joins_ = ObjDict()

        self.dbRows_ = self.getRows_(*args, **kwargs)

        if not isinstance(self.dbRows_, list):
            #handle legacy, single source returning raw data from mongo find
            row = self.row_name_
            self.dbRows_ = [ObjDict(((row, res), )) for res in self.dbRows_]
        
        self._source_list = list(self._sources.keys())

        if True: # self.dbRows_:
            self.changes_=[ModelStatus() for r in self.dbRows_]
            if not self._baseFields:
                #print('setfields',self.viewName_)
                self.buildBaseFields_()
            self.pag_fields_ = PageDict(self,self._baseFields)
        else:
            self.changes_= []
            self.fields_=ODict()
        #self.old_idx_ = 0

        # auto add an entry to empty NoSource Views
        if (self.dbRows_ == [] and 
            len(self._sources) == 1 and 
            isinstance(self.default_source_, DBNoSource) ):
                self.insert_()

    @property
    def safeName_(self):
        return getattr(self, 'viewName_', 'view with no viewName_ set: '
                + self.__class__.__name__)

    @property
    def default_dbRowSrc_(self):
        return self.default_source_.row_source

    @default_dbRowSrc_.setter
    def default_dbRowSrc_(self, value):
        assert False, ("using default_dbRowSrc to set values is deprecated: " +
                       self.__class__.__name__)
        # unreachable code below
        # if isinstance(value,str) and value[:1] =='_':
        #     #local data begins with _
        #     self._sources[value] = DBSource(value, None, None)
        #
        # elif not value is None:
        #     self._sources[value.name] = DBSource(value.name, value, None)

    @property
    def default_source_(self):
        return list(self._sources.values())[0]

    @property
    def row_name_(self):
        """return name of first(and most often only) source """
        return self.default_source_.full_name

    @property
    def joins_(self):
        raise ValueError('obsolete use of join')
        # unreachable code below
        # return self._joins

    @joins_.setter
    def joins_(self,value):
        if value != ObjDict():
            raise ValueError('obselete set of join')
        self._joins = value
        for k,v in value.items():
            if not k in self._sources:
                self._sources[k] = DBSource(k, None, None)
            self._sources[k].loader = value[k]

    @property
    def idx_(self):
        """note old .idx_ was the row to view.... now is just data passed to __json__
        indicting the number passed to a page view as currently selected to send to browser
        not used by server
        only left as a property so diagnositics can be added to retrieval or setting"""
        return getattr(self, "_idx", None) #raise "do not use!"

    @idx_.setter
    def idx_(self, value):
        if hasattr(self, "_idx"):
            raise ValueError("can only set idx once per view")
        self._idx = value

    @property
    def view_(self):
        return self

    @property
    def fields_(self):
        """asking for fields on ViewModel itself work for a row 0"""
        return ViewRow(self,0).fields_

    @property
    def joinkeys_(self):
        return list(self.joins_.keys())

    def set_source_idx_(self, source, idxrow):
        """ records a source of data as being from a fixed record
        this is relevant when a table within a record is the source of data
        source is which source of data(key, not number)
        idxrow is the row containing the _id
        """
        self._sources[source].row_id = idxrow['_id']

    def getJoin_(self, collectName, findFilt, idx_):
        if viewModelDB is None:
            raise ViewModelError('no db')
        collect=viewModelDB.baseDB.db.get_collection(collectName)
        result=collect.find(findFilt)
        result = [ObjDict(res) for res in result]
        assert len(result)==1,'Error with find for ()join'.format(collectName)
        self.dbRows_[idx_][collectName]=result[0]

    #def __getattr__(self,name):
    #    return getattr(self.field,name)

    # @staticmethod
    def maptbl_(self, tbl):
        newrettbl = self._sources[tbl].row_source
        tblcore = tbl.split('.', 1)[0]
        oldrettbl = viewModelDB.baseDB.db.get_collection(tblcore)
        
        assert newrettbl == oldrettbl, "oops setup fail for source"
        return oldrettbl

    def get_foreign_key(self, idx_, tbl):
        """
        For the case where the data we wanna delete is not loaded yet,
        We need to get its foreign id in order to delete it.
        """
        if tbl in self.dbRows_[idx_]:
            # The data has been loaded
            # TODO: need to handle the case where the `foreign id` is not there?
            # Since the data maybe partial loaded when user do a update
            return

        # The data hasn't been loaded yet, let's get its foreign key
        # This case represents that we are `cards`,
        # but we wanna get the foreign id from `members.cards`
        if '.' not in tbl:
            expected_part = '.' + tbl
            refer_key = ''
            for key in self.dbRows_[idx_].keys():
                if key.endswith(expected_part):
                    refer_key = key
                    break

            refer_data = self.dbRows_[idx_][refer_key]

            if 'key' in refer_data:
                foreign_key = self.dbRows_[idx_][refer_key]['key']

                if 'id' in foreign_key:
                    self.dbRows_[idx_][tbl] = {'_id': foreign_key['id']}
                elif 'sqlid' in foreign_key:
                    self.dbRows_[idx_][tbl] = {'sqlid': foreign_key['sqlid']}
                else:
                    print('[delete_] WARNING: No sqlid or objectId, what data is it?')
            else:
                print('[delete_] WARNING: No `key`, what data is it?')

    def update_(self):

        # note - could create more changes with join ids - while changes?
        for idx_, changes in enumerate(self.changes_):
            # if not self.joins_:
            #    changes = ObjDict(table=changes)
            for tbl, change in changes.items():

                if changes.action == ActionType.Delete:
                    self.get_foreign_key(idx_, tbl)
                    self._sources[tbl].apply_changes_to_dbsource(self, idx_, changes, tbl, changes.action)
                    continue

                if change:
                    self._sources[tbl].apply_changes_to_dbsource(self, idx_, change, tbl, changes.action)
                changes[tbl] = ModelStatus()  # see VIEW-40 about possible change

                '''
                src = self.maptbl_(tbl) #if self.joins_ else self.default_dbRowSrc_ 
                rawrow = self.dbRows_[idx_]
                row = rawrow[tbl] #if self.joins_ else rawrow
                row_id = row.get('_id',self._sources[tbl].row_id)
                if row_id is None and row:
                    pass #import pdb; pdb.set_trace()
                if row_id is None: # or new row of []
                    # row , must be new data so inser !!  (was no _id, so should be an insert!)
                    u=src.insert(change)
                    check_error(u)
                    if '_id' in change:
                        new_id = change['_id']
                        self.dbRows_[idx_][tbl]['_id'] = new_id
                        for join_link in self._sources[tbl].join_links:
                            ins_id = new_id
                            if '.' in join_link:
                                join_link,fld = join_link.split('.')
                                tmpobj = self[idx_][join_link].value
                                tmpobj[fld] = new_id
                                ins_id = tmpobj

                            self[idx_][join_link].value = ins_id
                    #add id to this rec.... 
                    # follow join instructions (from _sources)
                else:
                    update={'$set': re_key(tbl, idx_, change)}
                    filter_=dict(_id=row_id)
                    u=src.update_one(filter_,update)
                    check_error(u)
                '''

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.update_()

    def buildBaseFields_(self ):
        """ called once for the class """

        fields=BaseFieldDict()
        #fields.__call__ = self.loop
        self.__class__._baseFields = fields
        #self.rows =self.getRow()
        cls=self.__class__
        holder=[]
        for thiscls in [cls] + cls.mro()[:-2]: #skip object and baseView
            for attribName in list(thiscls.__dict__):
                #if at in self.__dict#    at = getattr(cls,a)

                if isinstance(thiscls.__dict__[attribName],BaseField):
                    attribObj = thiscls.__dict__[attribName]
                    theRow = self.dbRows_[0] if self.dbRows_ else ObjDict()
                    name = attribObj.setup(attribName,theRow,self)
                    holder.append( (attribObj.instanceNum,attribName,attribObj))
        for num,key,obj in sorted(holder):
            #print('hkey',key)
            fields[key]= obj

        #need to set main,head,foot - but as properties of fields_ in the end!
        #print('hold',holder)
        #print('sholder',sorted(holder))

    def insert_(self):
        """ add a new blank row to the end of data
        """
        last=len(self.dbRows_)
        newrow = ObjDict()
        for k in self._sources:
            newrow[k] =ObjDict()
            if '.' in k: # insert row is inside a document
                lead,end = k.split('.',1)
                #source = self._sources[k]
                self.maptbl_(k).update(
                    {'_id': self._sources[k].row_id},
                    {'$push':{ end:{}} }
                    )
        self.dbRows_+=[newrow]
        self.changes_ += [ModelStatus(ActionType.Insert)]

        row = self[last]
        # for fldk in row.fields_  removed as required by VIEW-71:
        #     fld = row.fields_[fldk]
        #     if fld._default is not None:
        #         fld.value = fld._default
        return row

    def __len__(self):
        return len(self.dbRows_)

    def loop_(self,section=Section.all,case=Case.viewAll ):

        group = [self.fields,self.head,self.main.self.foot][section]
        for field in group:
            if field.cases is None or case in field.cases:
                yield field

    def __iter__(self):
        return self.fields_.loopRows()

    def getRows_(self,*args,**kwargs):
        """ overwrite getRows to retrieve rows from db within the views of
        db typical from the application
        default 'getrows' is to assume args0 is a dictionary and simply
        take args[0] as dict to find within modelName_
         note: view can have no rows at all

         two types of result are permitted for getRows_ methods
         either a list of ObjDicts - where each dict is itself a dictionary
         of fields from each source,  or for a 'single source' view, the raw
         result of a find will be converted to the list of dictionaries by the 
         calling init method.
        """
        model= self.default_dbRowSrc_
        if model and args:
            find = args[0]
            if not isinstance(find,dict):
                find= {}
            return model.find(find)
        else:

            return [] if not args else args[0]


    def __json__(self, internal=False):
        res = ObjDict(
                    className = self.__class__.__name__,
                    viewName = self.safeName_,
                    idx = self.idx_,
                    data = [row.__json__(True) for row in self],
                    fields = self.fields_
        )
        
        if not internal:
            res=str(res)
        return res

    def labelsList_(self):
        """ list of the labelfields from dbRows
        """
        # print([ getattr(row,self.rowLabel) for row in self.dbrows])
        labelList = []

        for row in self:
            # first, try get it from `rowLabel_`
            try:
                row_label = getattr(row, 'rowLabel_')
            except AttributeError:
                row_label = None

            # second, if no value, we try look for the `rowLabel`
            if not row_label:
                for key, value in row.view_._baseFields.items():
                    if value.rowLabel:
                        row_label = getattr(row, value.name) 
                        break

            # finally, we add it to the list
            if row_label:
                labelList.append(row_label)
            else:
                labelList.append('no labels')

        return labelList

    def __getitem__(self, idx):
        if idx > len(self):
            raise IndexError("Index value '{}' is out-of-range! View has {} item(s).".format(idx, len(self)))
        return ViewRow(self, idx)

    def log_journal(self):
        def get_model_name(obj):
            if hasattr(obj, 'viewName_'):
                return obj.viewName_
            else:
                return "_" + obj.__class__.__name__

        def setup_logger(name):
            formatter = logging.Formatter(
                '%(asctime)-15s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            folder = os.path.join('..', 'journals')
            if not os.path.isdir(folder):
                os.makedirs(folder)
            log_file = os.path.join(folder, name + '.log')

            handler = RotatingFileHandler(log_file, maxBytes=20480000)
            handler.setFormatter(formatter)

            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
            logger.addHandler(handler)

            return logger

        if not self.should_journal:
            return

        model_logger = setup_logger(get_model_name(self))
        model_logger.info(ObjDict.dumps(self.changes_))

    def deprecmkList(self, rows=None, pageName=None):
        """ replacement for listTbl -expects mako to format
        handles returning whole row, but also used to give list of labels.
        this version only handles list of labels
        """
        if not rows:
            rows = self.fetchAll(**self.mapRowSpec())  # do a

        def arow(n, row):
            return n, pageName, ','.join([row[listField] for listField in self.listFields])

        return [arow(n, row) for n, row in enumerate(rows)]
