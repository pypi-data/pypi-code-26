

#from views.auth import ppssauthpolicy,ACLRoot,getPrincipals
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
import transaction
import zope.sqlalchemy

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import SessionAuthenticationPolicy
from constants import Conf
from models import initdb


from pyramid.security import (
    Everyone, Authenticated,
    remember,forget,
    Allow,
    Everyone,ALL_PERMISSIONS
    )


def initAuthDb(settings):
    engine = engine_from_config(settings, "sqlalchemy.")
    factory = sessionmaker()
    factory.configure(bind=engine)
    #dbsession = get_tm_session(session_factory, transaction.manager)
    dbsession = factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction.manager)
    with transaction.manager:
        initdb(dbsession,Conf.initdb)
    

configured = False
def includeme(config):
    global configured
    if configured:
        return
    configured = True
    #ppssauthpolicy = PPSSAuthenticationPolicy(config.get_settings())
    settings = config.get_settings()
    Conf.setup(settings)
    config.include("pyramid_beaker")
    config.add_static_view(  name='ppss_auth_static', path='ppss_auth_static', cache_max_age=3600)
    config.add_route('ppsslogin', '/login')
    config.add_route('ppsslogout', '/logout')

    config.add_route('ppsschangepassword', '/password/change')
    
    config.add_route('ppss:user:list', '/user/list')
    config.add_route('ppss:user:edit', '/user/modify/{elementid}')
    config.add_route('ppss:group:list', '/group/list')
    config.add_route('ppss:group:edit', '/group/modify/{elementid}')
    config.add_route('ppss:perm:list', '/perm/list')
    config.add_route('ppss:perm:edit', '/perm/modify/{elementid}')

    config.add_route('ppss:user:remove', '/user/remove/{userid}/{groupid}')

    initAuthDb(settings)

    from views.auth import AuthController

    config.add_view(AuthController,attr='login',route_name="ppsslogin", renderer=Conf.logintemplate)
    config.add_view(AuthController,attr='logout',route_name="ppsslogout")
    config.add_view(AuthController,attr='ppsschangepassword',route_name="ppsschangepassword", 
        permission="login", renderer=Conf.changepasswordtemplate)

    if Conf.forbiddentologin:
        config.add_forbidden_view(AuthController,attr='login',renderer=Conf.logintemplate)
    
    config.add_view(AuthController,attr='listUser',route_name="ppss:user:list",
        permission="listuser", renderer=Conf.listusertemplate)
    config.add_view(AuthController,attr='editUser',route_name="ppss:user:edit",
        permission="edituser", renderer=Conf.editusertemplate)
    
    config.add_view(AuthController,attr='listGroup',route_name="ppss:group:list",
        permission="listuser", renderer=Conf.listgrouptemplate)
    config.add_view(AuthController,attr='editGroup',route_name="ppss:group:edit",
        permission="edituser", renderer=Conf.editgrouptemplate)

    config.add_view(AuthController,attr='listPerm',route_name="ppss:perm:list",
        permission="sysadmin", renderer=Conf.listpermtemplate)
    config.add_view(AuthController,attr='editPerm',route_name="ppss:perm:edit",
        permission="sysadmin", renderer=Conf.editpermtemplate)


    from views.auth import getPrincipals,ACLRoot
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(SessionAuthenticationPolicy(callback=getPrincipals) )
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_root_factory(ACLRoot)
    pass
