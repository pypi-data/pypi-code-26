import hashlib
import random
import time
from collections import namedtuple


import sys
# was debug for imports?
# viewmodi =[ky for ky in sys.modules.keys() if ('viewModel' in ky) or ('oDB' in ky)]
from viewmodel.viewModel import BaseView
from viewmodel.viewFields import (
    TxtField, DateField, EnumForeignField, EnumField, IntField,
    ObjDictField,
    TxtListField, ObjListField, IdField, viewModelDB)

from objdict import ObjDict

from viewmodel import DBMongoEmbedSource

# viewmod =[ky for ky in sys.modules.keys() if ('viewModel' in ky) or ('oDB' in ky)]


Members = viewModelDB.baseDB.db.members
Plans=viewModelDB.baseDB.db.plans
#SaltCards=saltMongDB.baseDB.db.saltcards
Cards=viewModelDB.baseDB.db.cards


SessKey= namedtuple('SessKey',"last start key")


class MemberView(BaseView):
    # a view specifies a fieldset from one or more tables, and all the information to do the
    # reading plus
    viewName_ = "Members"

    models_ = Members

    id = IdField(cases={})
    phoneAtReg = TxtField(None, 16, cases={})
    memberID = TxtField('member name', 32, hint=
            "Your unique member name identies your membership and can be used for log in. "
            "You can change this name, but you cannot chose a name already in use. "
            "It is important to remember this name! If someone 'borrows' your phone- "
            "this name is your only login!")
    password = TxtField(None, 8, cases={})
    notes = TxtField(None, 200, cases={})
    encPass = TxtField(None, 32, cases={})
    quickName = TxtField('Name for Orders', 8, rowLabel=True, hint=
            "This is how your name shows on your orders at the store. The 'order name' must "
            "be short and should be easily read at the store - change this and save to "
            "change your name on orders")

    name = ObjDictField()

    title = TxtField('Title', 12, cases={}, src='name')
    givenNames = TxtField('Given', 32, cases={}, src='.name')
    familyNames = TxtField('Family', 32, cases={}, src='name')
    extraName = TxtField('xtra', 24,cases={}, src='name')
    nameType   =EnumField("Name Style",src='name',
                    fmt=dict(values=('e','c','s'),names=('European','Chinese','Spanish')
                        )
                    )
    plan   = EnumForeignField('Shaker Type',zeroText='None',session=viewModelDB
                        ,dispFields=('plans.name','plans.descr'),values='plans.idPlan')

    dob    =DateField('Date of Birth',cases={})
    ageGroup   =EnumField('Age Grouping',fmt=dict(vals=('1','2','3','4','5','7')
                    ,values=('1','2','3','4','5','7')
                    ,names=('0-20','21-30','31-40','41-55','55-70','70+')))
    malefem    =EnumField('Gender',cases={}
                ,fmt=dict(names=('Male','Female',"not sure"),values=('m','f','n')))

    autoTopUpLimit = IntField('Auto Shaker Refill Limit',12
            ,hint='(Refills over this value require password)')
    priorRequests  =TxtListField('Prior Requests with orders',128,48,
            name='prior',src='requests')
    priorPickUps   =TxtListField('Prior Pick Up Instructions',128,48,
            name='prior',src='pickUps')
    recommendStore   =TxtField('A store to recommend to everyone I invite is',24)

    sessionKeys   = TxtField(cases={})
    cards = ObjListField(cases={})
    stores = ObjListField(cases={})
    locations = ObjListField(cases={})
    """
    userID     =TxtField('',None,16)

    quickName  =TxtField('',None,8)
    userType   =TxtField('',None,16)
    proCodeID  =TxtField('',None)#TblIdxCol('',None)
    plan   =TblIdxCol('','Shaker Type',zeroText='None',xtable='plans',dispField='name')
    pwdCountDown   =IntCol('',None,3)
    autoTopUpLimit=AmtCol('','Auto Shaker Refill Limit',12
            hint='(Refills over this value require password)')
    access     =TxtField('',None,16)
    activePhone    =TblIdxCol('','Active Phone',xtable='phoneNumbers',dispField='phoneNum')
    activeAddr     =TblIdxCol('','Active Addr',xtable='addresses',dispField='label')
    activeEmail    =TblIdxCol('','Active Email',xtable='emails',dispField='label')
    contactlist    =IntCol('',None)#TblIdxCol('',None)
    title  =TxtField('','Title',12)
    givenNames     =TxtField('','Given',32)
    familyNames    =TxtField('','Family',32)
    extraName  =TxtField('','xtra',24)
    nameType   =ScalarCol('',"Name Style",posn=0
                    fmt={'vals':('e','c','s')
                    'labels':('European','Chinese','spanish')
                    } )
    logonFlag  =BoolFlagCol('',None,)
    dob    =DateCol('','Date of Birth')
    ageGroup   =ScalarCol('','Age Grouping',posn=0,fmt=dict(vals=('1','2','3','4','5','7')
                    labels=('0-20','21-30','31-40','41-55','55-70','70+')))
    malefem    =ScalarCol('','Gender',fmt=dict(vals=('m','f','n'),labels=('Male','Female',"not sure")))
    language   =IntCol('',None)#'Lang',fmt=dict(vals=('e','o'),labels=('eng','other')))
    stdtip     =IntCol('',None)
    securityQuestion =ScalarCol('','q')
    securityAnswer     =TxtField('',None,32)
    courseNames    =TxtField('',None,128)
    onSaltSince    =DateCol('','Joined Date')
    activeSince    =DateCol('','First Order')
    web    =TxtField('',None,32)
    priorRequests  =TxtField('','Prior Requests with orders',128,48)
    requestsChangedFlag    =IntCol('',None,5)
    requestsCounts     =TxtField('',None,36)
    requestsCountsOld  =TxtField('',None,36)
    priorPickUps   =TxtField('','Prior Pick Up Instructions',128,48)
    pickupsChangeFlag  =IntCol('',None,5)
    pickUpsCounts  =TxtField('',None,36)
    pickUpsCountsOld   =TxtField('',None,36)
    """



    def getRows_(self,*args,**kwargs):
        # self.default_dbRowSrc_ = viewModelDB.default(Members)

        if not args:
            return []
        elif isinstance(args[0],int):
            filt=dict(sqlid=args[0])
        else:
            filt=args[0]
        #print('args',args[0])
        self.filter_ = filt
        result = self.default_dbRowSrc_.find(filt)
        #result = [ObjDict(res) for res in result]
        return result #[ObjDict(res) for res in result]

    @staticmethod
    def cmd5(parms,method='md5'):
        digest = hashlib.new(method)
        if not isinstance(parms,(list,tuple)):
            parms=(parms)
        for parm in parms:
            digest.update(parm.encode())
        return digest.hexdigest()

    def checkSessionKey(self,fullkey=False):
        """ sessionKey field is a comma sep list of entries, each entry
        :dateaccessed:datecreated:key.  If fullkey  provided, find key and update
        access. Note, default is not 'None' as a deleted cookie will be None.
        If no key then make new one - and delete
        oldest if already have limit(5)."""
        #import pdb; pdb.set_trace()
        rawblock =self.fields_['sessionKeys'].value
        if isinstance(rawblock,str) and rawblock:
            rawblock= rawblock.split(',')

        keyblock = [] if not rawblock else [
                        SessKey(*x.split(':'))
                            for x in rawblock
                    ]

        #print('rawblock',rawblock,keyblock)
        last=start=time.strftime("%Y/%m/%d")
        if fullkey is False:
            if len(keyblock)>= 5:
                keyblock.sort()
                del keyblock[0]
            random.seed()
            key=self.cmd5(str(random.random())[2:])
        else:
            try:
                cook=SessKey(*fullkey.split(':'))
            except AttributeError:
                cook=SessKey(None,None,None)
            key=cook.key
            for i,block in enumerate(keyblock):
                if key == block.key:
                    if block.last == last:
                        return True
                    last=block.last
                    del keyblock[i]
                    break
            else:
                print('chech rawlock new {} {} {} {}'.format(i,block.key,key,key==block.key))
                return False
        thisblock =SessKey(last,start,key)
        keyblock.append(thisblock)
        #rawblock = ','.join([':'.join(i) for i in keyblock])
        rawblock = [':'.join(i) for i in keyblock]
        self.fields_['sessionKeys'].value = rawblock
        self.update_()
        #print('rawblock',rawblock)
        return ':'.join(thisblock)
    def validatePassword(self,pwd):
        #print("pwd c",self.encPass,pwd,self.cmd5(pwd),self.id,self.quickName)
        return self.encPass == self.cmd5(pwd)




class CardView(BaseView):
    ''' a view of one or more card documents.  Each view can be a join of
    a parent list of cards (from member table) plus the data from card documents
    '''
    viewName_ = "Cards"
    models_ = Cards, DBMongoEmbedSource(viewModelDB, "members.cards")

    #used in mako fmpage for on screen display of viewname

    id          = IdField(cases={})
    #salt        = IntField(cases={}) #no in db for Mongo
    membcard   = ObjDictField(cases={},name='key',src='members.cards')
    membcardk   = TxtField(cases={},name='id',src='members.cards')
    label       = TxtField('Label for Card', 8,src='members.cards',rowLabel=True)
    leadLen     = IntField(cases={})
    sqlid     = TxtField(cases={})
    leadings    = TxtField('',8,cases={})
    trailings   = TxtField('',8,cases={})
    expire      = TxtField('',4,cases={})
    encrypted   = TxtField('',12,cases={})
    owf         = TxtField('',32,cases={})
    cardNumber  = TxtField('',24,cases={})
    nameOnCard  = TxtField('Name On Card',24)
    cardType    = EnumField("Card Type",
                    fmt=dict(values=('E','V','M','A'),names=('EftPOS','Visa','MasterCard','Amex')
                        )
                    )
    accountsOnCard = TxtField('',8,cases={})
    defaultAcc  = TxtField('',1,cases={})
    allowOverride  = TxtField('',1,cases={})
    securecode  = TxtField('',6,cases={})
    encKey  = TxtField('',8,cases={})
    cardOnSaltSince = DateField()
    activeDate  = DateField()
    address     = IntField('enum which addr',cases={})
    defaultExpensexx = TxtField('to move to profile',24,cases={})
    askOverridexx = TxtField('to move to profile',24,hint='ask which expense?',cases={})


    def getRows_(self,*args,**kwargs):
        def cardreader(idx_):
            self.getJoin_('cards',
                        ObjDict(sqlid=self[idx_].membcard['sqlid']),
                            idx_)
            return {}
        def lazy(rows):
            #lazy_ indicates main row not yet loaded
            return [{'members.cards':row} for row in rows]
        def fromMemb(finddict):
            read = viewModelDB.default(Members).find(finddict)
            assert read.count()==1,'Problem finding member for cards'
            member=read[0]
            self.set_source_idx_('members.cards',member)
            return lazy(member['cards'])

        if not args:
            return []
        
        #self.joins_ = ObjDict((('cards',cardreader),('members.cards',None)))
        self._sources['cards'].loader = cardreader

        self._sources.cards.join_links = ['membcardk','membcard.id','membcard.sqlid']
        cardlist=args[0]
        if isinstance(cardlist,dict): #extract list from dict:(cards=[])
            cardlist=cardlist.get('cards', None)
        if isinstance(cardlist,list):
            # instanced from joindata - 'lazy' load of main data
            #extra code would be needed if more joins - not for cards
            return lazy(cardlist)
        elif isinstance(args[0],int): #work with members - get data then do lazy?
            data='members.cards'
            filtfld='members.sqlid'
            return fromMemb(dict(sqlid=args[0]))
        else:
            return fromMemb(args[0])
        #cases below not yet coded for Mongo
        selectFilt=args[0]
        joinfilt=SaltCards.card==Cards.id
        result = saltMongDB.session.query(SaltCards,Cards).filter(
                            joinfilt,
                            selectFilt).all()
        #print('did read cards',type(result[0]),len(result),dir(result[0]))
        crds=result[0].cards
        #print('sub',type(crds),dir(crds))
        return result

    """rowSpec={"table":"cards"
                  ,'min':1
                  ,"filter":{"salt": saltID}
                 }"""
