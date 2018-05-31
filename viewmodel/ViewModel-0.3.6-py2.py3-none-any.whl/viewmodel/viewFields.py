# 2.02 feb 2008
# improved editDrawN  for arrays to handle display as well as edit

#import saltSqlaDB
from decimal import Decimal
from bson.objectid import ObjectId

try:
    import saltMongDB as viewModelDB
except ImportError:
    # from .
    import viewmodel.viewMongoDB as viewModelDB

import datetime
from collections import namedtuple

from itertools import count
from objdict import combiParse, unParse, ObjDict, Struct, OEnum
from enum import Enum, EnumMeta
Case = Enum('ViewCase', 'viewAll viewOne edit allFields')
# 'edit' in Case.__members__    viewAll is for viewAll rows


class ModelStatus(dict):
    def __init__(self, action=None, **kwargs):
        super().__init__(**kwargs)

        if action is not None and not isinstance(action, ActionType):
            raise ValueError('Expected type of `action`: None or `ActionType`')

        self.action = action


class ActionType(OEnum):
    Insert = 1
    Delete = 2


def noBlanks(plist):
    return [p if p else '<blank>' for p in plist]


class FieldItem:

    def __init__(self, viewObj, field, row_index):
        ''' viewobj is obj containing value and prop is property '''
        self.viewObj = viewObj
        self.field = field
        self.types = FieldTypes()
        self.idx = row_index

    def __getattr__(self, name):
        return getattr(self.field, name)

    def __json__(self, internal=False):

        fields_dict = {
            'class_string': str(self.field),
            'idx': self.idx,
            'cases': self.field.cases,
            'hint': self.field.hint,
            'label': self.field.label,
            'fmt': self.field.fmt,
            'misc': self.field.misc,
            'name': self.field.name,
            'postID': self.field.postID,
            'postPrefix': self.field.postPrefix
        }

        if isinstance(self.Type, EnumMeta):
            fields_dict['type'] = 'Enum'
            fields_dict['items'] = []

            for item in self.Type:
                fields_dict['items'].append({
                    item.name: item.value
                })

        res = fields_dict

        if not internal:
            res = str(fields_dict)

        return res

    @property
    def Type(self):
        return self.field.Type(self.viewObj)

    @property
    def fieldatt(self):
        """since get attr looks in field, this should not be needed
           other than to make what is happening clearer in code
        """
        return self.field

    @property
    def value(self):
        return self.field.__get__(self.viewObj, None, self.idx)

    @value.setter
    def value(self, svalue):
        self.field.__set__(self.viewObj, svalue, self.idx)

    @property
    def strvalue(self):
        val = self.field.__get__(self.viewObj, None, self.idx)
        val = self.field.toStr(val)
        return str(val)

    @strvalue.setter
    def strvalue(self, svalue):
        '''note it could be that __set__ handles str format anyway
          actual class may override either, but no need to do both'''
        self.field.__set__(self.viewObj, self.field.Type(self.viewObj)(svalue),
                           self.idx)


class BaseField(object):
    """ fm elts make up the screen of fmpages
    elts may refer to data from the database table- or not!
    """
    """
    take II - to be rename FmCols or XxxCols with the base as BaseCol
    Cols are logical fields in the db. They may be direct db cols (db=True)
    or calculated from other columns.
    Columns with that are only used to calcuate other columns have form=False

    a dictionary of Cols derived from basecol is needed by a SaltTable to enable
    the salttable to do the following:-
      for every logical 'col' - render a html view of the data
                            - render an html input form of the data
                            -render a default label
                            -render a hint
                            -xtract new values from post data from an earlier input render
        salt tables have a 'render' method to perform those tasks - see saltTable class

    """
    clsCounter = count(0)
    def __init__(self, label=None, maxim=16, wide=0, hint="", *, hint2='', name=None, src='',
                 rowLayout='[xx]', fmt={}, edit=True, readOnlyBracket="  ", db=None, row=None,
                 form=True, misc=None, colwidth=0, postPrefix='field', value=None, posn=0,
                 comment="", rowLabel=False, key=None, cases=None):
        """
        'src' is where the data is located - by default this is assumed to be in the first
             database rows of the container view class.  Set src=None for fields with no external source.
        'name' is the field name matches sql row db(where relevant - sql). Normal name is not provided
            as a paramter, and calculated from the name of attribute the field is assigned to
            If 'src' is not None and name is not in the rows provided, then an error will result
            for MongoDB src can indicate the object containing the field

        label is the display version of the name-None for use name, empty string for blank

        maxim is the maximum field width
        wide is the display width
        hint,hint2 hint is for 'help' type display...hint2 may be deprecated or reused for long verison
        rowLayout  - deprecated!
        fmt: contains field postPrefix, width etc plus sub field information
            -(eg enum texts)see indivdual fld types for more details


        ---> deprec fields follow!
        edit is now deprecated...it is decided by the view ???
        readOnlyBracket ...still in use for wrapping 'd'isplay views...could be a render parm?


        db - dbTable that field is in. Can be set after __init__. Cols can also exist without a table
                set as '' at init(rather than None) to have no table & prevent setname setting a valid db

        row - same rules as db- and moving to supercede db so db is extracted from row
            the row object holds all col entries in a dict. thus a datatable can have 
            several active rows each having a its own set of cols .

        form is a bool- field existing on the form but not in db?
        posn is the character position within the field. A single text dbfield can support
            a set of logical cols (bool and scalar cols support this) allowing 'flags' contain
            several subelements

        value is taken as the initial value.  The insert_ method uses this value to initialise
            new fields in inserted rows.  Note 'None' values are ignored, and one insert_()
            occurrs automatically for DBNoSource sources so by default the 'value' will appear.

        <---- end of deprec

        misc is for use by individual derived classes
        colwidth ...tba(but it is in use)

        postPrefix... the string to use when to avoid display id clashes
        postID:   a property retrieveing the field name with the postPrefix attached


        _value - the data content. None indicates it should be loaded from the dbTable.data
        value: property for actual value
        strvalue: property for 'str' version of value. Obtain str formated for display and parse str
            in order to set value


        comment is just that- allows adding a comment. nothing is done with the comment at this time

        rowLabel:  True if use this field is a label for the row

        cases:
           if not None (all cases) then this is the cases in which the field is to be included in iteration
           (as per 'Case' type posibilities)

        viewobj:  the view object this field is on - set during 'setup' which is called from viewObject.

        deprecated:
           key is the key in the columns dict - not the db key (which is name).
            This allows for virtual cols with different keys than the dbcol name
        )"""
        #self.instanceNum = self.clsCounter
        #self.__class__.clsCounter += 1
        self.instanceNum = next(self.clsCounter)
        #print('instance field label:{} count:{}'.format(label,self.instanceNum))

        if hasattr(self, 'preInit'):
            self.preInit()
        self.name = name
        self.asked_name = name
        self.src = src
        self.raw_src = src if isinstance(src, str) else ''

        """ deprec for now
        if key:
            self.key=key
        else:
            self.key=name"""

        if src is None:
            self._value = value if value is not None else ''
            # default empty string if no src for column
            # src = None is not a useful way to specify src....
            #  unless perhaps there is a default name for a src of None?

        self._default = value

        self.postPrefix = postPrefix

        self.label = label  # updated at setup
        self.rowLabel = rowLabel

        def hintMap(hint):
            if hint == '' or hint[:1] == ' ':
                return hint
            return '' + hint  # we are adding a <br> here

        self.hint = hintMap(hint)
        self.hint2 = hintMap(hint2)
        self.cwidth = colwidth
        self.posn = posn

        if wide == 0:
            wide = maxim
        self.fmt = {'size': wide, 'max': maxim,
                    'postPrefix': postPrefix, 'readOnlyBracket': readOnlyBracket}
        self.fmt.update(fmt)

        self.layout = {}  # 2015  is this deprecated?
        # if hasattr(rowLayout,'islower'):#test for string
        #   self.layout={'row':rowLayout}
        # else:
        #   rowLayout['row']=defVal(rowLayout,'row','[xx]')
        #   self.layout=layout
        # self.readOnlyBracket=readOnlyBracket

        # 2015 ....following enties
        self.noEdit = not edit
        self.edit = edit
        # self.mkFmtStrs(rowLayout)
        # self.labelStr=self.mkLabelStr()
        # self.fieldStr=self.mkFieldStr()
        # self.rowBracks()

        # self.dbTable=db
        # self.row=row

        if name == "":
            self.db = False
        self.misc = misc if misc else {}

        self.cases = cases
        return

    def __get__(self, obj, objtype=None, idx=None):
        """ field could be local, could be direct in view.rows_,
            or each row could have multiple documents from separate collections
            with 'source' indicating the relevant collection: effectively a join
            'Lazy' get allows retrieving the data from the collection on demand
            where 'joins_' is set to indicate which collections

            the format returned by get is the 'working format' of the type
            this is the type of the value from the perspective of programs
            doing calcualtions with the value

            idx is the row to be accessed
        """
        #import pdb; pdb.set_trace()
        if idx is None:
            if len(obj.dbRows_) > 1:
                raise TypeError("cannot read direct from multi element view")
            idx = 0 # we have just ensured only 1 row maximum
        if obj is None:  # test if called from class not instance
            return None
        #prrint('Retrieving {} from row {}'.format( self.name,obj.old_idx_))
        if True: # self.src is not None: # None as legacy indicator of 'no source'
            if True: #isinstance(self.src, str):
                src_nm = obj._source_list[self.src]
                if src_nm not in obj.dbRows_[idx]:
                    obj._sources[src_nm].loader(idx)
                srcdict = obj.dbRows_[idx][src_nm]
                for embed in self.src_dicts:
                    srcdict = srcdict.get(embed, {})
                return srcdict.get(self.name, self.default(obj))
                #        ,self.name)
            return obj.dbRows_[idx].get(self.name, self.default(obj))
            # return getattr(obj.dbRows_[obj.old_idx_],self.name)
        return self._value

    @staticmethod
    def toStr(val):

        return str(val)

    @staticmethod
    def storageFormat(data):
        """ convert data from format returned by get, to raw database format
          this is the placeholder for routines specific to derived classes"""
        return data

    def __set__(self, obj, val, idx_=None):
        """as a base method this assumes 'val' is in the format data comes __get__()
          overides must handle 'txt' or format from __get__(), then call this method
          may also need to overide storage format to reverse mapping from db in get"""
        #print('Updating', self.name)
        if idx_ is None:
            # if hasattr(obj,'idx_'):  #checking quack better than checking type
            #    idx_= obj.old_idx_
            if len(obj) > 1:
                raise ValueError('Cannot set multi row view')
            else:
                idx_ = 0
        if True: #self.src:
            if val != self.__get__(obj, None, idx_):
                # print(' it is changed?',val,self.__get__(obj),val!=self.__get__(obj))
                old_v = self.__get__(obj, None, idx_)
                v = self.storageFormat(val)
                if True: # isinstance(self.src, str):  # was always false for mongo- not now!
                    src_nm = obj._source_list[self.src]
                    store_location = obj.dbRows_[idx_].get(src_nm)
                    for embed in self.src_dicts:
                        if not embed in store_location:
                            store_location[embed] = {}
                        store_location = store_location[embed]
                    store_location[self.name] = v
                    if v != old_v:
                        change_row = obj.changes_[idx_]
                        if not src_nm in change_row:
                            change_row[src_nm] = ModelStatus()
                        name = '.'.join(self.src_dicts +[self.name])
                        change_row[src_nm][name] = v
                else:
                    obj.dbRows_[idx_][self.name] = v
                    obj.changes_[idx_][self.name] = v
        else:
            self._value = val

    def setup(self, name, sampleRow, view):
        self.container_name = name
        if self.name is None:
            self.name = name
        src = self.src
        if not isinstance(src, int):
            try:
                self.src = view._source_list.index(self.src)
            except ValueError:
                self.src = 0
        self.src_name = view._source_list[self.src]
        self.src_dicts = view._sources[self.src_name].map_src(self.raw_src)
        # if self.src is None:
        #     self._value = ''  # code to establish src in the field
        # elif self.src == '':
        #     #if view.joins_:
        #     self.src = view.row_name_  # use default
            #else:
            #    self.src = True

            # for dbrow in obj.dbrows:  any loop should be for compound names
            # self.src=True  #2016-03 mongo simpler but no check for in row
            # elif view.joins_:
            #     dirs=[(dir(getattr(sampleRow,j)),j)
            #         for j in view.joins_]
            #     #print('the dirs',dirs)
            # else:
            #     dirs=[(dir(sampleRow),True)]
            # for the_dir,src in dirs:
            #     if name in the_dir:
            #         self.src=src #obj.dbrows_
            #         break
            #     #if self.src:
            #     #    break
            # else:
            #     print('dir sam',dir(sampleRow))
            #     raise KeyError("View Field {}:{} not found in database".format(
            #             view.viewName_,name))
            # #if name=='id':
            #     #print('name the src',name,self.src,view.viewName_)
            # assert self.src != '','got though view setup with weird not found'
            # if self.src=='':
            #     print('got though setup with weird not found')
        if self.label is None:
            self.label = self.name
        if self.rowLabel:
            view.__class__.rowLabel_ = name

        return self.name

    @property
    def postID(self):
        return self.postPrefix + self.container_name

    def Type(self, obj):
        return str

    def default(self, *args):
        return self._default

    ##############################################
    # below here fns not updated to fields yet


# ================================================================================================
NameVals = namedtuple('NameVals', 'names values')


class EnumField(BaseField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._default = None
        self._Type = None

    def nameVals(self, obj):
        if not 'values' in self.fmt:
            self.fmt['values'] = list(range(1, len(self.fmt['names']) + 1))
        return NameVals(self.fmt['names'], self.fmt['values'])

    def __get__(self, obj, objtype=None, idx=None):
        res = super().__get__(obj, objtype, idx)
        if res is None:
            return None
        #print("ok did the get",res)
        #print('self defau',self.default(obj).value)
        if isinstance(self.default(obj).value, int):
            #print('default is int!')
            # if values are int ensure working with int
            #print('enum get int',res)
            res = int(res)

        try:
            #print('bout to get tyoe')
            Type = self.Type(obj)
            #print('got the type',Type)
            return Type(res)
        except ValueError:
            return self.default(obj)

    def Type(self, obj):
        """ a property to defer buiding type until actually needed"""
        #print('enum type')
        if not self._Type:
            # defer building type until needed
            nameVals = self.nameVals(obj)
            # print('namvale',nameVals,self.label)
            self._Type = Enum(self.label, zip(
                noBlanks(nameVals.names), nameVals.values))
        #print('at enum tr')
        #print('enum type return',self._Type,self.name)
        return self._Type

    def default(self, obj):
        if not self._default:
            Type = self.Type(obj)
            self._default = Type(self.nameVals(obj).values[0])
        return self._default

    @staticmethod
    def storageFormat(data):
        """ convert data from format returned by get, to raw database format """
        return data.value

    def __set__(self, obj, val, idx_=None):
        """as a base method this assumes 'val' is in the format data comes __get__()
          overides must handle 'txt' or format from __get__(), then call this method
          may also need to overide storage format to reverse mapping from db in get"""
        if isinstance(val, str):
            if isinstance(self.default(obj).value, int):
                print('isint')
                val = int(val)
            if val in self.Type(obj).__members__:
                val = self.Type[val]  # case of name
            else:  # prefer to have value
                val = self.Type(obj)(val)
        super().__set__(obj, val, idx_)


class EnumForeignField(EnumField):
    """ the field is an index into another table
    the contents of the field is restricted to being one of the field
    values in the other table (a foreign key), or an index into the
    other table.
    If a filter is specified, then the field can only reference rows in the
    other table that match the filter.
    The field value is restricted to having the values contained in the 'values'
    field of the other table,
    .  or
    valid index (1...6 if there are six values) plus optionally 'zero' if 'zero text is supplied.

    The 'values' parameter either specifies the column in the other table containing the
    possible field values. If values = none then values are just indexes into the list.
    """

    def __init__(self, *args, zeroText=None, values=None, dispFields=(), session=None, saltFilter=None, sqfilter=None, **kwargs):
        """load possible values from other table, question is when to reload!
        if 'values' is none, then values as range of possibles """
        self.zeroText = zeroText
        self.values = values
        if not isinstance(dispFields, (list, tuple)):
            raise TypeError('dispfields should be a list')
        self.dispFields = dispFields
        self.session = session
        self.sqfilter = sqfilter
        self.saltFilter = saltFilter

        super().__init__(*args, **kwargs)

    def nameVals(self, obj):
        #prrint('enff namevals',self.name,self.dispFields)
        firstDisp = self.dispFields[0]
        if not isinstance(firstDisp, str):
            raise TypeError("Dispfield for Emum Foreign not SQLA Field")
            # print('typeok')
        self.xtable = self.session.baseDB.db.get_collection(
            viewModelDB.pclass(firstDisp))  # table name
        filt = {}
        try:
            if self.saltFilter:
                filt = {self.saltFilter: obj.salt}
        except (AttributeError) as e:
            print('at catchall?', e.__doc__, e)
            #print (e.message)

        # session.query(self.xtable)
        rows = [r for r in self.xtable.find(filt)]

        # if self.sqfilter:
        #    rows = rows.filter(self.sqfilter())
        #rows = rows.all()
        #print("len rows nv",len(rows))

        values = self.values
        if '.' in values:
            #print('dir val',dir(values))
            values = viewModelDB.key(values)

        baseNms, baseVls = ([], []) if not self.zeroText else(
            [self.zeroText], [0])
        # print('bases',baseNms,baseVls)
        values = baseVls + [row[values] for row in rows
                            ] if values else [*range(1, len(rows) + 1)]

        names = baseNms + [', '.join([row[viewModelDB.key(dispField)]
                                      for dispField in self.dispFields])
                           for row in rows]
        Res = NameVals(values=values, names=names)
        # print('resnv',Res,Res.values,Res.names)
        return Res


# all below here not in current format yet

BaseCol = BaseField


# ======================================================================

YMD = namedtuple('YMD', 'y m d')


def strToDate(val):
    swap = False
    for char in ':/-':
        if char in val:
            swap = True
            res = YMD(*(val.split(char)))
            break
    else:
        # no separator found assum ddmmyy
        if len(val) == 4:  # expiry date?
            res = YMD('20' + val[2:], val[:2], 1)
        elif len(val) == 6:
            res = YMD('20' + val[4:], val[2:4], val[:2])
        elif len(val) == 8:
            res = YMD(val[4:], val[2:4], val[:2])
        else:
            raise ValueError(
                'Cannot conver str to date: no separator found and bad lenght')
    try:
        res = YMD(*(int(a) for a in res))
    except ValueError:
        raise ValueError('date with non integer part')
    if swap and res.y < 32:
        res = YMD(res.d, res.m, res.y)
    return datetime.datetime(*res)

def strToTime(val):
    swap = False
    for char in ':/-':
        if char in val:
            swap = True
            res = val.split(char)
            break
    else:
        # no separator found assum hhmmss
        if len(val) == 4:  # expiry date?
            res = val[:2], val[2:]
        elif len(val) == 6:
            res = val[:2], val[2:4], val[2]
        else:
            raise ValueError(
                'Cannot conver str to time: no separator found and bad lenght')
    return datetime.datetime(1, 1, 1, *[int(i) for i in res])

def strToDateTime(val):
    if ' ' in val:
        da, ti = val.split(' ', 1)
        da = strToDate(da)
        ti = strToTime(ti)
        return datetime.datetime.combine(da.date(), ti.time())
    return strToDate(val) #no separator....just date?

class DateTimeField(BaseField):
    """ raw database format is 'datetime.date'
       get is ok- returns date time.date
       getstr coulc format better

       fmt['date'] sets how datetimes are converted to str
       which allows converting to date or time or any format
       fields are per  strftime().  Currently supported are
          d m Y H M S, as well as B(month name) and A(day name)
            use [-2:] to truncate Y or [-3:] to truncate B or A
            eg '{d}/{m}/{Y[-2:]}'
        when converting from string, the format examined first
        if fmt has a 'd' but no 'H' it is assumed to be a date only field
        if fmt has an 'H' but no 'd' it is assumed to be a time only field.
       """
    months = ('January', 'February', 'March', 'April',
              'May', 'June', 'July', 'August', 'September',
              'October', 'November', 'December')
    days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday',
            'Friday', 'Saturday', 'Sunday')

    def __get__(self, obj, objtype=None, idx=None):
        res = super().__get__(obj, objtype, idx)
        # print('datetype', type(res), res)
        return res

    @staticmethod
    def storageFormat(data):
        """ convert data from format returned by get, to raw database format """
        return data

    def __set__(self, obj, val, idx_=None, converter=strToDateTime):
        """as a base method this assumes 'val' is in the format data comes __get__()
          overides must handle 'txt' or format from __get__(), then call this method
          may also need to overide storage format to reverse mapping from db in get"""
        # print('Datefild',type(val),val)
        #import pdb; pdb.set_trace()
        if isinstance(val, datetime.datetime):
            pass  # nothing to do
        elif isinstance(val, datetime.date):
            val = datetime.dateime.combine(val, datetime.time(0, 0, 0))
        elif isinstance(val, datetime.time):
            val = datetime.dateime.combine(datetime.date(1, 1, 1), val)
        elif isinstance(val, str):
            val = converter(val)
        else:
            raise ValueError('Date must be str or datetime.date')
        super().__set__(obj, val, idx_)

    def toStr(self, value):
        if value is None: return ""
        date = self.fmt.get('date', '{d:2}/{m:02}/{Y} {H}:{M:02}:{S:02}')
        dt = value  # self.__get__(self.viewObj)
        return date.format(**dict(d=dt.day, m=dt.month,
                                  Y=str(dt.year).rjust(4, '0'),
                                  H=dt.hour, M=dt.minute, S=dt.second,
                                  B=self.months[dt.month], A=self.days[dt.weekday()]))


class DateField(DateTimeField):
    """ set fmt[date] with a 'd' but without and 'H' (hour)field,
        and you have a date that does not expect the time on input
    """

    def __init__(self, *args, **kwargs):
        fmt = kwargs.get('fmt', {})
        if not 'date' in fmt:
            fmt['date'] = '{d:2}/{m:02}/{Y}'
            kwargs['fmt'] = fmt
        super().__init__(*args, **kwargs)

    def __get__(self, obj, objtype=None, idx=None):
        res = super().__get__(obj, objtype, idx)
        #print('datetype', type(res), res)
        return res.date() if res else res

    def __set__(self, obj, val, idx_=None):
        super().__set__(obj, val, idx_, strToDate)

    def toStr(self, value):
        date = self.fmt.get('date', '{d:2}/{m:02}/{Y}')
        dt = value  # self.__get__(self.viewObj)
        if value is None: return ""
        return date.format(**dict(d=dt.day, m=dt.month,
                                  Y=str(dt.year).rjust(4, '0'),
                                  B=self.months[dt.month], A=self.days[dt.weekday()]))



# ======================================================================

class TimeField(DateTimeField):
    """ set fmt[date] with a 'd' but without and 'H' (hour)field,
        and you have a date that does not expect the time on input
    """

    def __init__(self, *args, **kwargs):
        fmt = kwargs.get('fmt', {})
        if not 'time' in fmt:
            fmt['time'] = '{H}:{M:02}:{S:02}'
            kwargs['fmt'] = fmt
        super().__init__(*args, **kwargs)

    def __get__(self, obj, objtype=None, idx=None):
        res = super().__get__(obj, objtype, idx)
        return res.time() if hasattr(res, 'time') else res

    def __set__(self, obj, val, idx_=None):
        super().__set__(obj, val, idx_, strToTime)

    def toStr(self, value):
        if value is None: return ""
        tdate = ' {H}:{M:02}'
        dt = value  # self.__get__(self.viewObj)
        return tdate.format(**dict(H=dt.hour, M=dt.minute, S=dt.second))


# ============================================================================


class AmtCol(BaseCol):

    def fromStr(self, pstr):
        "import from amt form"
        return saltInt(digits(pstr))

    def amtFmt(self, thenum):
        """ should check places etc...from format...skip for now"""
        theint = saltInt(thenum)
        return "$%i.%02i" % (theint / 100, theint % 100)

    def drawXXX(self, page, dtbl={}):  # fmdrawitem
        """(row,flds,key,rowfmt)"""
        # #dumpit($fld,'flds');
        tbl = page.table
        if dtbl == {}:
            data = dbTable.data
        else:
            data = dtbl
        key = self.name

        if self.dbTable:
            self.value = self.amtFmt(data[key])
            # use with try if data from dies?-> self.value=self.amtFmt(data[key])
        # str+=self.drawClose(tbl)
        return self.drawWrapped(self.baseDraw(key, self.value), tbl)

    def extractXXX(self, postData, tablee=None):
        r1 = BaseCol.extract(self, postData, self.dbTable)
        fld = digits(r1[0][1])
        return [(r1[0][0], fld), ]

# ===============================================================================


class BinTxtCol(BaseCol):
    # def __init__(self,name,label,maxim=16,hint="",rowLayout='[xx]',noEdit=False,readOnlyBracket='  '):
    #   """(name,max,hint,rowLayout) returns std array- wrong class """
    #   BaseCol.__init__(self,name,label,maxim,hint,rowLayout)
    #   self.noEdit=noEdit
    #   self.ftype='txt'
    #   if readOnly:self.readOnly=True
    #   self.readOnlyBracket=readOnlyBracket

    def drawXXX(self, page, dtbl={}):  # fmdrawitem
        """(row,flds,key,rowfmt)"""
        # #dumpit($fld,'flds');
        tbl = page.table
        if dtbl == {}:
            data = dbTable.data
        else:
            data = dtbl
        key = self.name

        if self.dbTable:
            self.value = data[key]
        # str+=self.drawClose(tbl)
        return self.drawWrapped(self.baseDraw(key, self.value), tbl)

#************************************************************
# id fields
#
class IdField(BaseField):
    """ see IdDAutoField for old sql mapping
    now maps field name 'id' to '_id' and that is all
    now only maped is no 'name' was asked for in init
    """

    def __get__(self, obj, objtype=None, idx=None):
        if self.name == 'id' and self.asked_name is None:
            #odict = obj.dbRows_[obj.old_idx_]
            # fld=obj.fields_[self.name] - which name to set?
            #self.name = 'sqlid' if 'sqlid' in odict else '_id'
            self.name = '_id'
        res = super().__get__(obj, objtype, idx)
        # print('int get',type(res),res) does not work for 'None' result
        return res

    def __set__(self, obj, val, idx_=None):
        if not isinstance(val, ObjectId):
            val = ObjectId(val)
        super().__set__(obj, val, idx_)

    @staticmethod
    def id_dict(id):
        if isinstance(id, int):
            return dict(sqlid=id)
        else:
            return dict(_id=id)

class IdAutoField(BaseField):
    """ - previously was IdField with the idea that it can
    work to help migration between sqlid and _id.  for get,
    return sqlid if present, otherwise return _id.
    for set??, set _id if type is IdObject, otherwise set sqlid

    does not matter what variable is called or name is set
    field will use 'sqlid' data if present, otherwise '_id'
    """

    def __get__(self, obj, objtype=None, idx=None):
        if True: #self.name == 'id':
            local_idx = 0 if idx is None else idx
            #import pdb; pdb.set_trace()
            odict = obj.dbRows_[local_idx][obj.row_name_]
            # fld=obj.fields_[self.name] - which name to set?
            self.name = 'sqlid' if 'sqlid' in odict else '_id'
        res = super().__get__(obj, objtype, idx)
        # print('int get',type(res),res) does not work for 'None' result
        return res

    @staticmethod
    def id_dict(id):
        if isinstance(id, int):
            return dict(sqlid=id)
        else:
            return dict(_id=id)

# ---------------------

class IntField(BaseField):
    """ raw database format is ???
       get is ok- returns int
       """

    def __get__(self, obj, objtype=None, idx=None):
        res = super().__get__(obj, objtype, idx)
        # print('int get',type(res),res) does not work for 'None' result
        return res

    @staticmethod
    def storageFormat(data):
        """ convert data from format returned by get, to raw database format """
        return data

    def __set__(self, obj, val, idx_=None):
        """as a base method this assumes 'val' is in the format data comes __get__()
          overides must handle 'txt' or format from __get__(), then call this method
          may also need to overide storage format to reverse mapping from db in get"""
        # print('IntField',type(val),val)
        try:
            val = int(val)
        except ValueError:
            raise ValueError('Int value could not convert')
        super().__set__(obj, val, idx_)


# =========================== most common case no binary
class TxtField(BaseField):

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    def __get__(self, obj, objtype=None, idx=None):
        res = super().__get__(obj, objtype, idx)
        return res if res is None else str(res)

    def Type(self, obj):
        return str

    def default(self, obj):
        res = super().default(obj)
        return '' if res == None else res

# =========================== most common case no binary
class ObjDictField(BaseField):

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    def __get__(self, obj, objtype=None, idx=None):
        res = super().__get__(obj, objtype, idx)
        # print('int get',type(res),res) does not work for 'None' result
        return ObjDict(res)

    def __set__(self, obj, val, idx_=None):
        if isinstance(val, Struct):
            val = dict(val.items())
        super().__set__(obj, val, idx_)

    def Type(self, obj):
        return ObjDict

    def default(self, obj):
        res = super().default(obj)
        return ObjDict() if res == None else res


# =========================== most common case no binary
class DecField(BaseField):
    """ currently field uses fixed 2 places,  but places needs to come from 
    location that can be set from counry of store.  current idea is in 
    format internal value to format could be set at any time."""
    def __init__(self, places=0, *args, **kargs):
        super().__init__(*args, **kargs)
        self.places = places

    def Type(self, obj):
        return Decimal

    def __get__(self, obj, objtype=None, idx=None):
        res = super().__get__(obj, objtype, idx)
        # print('int get',type(res),res) does not work for 'None' result
        return Decimal(res)/100

    @staticmethod
    def storageFormat(data):
        """ convert data from format returned by get, to raw database format
        rawdatabase format for decimals is int.  number of places to be added """
        if isinstance(data, Decimal):
            data = int(data*100)
        return data

    def default(self, obj):
        res = super().default(obj)
        return Decimal(0) if res == None else res

# ==================================================================================
class TxtListField(BaseField):
    """methods here work for top level item - which is a list
        methods to work with elements to be added
    """

    def Type(self, obj):
        return list

    def default(self, obj):
        res = super().default(obj)
        return [] if res == None else res
    # def __get__(self, obj, objtype=None):
    #     res = super().__get__(obj,objtype)
    #     #res = ",".join(res)
    #     return res

    @staticmethod
    def toStr(val):  # called by .strValue for use in forms etc
        return ", ".join(val)

    @staticmethod
    def storageFormat(data):
        """ convert data from format returned by get, to raw database format """
        if isinstance(data, str):
            data.replace(', ', ',')  # strip padding following ','
            return data.split(",")
        return data

    def __xxset__(self, obj, val, idx_):  # on hold in case we need it
        """as a base method this assumes 'val' is in the format data comes __get__()
          overides must handle 'txt' or format from __get__(), then call this method
          may also need to overide storage format to reverse mapping from db in get"""
        print('IntField', type(val), val)
        try:
            val = int(val)
        except ValueError:
            raise ValueError('Int value could not convert')
        super().__set__(obj, val, idx_)


class ObjListField(BaseField):
    """methods here work for top level item - which is a list
        methods to work with elements to be added
    """

    def Type(self, obj):
        return ObjDict()

    def default(self, obj):
        res = super().default(obj)
        return [] if res == None else res
    # def __get__(self, obj, objtype=None):
    #     res = super().__get__(obj,objtype)
    #     #res = ",".join(res)
    #     return res

    @staticmethod
    def toStr(val):  # called by .strValue for use in forms etc
        return unParse(val)

    @staticmethod
    def storageFormat(data):
        """ convert data from format returned by get, to raw database format """
        if isinstance(data, str):
            try:
                return combiParse(data)
            except:
                return []
        return data


class BaseArrCol(BaseCol):
    """ either single dbcol arrarys using split or multi col arrays
    minElts is the minimun size, maxElts is the maximum allowed

    """
    # def preInit():
    #   if rowLayout=='-xx-' and label=='':rowLayout='--x-'
    #   BaseCol.__init__(self,name=name,label=label,rowLayout=rowLayout,misc=misc)

    def fromStr(self, pstr):
        if isinstance(pstr, list):
            return pstr
        return pstr.split(',')

    def iterator(self, width, tbl=None):
        return self.iteratorBase(len(self.getValue(self.dbTable)), width)

    def getValue(self, tbl=None):
        if self.dbTable and self.value == None:
            self.value = self.dbTable.txtArr(self.name, defVal(
                self.misc, 'minElts', 0), defVal(self.misc, 'maxElts', 100))
        return self.value

    def putValueInDb(self, tbl=None, strVal=None, idx=None):
        if strVal != None:
            self.value = self.fromStr(strVal)
        row = self.row
        if not row:
            row = self.dbTable.data

        # if self.dbTable and self.value!=None: -> self .dbtable set for both
        # anyway?
        if self.dbTable and self.value != None:
            ret = row.colToDb(self.name, '-'.join(self.value))
            return ret
        return row.colFromDb(self.name, "")

    def valueEqDb(self, tblxxDeprec=None):
        if not(self.dbTable) or self.value == None:
            return True  # can't put it in table...so effectively same value

        row = self.row
        if not row:
            row = self.dbTable.data

        return row.colFromDb(self.name) == '-'.join(self.value)
        # return self.dbTable.data[self.name]=='-'.join(self.value)
    # def thevals(self,tbl):
        # debecho('valsec',tbl.numArr(self.name
        #       ,defVal(self.misc,'minElts',0),defVal(self.misc,'maxElts',100)),self,dbTable.data)
        # if self.value!=None:
    #   return tbl.numArr(self.name
    #           ,defVal(self.misc,'minElts',0),defVal(self.misc,'maxElts',100))

    def editDrawN(self, key, val, table=None, idx=None, edit=True, fmt=None):
        # debecho('vvvVv',repr(self.thevals),self.thevals(),self,table.data)
        if edit:
            return self.baseDraw(key + str(idx), self.getValue(self.dbTable)[idx])
        else:
            return self.dispDraw(key + str(idx), self.getValue(self.dbTable)[idx])

    def extractPost(self, postData, tablex=None):
        """ extract this field from post data- form level validity done elsewhere
        this array version will only be called once for all postdata since only one array Col
        """
        table = self.dbTable
        idx = 0
        vals = []
        baseNm = self.fmt['postPrefix'] + self.name
        while baseNm + str(idx) in postData:
            vals.append(postData[baseNm + str(idx)])
            idx += 1
        self.value = self.fromStr(vals)
        return self.value
        # if not self.valueEqDb(table):#self.value!= page.table.data[self.name]:
        #   return [(self.name,self.putValueInDb(table)),]
        # else: return []


class NumArrCol(BaseArrCol):
    """ either single dbcol arrarys using split or multi col arrays
    minElts is the minimun size, maxElts is the maximum allowed

    """

    def fromStr(self, pstr):
        if isinstance(pstr, list):
            return [saltInt(n) for n in pstr]
        return [saltInt(n) for n in pstr.split('-')]

    def getValue(self, tbll=None):  # note -overides to use numArr!
        if self.dbTable and self.value == None:
            self.value = self.dbTable.numArr(self.name, defVal(
                self.misc, 'minElts', 0), defVal(self.misc, 'maxElts', 100))
        return self.value

    def valueEqDb(self, tbll=None):
        if not(self.dbTable) or self.value == None:
            return True  # can't put it in table...so effectively same value
        debecho('tbl data', self.name, self.dbTable.data, self.value)
        row = self.row
        if not row:
            row = self.dbTable.data

        return row.colFromDb(self.name) == '-'.join([str(n) for n in self.value])

    def putValueInDb(self, tbll=None, strVal=None, idx=None):
        if strVal != None:
            self.value = self.fromStr(strVal)
        row = self.row
        if not row:
            row = self.dbTable.data

        if self.dbTable and self.value != None:
            #ret=self.dbTable.data[self.name]='-'.join([str(n) for n in self.value])
            ret = row.colToDb(
                self.name, '-'.join([str(n) for n in self.value]))
            return ret
        return row.colFromDb(self.name, "")
        # return defVal(self.dbTable.data,self.name)
# def preInit():
    #   if rowLayout=='-xx-' and label=='':rowLayout='--x-'
    #   BaseCol.__init__(self,name=name,label=label,rowLayout=rowLayout,misc=misc)
    # def iterator(self,width,tbl):
    #   return self.iteratorBase(len(self.thevals(tbl)),width)

    # def thevals(self,tbl):
        # debecho('valsec',tbl.numArr(self.name
        #       ,defVal(self.misc,'minElts',0),defVal(self.misc,'maxElts',100)),self,dbTable.data)
    #   return tbl.numArr(self.name
    #           ,defVal(self.misc,'minElts',0),defVal(self.misc,'maxElts',100))

    # def editDrawN(self,key,val,table,idx=None,edit=True,fmt=None):
        # debecho('vvvVv',repr(self.thevals),self.thevals(),self,table.data)
    #   return self.baseDraw(key+str(idx),self.thevals(table)[idx])

    def drawXXX(self, page):
        tbl = page.table
        res = self.brack('o') + self.labelStr()
        i = 0
        if not isinstance(self.name, str):
            """ an array of field names instead of a single array
              in this style all fields are in separate dbcols  """
            elist = [(name, dbTable.data[name]) for name in self.name]
        else:
            vals = self.val(tbl)
            elist = zip([self.name + str(i) for i in range(len(vals))], vals)
        # need to return list of names and vals for either case
        for key, val in elist:
            res += self.fieldStr() % self.baseDraw(key, val)
            i += 1
        return res + self.brack('c')


class TxtArrCol(BaseArrCol):
    """ either single dbcol arrarys using split or multi col arrays
    minElts is the minimun size, maxElts is the maximum allowed

    """
    # def preInit():
    #   if rowLayout=='-xx-' and label=='':rowLayout='--x-'
    #   BaseCol.__init__(self,name=name,label=label,rowLayout=rowLayout,misc=misc)
    # def iterator(self,width,tbl):
    #   return self.iteratorBase(len(self.thevals(tbl)),width)
    # def thevals(self,tbl):
    # debecho('valsec',tbl.numArr(self.name
    #       ,defVal(self.misc,'minElts',0),defVal(self.misc,'maxElts',100)),self,dbTable.data)
    #   return tbl.numArr(self.name
    #           ,defVal(self.misc,'minElts',0),defVal(self.misc,'maxElts',100))

    # def editDrawN(self,key,val,table,idx=None,edit=True,fmt=None):
    # debecho('vvvVv',repr(self.thevals),self.thevals(),self,table.data)
    #   return self.baseDraw(key+str(idx),self.thevals(table)[idx])


# ==========================================================================
PosnField = BaseField


class BoolFlagCol(PosnField):

    def __init__(self, name, label, hint="", rowLayout='--x-', edit=True, readOnlyBracket=' ', fmt={}, posn=0, char='y', **dargs):
        """  label is not passed to low level and rowlayout assumes no separate label
            this allows for label to be in with the data as is normal for tick box
            ok make it a 'db' col if posn 0- avoids repeats """
        # fmt.update(dict(postPrefix='bool')
        BaseCol.__init__(self, name, label, hint=hint, rowLayout=rowLayout,
                         edit=edit, readOnlyBracket=readOnlyBracket, fmt=fmt, posn=posn, **dargs)
        self.fldlabel = label
        self.posn = posn
        self.char = char
        return

    def boolname(self, fmt):
        return fmt['postPrefix'] + self.name + str(self.posn) + self.char

    def getValue(self, tbll=None):
        row = self.row
        if not row:
            row = self.dbTable.data

        if self.value == None:
            if self.dbTable:
                self.value = row.colFromDb(self.name)[self.posn:][:1]
                # self.value=self.dbTable.data[self.name][self.posn:][:1]
            else:
                self.value = ' '
        #retv=self.value not in ' -0'
        debecho('bool get v2', self.name, self.value, self.value in ' -0')
        return self.value not in ' -0'

    def draw(self, edit, key, val, tablee=None, fmt=None):  # self,page):
        if not fmt:
            fmt = self.fmt
        tbl = self.dbTable
        checked = ''
        self.getValue()
        data = self.value
        # if len(data)>self.posn and data[self.posn] not in ' -0':
        if data not in ' -0':
            checked = ' checked '
        debecho('booldraw', self.name, self.value, checked)
        res = '<input name="%s" type="checkbox" value="%s" %s>' % (
            self.boolname(fmt), self.char, checked)
        return (res + self.label)  # +self.brack('c')

    def extractPost(self, postData, tablee=None):
        """ extract this field from post data- form level validity done elsewhere"""
        table = self.dbTable
        debecho('epbool', self.name, self.value, table.data, self.row)
        try:
            val1 = [c for c in table.data[self.name]]
        except:
            val1 = []  # case of no record and thus no data
        val2 = "".join(padout(val1, self.posn + 1, '-'))  # .ljust(self.posn+1)
        val = val2

        debecho('xtrabool', val, val1, "x".join(val1), val2,
                self.posn + 1, self.name, table.data, self.fmt, postData)
        try:
            self.value = postData[self.boolname(self.fmt)]
            debecho('xtratest2 b', val, self.name)
        except KeyError:
            self.value = '-'
        return self.value
        # debecho('xtrabbb',val,self.boolname(self.fmt),table.data[self.name],self.posn)

# =============================================================


# ===========================================================================
class TblIdxCol(BaseCol):

    def __init__(self, name, label, xtable=None, zeroText="", idField='id', dispField='label', cursor=None, **others):
        #   """(name,max,hint,rowLayout) returns std array- wrong class """
        BaseCol.__init__(self, name, label, **others)
        self.filterStr = ''
        self.cursor = cursor
        self.xtable = xtable
        self.dispField = dispField
        self.idField = idField
        self.zeroText = zeroText
        return

    def setCursor(self, cursor):
        self.cursor = cursor

    def draw(self, editFlag, key, val, tablee=None, fmt=None):  # draw(self,page): #fmdrawitem
        """(row,flds,key,rowfmt)"""
        def drawOpt(txt, val, sel):
            selstr = ""
            if val == sel:
                selstr = " selected "
            return '<option value="%s" %s > %s </option><br>' % (val, selstr, txt)
        # #dumpit($fld,'flds');
        if not fmt:
            fmt = self.fmt
        tbl = self.dbTable
        row = self.row
        key = self.name
        tstr = ""  # self.drawLabel(tbl)# ;
        if not self.edit:  # simply look up value
            readOnlyBracket = defVal(self.fmt, 'readOnlyBracket', '  ')
            debecho('td noed', tstr, readOnlyBracket)
            sel = ("SELECT %s FROM %s WHERE %s = '%s'"
                   % self.dispField, self.xtable, self.idField, row.colFromDb(key))
            # sel=("SELECT %s FROM %s WHERE %s = '%s'"
            #    % self.dispField,self.xtable,self.idField,tbl.data[key])
            self.cursor.execute(sel)
            data = self.cursor.fetchone()
            tstr += readOnlyBracket[:1] + str(data[0]) + readOnlyBracket[1:]
        else:
            sel = "SELECT %s,%s FROM %s %s ORDER BY %s" % (
                self.idField, self.dispField, self.xtable, self.filterStr, self.idField)
            debecho('idx sel str', sel)
            cursor = self.cursor
            if not cursor:
                cursor = self.row.tbl.cursor
            cursor.execute(sel)
            data = cursor.fetchall()
            # key
            tstr += '<select name="%s">' % (fmt['postPrefix'] + self.name)
            thisVal = self.getValue()  # saltInt(tbl.data[key])
            if self.zeroText:
                tstr += drawOpt(self.zeroText, 0, thisVal)
            for id, lbl in data:
                tstr += drawOpt(lbl, id, thisVal)
            tstr += "</select>"

        # tstr+=self.drawClose(tbl)
        return tstr  # self.drawWrapped(tstr)

    def drawData(self, key, val, tablee=None, fmt=None):  # draw(self,page): #fmdrawitem
        """(row,flds,key,rowfmt)"""
        def drawOpt(txt, val, sel):
            selstr = ""
            if val == sel:
                selstr = " selected "
            return '<option value="%s" %s > %s </option><br>' % (val, selstr, txt)
        # #dumpit($fld,'flds');
        if not fmt:
            fmt = self.fmt  # fmt probably no use with drawData!!
        tbl = self.dbTable
        row = self.row
        key = self.name
        tstr = ""  # self.drawLabel(tbl)# ;
        if False:  # not self.edit:#simply look up value
            readOnlyBracket = defVal(self.fmt, 'readOnlyBracket', '  ')
            debecho('td noed', tstr, readOnlyBracket)
            # sel=("SELECT %s FROM %s WHERE %s = '%s'"
            #    % self.dispField,self.xtable,self.idField,tbl.data[key])
            sel = ("SELECT %s FROM %s WHERE %s = '%s'"
                   % self.dispField, self.xtable, self.idField, row.colFromDb(key))
            self.cursor.execute(sel)
            data = self.cursor.fetchone()
            # return dict(name=self.name,
            #tstr+= readOnlyBracket[:1]+str(data[0])+readOnlyBracket[1:]
        else:
            sel = "SELECT %s,%s FROM %s %s ORDER BY %s" % (
                self.idField, self.dispField, self.xtable, self.filterStr, self.idField)
            debecho('idx sel str', sel)
            cursor = self.cursor
            if not cursor:
                cursor = self.row.tbl.cursor
            cursor.execute(sel)
            data = cursor.fetchall()

            # tstr+= '<select name="%s">' % (fmt['postPrefix']+self.name)#key
            thisVal = self.getValue()  # saltInt(tbl.data[key])
            if self.zeroText:
                vals = [(self.zeroText, 0)]
            else:
                vals = []
            for id, lbl in data:
                vals.append((lbl, id))
            return dict(type='listbox', value=thisVal, name=self.name, choices=vals, label=self.label, hint=self.hint)

        # tstr+=self.drawClose(tbl)
        return tstr  # self.drawWrapped(tstr)

    def fromStr(self, pstr):
        "import from string form"
        debecho('tblidx from str', self.value, pstr)
        self.getValue()
        debecho('tblidx from str2', self.value, pstr)
        if isinstance(self.value, int):
            # values can be int or txt- so decide based on what we have now
            return saltInt(pstr)
        if isinstance(self.value, long):
            # values can be int or txt- so decide based on what we have now
            return saltLong(pstr)
        return pstr


class FieldTypes:
    Enum = EnumField
    Txt = TxtField
    Int = IntField
