from setuptools import setup,find_packages

longdescription = """
::
  this package aims to give and easy pluggable module to provide authentication.

  To activate the package, in your main __init__.py file, inside the main function, add this line:

:: 
  config.include('ppss_auth')

::

  It's based upon sqlalchemy backend for the creation and usage of 3 main tables:
  ppss_user - containing basic information about the users (username, hashed password and related data )
  ppss_group - user groups to allow for easier handling of user groups and permissions
  ppss_permission - a list of permissions (just an id and a name)

  When a user login, sessionauthpolicy is used to store her informations (userid and user groups)

  ppss_auth use these info from the ini file:

-ppss_auth.adminname - the name of a sueruser. Deafult to "admin"
-ppss_auth.adminpass - the corresponding password. If not provided the admin is not allowed to log in (with the ini credentials. It may exist in database)
-ppss_auth.post_login_follow - try to redirect the browser back to where it came from after successful login (use true case insensitive to activate it). It's useful if combined with the forbidden pattern
-ppss_auth.post_login_route - name of the route where to send the browser after user logged in. Default to Home. Ignored if ppss_auth.post_login_follow is set to true AND there is a referer to go to.
-ppss_auth.post_logout_route - name of the route where to send the browser after log out. Defaults to home
-ppss_auth.logintemplate - name of the login template. It defaults to the internal template: "ppss_auth:/templates/login.mako"
-ppss_auth.changepasswordtemplate - name of the change password template. Defaults to: ppss_auth:/templates/change.mako
-ppss_auth.modifyusertemplate - Defaults to: ppss_auth:/templates/modifyuser.mako
-ppss_auth.listusertemplate - Defaults to: ppss_auth:/templates/listuser.mako
-ppss_auth.logintemplateinherit - Defaults to: ppss_auth:/templates/layout.mako

::
  to init the Tables, in the initialization script, add this row:
  from ppss_auth import (models as ppssmodels)

  while creating the default data you use something like:
  ppssmodels.initdb(dbsession,createdefault=False)
  This creates the tables and, if createdefault evaulates to True, it create a default admin/admin user with the admin permission. Please change the password to avoid secuirity issues
  the method retunrs (adminuser,adminpassword)
  On users use the setPassword method to change the password, providing the new password

"""

setup(name='ppss_auth',
  version='0.5.4',
  description='simple auth scheme for pyramid, based on Mako template and sqlalchemy backend',
  long_description=longdescription,
  author='pdepmcp',
  author_email='d.cariboni@pingpongstars.it',
  license='MIT',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
  ],
  keywords="pyramid module authentication accelerator",
  python_requires='>=2.7, <3',
  url='http://www.pingpongstars.it',

  #packages=['src/test1'],
  packages=find_packages(),
  include_package_data=True,

)


