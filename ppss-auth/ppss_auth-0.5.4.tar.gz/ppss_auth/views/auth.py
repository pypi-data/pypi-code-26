from pyramid.response import Response
from pyramid.authentication import AuthTktCookieHelper
from pyramid.settings import asbool

from ..constants import Conf
from ..models import PPSsuser,PPSsgroup

from pyramid.view import view_config,forbidden_view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

import os,datetime,logging
l = logging.getLogger('ppssauth')


from pyramid.security import (
    Everyone, Authenticated,
    remember,forget,
    Allow,Deny,
    Everyone,ALL_PERMISSIONS
    )


def getPrincipals(uid,request):
    groups = request.session.get('principals',[])
    l.info("####  usergroups:{g}".format(g=groups))
    return groups

class ACLRoot(object):
    baseACL=[(Allow, Authenticated, 'view'),
        (Allow, 'g:superadmin', ALL_PERMISSIONS),
        (Deny,  'g:admin', 'deleteadmin'),
        (Allow, 'g:admin', ALL_PERMISSIONS)
        ]

    lastupdateACL = datetime.datetime.now()
    __acl__ = [
        (Allow, 'g:superadmin', ALL_PERMISSIONS),
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]
    def __init__(self, request):
        self.request = request
        #l.info("*************ACLRoot*************")
        groups = self.request.dbsession.query(PPSsgroup).filter(PPSsgroup.enabled==1).all()
        acl = [] 
        for group in groups:
            acl.append( (Allow,
                    str("g:"+group.name),
                    tuple([str(p.name) for p in group.permissions])  
            ) )

        ACLRoot.__acl__ = ACLRoot.baseACL + acl
        l.info("built ACL:{acl}".format(acl=repr(ACLRoot.__acl__)) )



class AuthController():

    def __init__(self,request):
        self.request = request
        self.user = None
        self.retdict = {
            'midtpl':Conf.sectiontemplateinherit,
            'supertpl':Conf.mastertemplateinherit,
        }

    def login(self):
        l.debug("trying login")
        r = self.request
        postloginpage = self.request.referer if self.request.referer!=self.request.route_url("ppsslogin") else Conf.postloginroute
        postloginpage = Conf.postloginroute
        if r.POST:
            username = r.params.get("username",u"")
            password = r.params.get("password",u"")
            #l.info("u={username},p={password} ".format(username=username,password=password))
            if Conf.adminpass and  username == Conf.adminname and password == Conf.adminpass:
                l.info("{username} logged in as superuser".format(username=username) )
                r.session['admin'] = True
                r.session['principals'] = ["g:admin","g:superadmin"]
                r.session['user'] = {'id':'1','name':'admin'}
                headers = remember(r, u"1")
                r.userid=u"1"
                return HTTPFound(r.route_url(postloginpage),headers=headers)
            res = PPSsuser.checkLogin(username,password,r.dbsession)
            if res:
                l.debug("{username} logged in as normal user".format(username=username) )
                r.userid=res.id
                r.session['user'] = {'id':res.id,'name':username}
                headers = remember(r, res.id)
                r.session['principals'] = [str("g:"+group.name ) for group in res.groups  ]  #["g:user"]
                return HTTPFound(r.route_url(postloginpage),headers=headers)
            self.request.dbsession.query(PPSsuser).filter()    
            return {'logintpl': Conf.publictemplateinherit ,'msg':'something went wrong with your login. Please check your informations'}
        #return Response("ok")
        #return{'logintpl': "arvalpromotool:/templates/layout/bolayout.mako" , 'msg':''}
        return{'logintpl': Conf.publictemplateinherit , 'msg':''}

    def logout(self):
        l.info("logout")
        l.info("principals = {pr}".format(pr=self.request.session.get('principals',[])  ))

        headers = forget(self.request)
        self.request.session.pop('admin',None)
        self.request.session.pop('user',None)
        self.request.session.pop('principals',None)
        
        return HTTPFound(self.request.route_url(Conf.logoutroute),headers=headers)

    def ppsschangepassword(self):
        l.info("change password")
        retdict = {'logintpl': Conf.publictemplateinherit,'msg':"",'res':True}
        retdict.update(self.retdict)
        if self.request.POST:
            oldpassword = self.request.params.get("oldpassword")
            newpassword = self.request.params.get("newpassword")
            username = self.request.session.get("user").get("name")
            res = PPSsuser.checkLogin(username,oldpassword,self.request.dbsession)     
            if res:
                res.password = newpassword       
                
            else:
                retdict['res']=False
                retdict['msg']='password is wrong'
        return retdict
        
    def listUser(self):
        elements = self.request.dbsession.query(PPSsuser).all()
        retdict = {'elements':elements}
        retdict.update(self.retdict)
        return retdict
    def editUser(self):
        userid = int(self.request.matchdict.get("elementid","-1"))
        l.info("change password")
        retdict = dict(self.retdict,**{'msg':"",'res':True,'userid':userid} )
        if userid<0:
            user = PPSsuser()
        else:
            user = PPSsuser.byId(userid,self.request.dbsession)
            if not user:
                retdict['res'] = False
                retdict['msg'] = "user not found"
        allgroups = PPSsgroup.all(self.request.dbsession)
        retdict.update({"user" : user, 'allgroups':allgroups })

        if self.request.POST:
            if userid<0:
                
                self.request.dbsession.add(user)
            if not user:
                return retdict
            newpassword = self.request.params.get("password","")
            if newpassword:
                user.setPassword(newpassword)
            user.username = self.request.params.get("username",user.username)
            user.enabled = 1 if self.request.params.get("enabled")=="1" else 0
            
            groups=map(int,self.request.params.getall("groups"))
            usergroups = [PPSsgroup.byId(groupid,self.request.dbsession) for groupid in groups]
            user.groups = usergroups
            self.request.dbsession.flush()
            return HTTPFound(self.request.route_url('ppss:user:edit',userid = user.id))
            #return retdict

        return retdict



    def listGroup(self):
        elements = self.request.dbsession.query(PPSsgroup).all()
        return dict(self.retdict,**{'elements':elements}) 
    def editGroup(self):
        groupid = int(self.request.matchdict.get("elementid","-1"))
        retdict = dict(self.retdict,**{'msg':"",'res':True,'groupid':groupid} )
        if groupid<0:

            group = PPSsgroup()
        else:
            group = PPSsgroup.byId(groupid,self.request.dbsession)
            if not group:
                return HTTPFound(self.request.route_url('ppss:group:list'))
        retdict.update({'group':group})


        if self.request.POST:
            if groupid<0:
                self.request.dbsession.add(group)
            group.name = self.request.params.get("name")
            group.enabled = 1 if self.request.params.get("enabled")=="1" else 0
            #self.request.dbsession.flush()
        return retdict

    def listPerm(self):
        elements = self.request.dbsession.query(PPSspermission).all()
        return dict(self.retdict,**{'elements':elements})
    def editPerm(self):
        return {}




