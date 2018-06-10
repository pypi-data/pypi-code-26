"""
Brython MDCComponent: MDCDrawer
===============================


"""


from .core import MDCTemplate



########################################################################
class __drawerItem__(MDCTemplate):
    """"""
    NAME = 'draweritem', 'Drawer Item'

    MDC_optionals = {

        'ignore_link': 'RDNT-ignore_link',

        }


    #----------------------------------------------------------------------
    def __new__(self, name, icon, link='#', ignore_link=False, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        #self.mdc.id = name
        #self.element.bind('click', self.activate)
        return self.element


    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
        <a class="mdc-list-item {ignore_link}" href="{link}">
          <i class="material-icons mdc-list-item__graphic" aria-hidden="true">{icon}</i>{name}
        </a>
        """
        return cls.render_html(code, context)


    #----------------------------------------------------------------------
    #@classmethod
    #def activate(cls, *args, **kwargs):
        #""""""

        #print('EWE')

        #for item in document.select('.mdc-drawer .mdc-list-item'):
            #item.class_name = item.class_name.replace('mdc-list-item--activated', '')

        ##print(cls.mdc.id)
        #cls.mdc.add_class(['mdc-list-item--activated'])






########################################################################
class MDCDrawer(MDCTemplate):
    """"""

    CSS_classes = {
        #'permanent': 'mdc-drawer--permanent',
        #'fixed':  'mdc-toolbar--fixed',
        #'waterfall': 'mdc-toolbar--waterfall',
        #'flexible': 'mdc-toolbar--flexible',
        #'fixed_lastrow_only': 'mdc-toolbar--fixed-lastrow-only',
    }

    #----------------------------------------------------------------------
    def __new__(self, header='', temporary=True, persistent=False, permanent=False, **kwargs):
        """"""

        #print(locals(), kwargs)

        #return super(MDCDrawer, self).__new__(locals())

        self.element = self.render(locals(), kwargs)
        ##self.element.mdc = mdcDrawer.new(self.element)


        # if self['drawer_drawer']:
            # self['drawer_drawer'].style = {'overflow': 'scroll'}

        self.element.style = {'min-height': '100%'}

        return self.element

        #return self.render(locals(), kwargs)


    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        if context.get('permanent'):

            cls.NAME = 'drawer', 'MDCPermanentDrawer'
            # <div class="mdc-drawer__toolbar-spacer"></div>
            code = """
                <nav class="mdc-drawer mdc-drawer--permanent mdc-typography">
                  <div class="mdc-drawer__content">

                    <header class="mdc-drawer__header mdc-theme--primary-bg mdc-theme--on-primary">
                      <div class="mdc-drawer__header-content">
                        {header}
                      </div>
                    </header>

                    <nav class="mdc-list">

                    </nav>
                  </div>
                </nav>
            """
        elif context.get('persistent'):
            cls.NAME = 'drawer', 'MDCPersistentDrawer'
            code = """
                <aside class="mdc-drawer mdc-drawer--persistent mdc-typography">
                  <nav class="mdc-drawer__drawer">
                    <header class="mdc-drawer__header mdc-theme--primary-bg mdc-theme--on-primary">
                      <div class="mdc-drawer__header-content">
                        {header}
                      </div>
                    </header>
                    <nav  class="mdc-drawer__content mdc-list">

                    </nav>
                  </nav>
                </aside>
            """

        elif context.get('temporary'):
            cls.NAME = 'drawer', 'MDCTemporaryDrawer'
            code = """
            <aside class="mdc-drawer mdc-drawer--temporary mdc-typography">
              <nav class="mdc-drawer__drawer">
                <header class="mdc-drawer__header mdc-theme--primary-bg mdc-theme--on-primary">
                  <div class="mdc-drawer__header-content">
                    {header}
                  </div>
                </header>
                <nav class="mdc-drawer__content mdc-list">

                </nav>
              </nav>
            </aside>
            """


        return cls.render_html(code, context)



    #----------------------------------------------------------------------
    @classmethod
    def __getitem__(self, name):
        """"""
        try:

            if name is 'content':
                return self.element.select('.mdc-list')[0]
            elif name is 'items':
                return self.element.select('.mdc-list .mdc-list-item')
            elif name is 'header':
                return self.element.select('.mdc-drawer__header')[0]
            elif name is 'drawer_drawer':
                return self.element.select('.mdc-drawer__drawer')[0]

            #elif name is 'title':
                #return self.element.select('.mdc-toolbar__title')[0]

        except IndexError:
            return None



    #----------------------------------------------------------------------
    @classmethod
    def add_item(cls, element, name, icon, link='#', **kwargs):
        """"""
        item = __drawerItem__(name, icon, link, **kwargs)
        #item.bind('click', cls.__activate__(item))
        #item.bind('click', item.mdc.activate)

        cls['content'] <= item
        return item



    ##----------------------------------------------------------------------
    #@classmethod
    #def __activate__(self, item):
        #""""""
        #inset = lambda evt:item.mdc.activate()
        #return inset


    ##----------------------------------------------------------------------
    #@classmethod
    #def activate(cls, item, *args, **kwargs):
        #""""""
        #print('EWE')

        #for it in document.select('.mdc-drawer .mdc-list-item'):
            #it.class_name = it.class_name.replace('mdc-list-item--activated', '')

        #item.mdc.add_class(['mdc-list-item--activated'])





    #----------------------------------------------------------------------
    @classmethod
    def open(cls, element):
        """"""
        cls.mdc.open = True


    #----------------------------------------------------------------------
    @classmethod
    def close(cls, element):
        """"""
        cls.mdc.open = False

