"""
Brython MDCComponent: MDCButton
===============================


Brython MDCComponent: MDCFab
===============================



"""
from .core import MDCTemplate



########################################################################
class MDCButton(MDCTemplate):
    """This is my doctring fro Button Class.

    This is the second lline!!!
    """

    NAME = 'button', 'MDCButton'

    CSS_classes = {
        'raised': 'mdc-button--raised',
        'unelevated': 'mdc-button--unelevated',
        'outlined': 'mdc-button--outlined',
        'dense': 'mdc-button--dense',
        #'icon': 'mdc-button__icon',
    }


    MDC_optionals = {

        'reversed': 'style = "margin-left: 8px; margin-right: -4px;"',
        'ripple': 'data-mdc-auto-init="MDCRipple"',
        'icon': '<i class="material-icons mdc-button__icon" {reversed} aria-hidden="true">{icon}</i>',
        'icon_': '<i class="material-icons" {ripple} tabindex="0" role="button" title="">{icon_}</i>',
        'disabled': 'disabled',



    }


    #----------------------------------------------------------------------
    def __new__(self, text=None, href=None, icon=False, **kwargs):
        """"""
        icon_ = icon
        self.element = self.render(locals(), kwargs)
        return self.element



    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""

        if context.get('href'):
            if context.get('text'):
                if not context.get('reversed'):
                    code = """
                        <a href="{href}" class="mdc-button {CSS_classes}" {ripple} {disabled}>
                        {icon}
                        {text}
                        </a>
                    """
                else:
                    code = """
                        <a href="{href}" class="mdc-button {CSS_classes}" {ripple} {disabled}>
                        {text}
                        {icon}
                        </a>
                    """
            else:
                code = """
                {icon}
                """


        else:
            if context.get('text'):
                if not context.get('reversed'):
                    code = """
                        <button class="mdc-button {CSS_classes}" {ripple} {disabled}>
                        {icon}
                        {text}
                        </button>
                    """
                else:
                    code = """
                        <button class="mdc-button {CSS_classes}" {ripple} {disabled}>
                        {text}
                        {icon}
                        </button>
                    """
            else:
                code = """
                    {icon_}
                    """


        return cls.render_html(code, context)




########################################################################
class MDCFab(MDCButton):
    """"""

    CSS_classes = {
        'mini': 'mdc-fab--mini',
        'exited': 'mdc-fab--exited',
    }


    #----------------------------------------------------------------------
    def __new__(self, icon, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element


    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
            <button class="mdc-fab material-icons {CSS_classes}" {ripple} {disabled}>
              <span class="mdc-fab__icon">
                {icon}
              </span>
            </button>
        """

        return cls.render_html(code, context)



########################################################################
class MDCIconToggle(MDCButton):
    """"""

    NAME = 'iconToggle', 'MDCIconToggle'

    #----------------------------------------------------------------------
    def __new__(self, icon_on, icon_off, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element


    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
            <i class="mdc-icon-toggle material-icons" role="button" aria-pressed="false" {ripple} {disabled}
               aria-label=""
               data-toggle-on='{{"label": "", "content": "{icon_on}"}}'
               data-toggle-off='{{"label": "", "content": "{icon_off}"}}'>
              {icon_off}
            </i>
        """

        return cls.render_html(code, context)