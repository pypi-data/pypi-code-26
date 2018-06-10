"""
Brython MDCComponent: MDCTab
============================


"""


from .core import MDCTemplate

from browser import html
#from .MDCButton import MDCButton,  MDCIconToggle



########################################################################
class __tabItem__(MDCTemplate):
    """"""

    #NAME = 'tabs', 'MDCTabBar'

    MDC_optionals = {

        #'outlined': 'mdc-card--outlined',
        #'full_bleed': 'mdc-card__actions--full-bleed',
        #'icon': '<i class="material-icons mdc-button__icon" aria-hidden="true">{icon}</i>',
        'active': 'mdc-tab--active',

    }


    #----------------------------------------------------------------------
    def __new__(self, text=None, icon=None, id='#', active=False, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element


    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        if context['text'] and not context['icon']:
            code = """
                <a class="mdc-tab {active}" href="#{id}">{text}</a>
            """


        elif not context['text'] and context['icon']:
            code = """
                <a class="mdc-tab {active}" href="#{id}">
                  <i class="material-icons mdc-tab__icon" aria-label="Recents">{icon}</i>
                </a>
            """


        elif context['text'] and context['icon']:
            code = """
                <a class="mdc-tab mdc-tab--with-icon-and-text {active}" href="#{id}">
                  <i class="material-icons mdc-tab__icon" aria-hidden="true">{icon}</i>
                  <span class="mdc-tab__icon-text">{text}</span>
                </a>
            """


        return cls.render_html(code, context)





########################################################################
class MDCTabBar(MDCTemplate):
    """"""

    NAME = 'tabs', 'MDCTabBar'

    CSS_classes = {

        #'_16_9': 'mdc-card__media--16-9',
        #'square': 'mdc-card__media--square',
    }

    MDC_optionals = {

        #'outlined': 'mdc-card--outlined',
        #'full_bleed': 'mdc-card__actions--full-bleed',
        #'icon': '<i class="material-icons mdc-button__icon" aria-hidden="true">{icon}</i>',
        #'disabled': 'disabled',

    }


    #----------------------------------------------------------------------
    def __new__(self, *items, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs, attach_now=False)
        self.element.panels = html.DIV(Class='panels')
        self.element.bind('MDCTabBar:change', self.__tabchanged__(self.element))

        self.element.panel = {}

        for item in items:
            _, panel = self.add_item(**item)
            self.element.panel[item['id']] = panel

        self.attach()

        return self.element



    #----------------------------------------------------------------------
    #@classmethod
    def __tabchanged__(element, *args, **kwargs):
        """"""
        def inset(evt):
            index =  element.mdc.activeTabIndex

            for panel in element.panels.select('.panel'):
                panel.style = {'display': None,}

            panel = element.panels.select('.panel')[index]
            panel.style = {'display': 'block',}

        return inset



    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
            <nav class="mdc-tab-bar">
              <span class="mdc-tab-bar__indicator"></span>
            </nav>
        """

        return cls.render_html(code, context)




    #----------------------------------------------------------------------
    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'items':
            return self.element.select('.mdc-tab')

        elif name is 'items_location':
            try:
                return self.element.select('.mdc-tab-bar')[0]
            except:
                return self.element

        #elif name is 'action_icons':
            #return self.element.select('.mdc-card__action-icons')[0]


    #----------------------------------------------------------------------
    @classmethod
    def add_item(cls, element, text=None, icon=None, id='#', active=False):
        """"""
        item = __tabItem__(text=text, icon=icon, id=id, active=active)
        cls['items_location'] <= item

        if active:
            active = 'active'
            display = 'block'
        else:
            active = ''
            display = None

        panel = html.DIV(Class='panel {}'.format(active), id=id, role='tabpanel', aria_hidden=True)
        panel.style = {'display': display,}
        cls.element.panels <= panel




        return item, panel






    ##----------------------------------------------------------------------
    #@classmethod
    #def title(self, mdc, text):
        #""""""
        #self['title'].text = text




########################################################################
class MDCTabScroller(MDCTabBar):
    """"""

    NAME = 'tabs', 'MDCTabBarScroller'



    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
            <div id="my-mdc-tab-bar-scroller" class="mdc-tab-bar-scroller">
              <div class="mdc-tab-bar-scroller__indicator mdc-tab-bar-scroller__indicator--back">
                <a class="mdc-tab-bar-scroller__indicator__inner material-icons" href="#" aria-label="scroll back button">
                  navigate_before
                </a>
              </div>
              <div class="mdc-tab-bar-scroller__scroll-frame">
                <nav id="my-scrollable-tab-bar" class="mdc-tab-bar mdc-tab-bar-scroller__scroll-frame__tabs">
                  <span class="mdc-tab-bar__indicator"></span>
                </nav>
              </div>
              <div class="mdc-tab-bar-scroller__indicator mdc-tab-bar-scroller__indicator--forward">
                <a class="mdc-tab-bar-scroller__indicator__inner material-icons" href="#" aria-label="scroll forward button">
                  navigate_next
                </a>
              </div>
            </div>
        """

        return cls.render_html(code, context)


