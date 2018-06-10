"""
Brython MDCComponent: MDCMenu
=============================


"""


from browser import window
from .core import MDCTemplate
#from .MDCButton import MDCButton,  MDCIconToggle



########################################################################
class __menuItem__(MDCTemplate):
    """"""

    #MDC_optionals = {


        #'disable': 'tabindex="-1" aria-disabled="true"',


    #}



    #----------------------------------------------------------------------
    def __new__(self, text, disable=False, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element


    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""

        if not context['disable']:
            cls.MDC_optionals['disable'] = 'tabindex="0"'
        else:
            cls.MDC_optionals['disable'] = 'tabindex="-1" aria-disabled="true"',


        code = """
            <li class="mdc-list-item" role="menuitem" {disable}>
              {text}
            </li>
        """
        return cls.render_html(code, context)






########################################################################
class MDCMenu(MDCTemplate):
    """"""

    NAME = 'menu', 'MDCMenu'

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
    def __new__(self, corner='BOTTOM_END', **kwargs):
        """"""

        self.element = self.render(locals(), kwargs)

        #if corner in ['BOTTOM_START', 'BOTTOM_LEFT', 'BOTTOM_RIGHT', 'BOTTOM_END', 'TOP_START', 'TOP_LEFT', 'TOP_RIGHT', 'TOP_END']:
            #c = getattr(window.mdc.menu.MDCMenuFoundation.Corner, corner)
            #print(c, self.mdc.setAnchorCorner)
        #self.mdc.setAnchorCorner(window.mdc.menu.MDCMenuFoundation.Corner.BOTTOM_END)

        return self.element


#menu.setAnchorCorner(mdc.menu.MDCMenuFoundation.Corner.TOP_START)


    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""

        code = """
            <div class="mdc-menu" tabindex="-1">
              <ul class="mdc-menu__items mdc-list" role="menu" aria-hidden="true">
              </ul>
            </div>

        """
        return cls.render_html(code, context)




    #----------------------------------------------------------------------
    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'content':
            return self.element.select('.mdc-menu__items')[0]

        #elif name is 'action_buttons':
            #return self.element.select('.mdc-card__action-buttons')[0]

        #elif name is 'action_icons':
            #return self.element.select('.mdc-card__action-icons')[0]



    #----------------------------------------------------------------------
    @classmethod
    def add_item(cls, element, *args, **kwargs):
        """"""
        item = __menuItem__(*args, **kwargs)
        cls['content'] <= item
        return item


    #----------------------------------------------------------------------
    @classmethod
    def add_divider(cls, element):
        """"""
        divider = '<li class="mdc-list-divider" role="separator"></li>'
        divider = cls.render_str(divider)
        cls['content'] <= divider



    #----------------------------------------------------------------------
    @classmethod
    def toggle(cls, element, corner='TOP_START', *args, **kwargs):
        """"""
        if corner in ['BOTTOM_START', 'BOTTOM_LEFT', 'BOTTOM_RIGHT', 'BOTTOM_END', 'TOP_START', 'TOP_LEFT', 'TOP_RIGHT', 'TOP_END']:
            c = getattr(window.mdc.menu.MDCMenuFoundation.Corner, corner)
            cls.mdc.setAnchorCorner(c)


        cls.mdc.open = not cls.mdc.open
        #self['title'].text = text


