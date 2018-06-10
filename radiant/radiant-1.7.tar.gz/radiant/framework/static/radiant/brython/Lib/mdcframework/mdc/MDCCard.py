"""
Brython MDCComponent: MDCCard
=============================


"""

from .core import MDCTemplate
from .MDCButton import MDCButton,  MDCIconToggle

########################################################################
class MDCCard(MDCTemplate):
    """"""

    NAME = 'card', 'MDCCcard'

    CSS_classes = {

        '_16_9': 'mdc-card__media--16-9',
        'square': 'mdc-card__media--square',
    }

    MDC_optionals = {

        'outlined': 'mdc-card--outlined',
        'full_bleed': 'mdc-card__actions--full-bleed',
        #'icon': '<i class="material-icons mdc-button__icon" aria-hidden="true">{icon}</i>',
        #'disabled': 'disabled',

    }

    #----------------------------------------------------------------------
    def __new__(self, title, subtitle='', content='', media='', _16_9=True, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element



    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""

        if not context.get('full_bleed', ''):
            code = """
                <div class="mdc-card {outlined}">
                  <div class="mdc-card__media {CSS_classes}" style='background-image: url("{media}"); background-color: #00ff00'>
                    <div class="mdc-card__media-content"></div>
                  </div>

                    <div class="demo-card__primary" style='padding: 1em;'>
                      <h2 class="demo-card__title mdc-typography--headline6" style='margin: 0;'>{title}</h2>
                      <h3 class="demo-card__subtitle mdc-typography--subtitle2" style='margin: 0;'>{subtitle}</h3>
                    </div>

                    <div class="demo-card__secondary mdc-typography--body2" style='padding: 0 1rem 8px 1rem;'>
                      {content}
                    </div>

                  <div class="mdc-card__actions">
                    <div class="mdc-card__action-buttons">
                    </div>
                    <div class="mdc-card__action-icons">
                    </div>
                  </div>
                </div>
            """

        else:
            code = """
                <div class="mdc-card {outlined}">
                  <div class="mdc-card__media {CSS_classes}" style='background-image: url("{media}"); background-color: #00ff00'>
                    <div class="mdc-card__media-content"></div>
                  </div>

                    <div class="demo-card__primary" style='padding: 1em;'>
                      <h2 class="demo-card__title mdc-typography--headline6" style='margin: 0;'>{title}</h2>
                      <h3 class="demo-card__subtitle mdc-typography--subtitle2" style='margin: 0;'>{subtitle}</h3>
                    </div>

                    <div class="demo-card__secondary mdc-typography--body2" style='padding: 0 1rem 8px 1rem;'>
                      {content}
                    </div>

                  <div class="mdc-card__actions {full_bleed}">

                  </div>
                </div>
            """

        return cls.render_html(code, context)




    #----------------------------------------------------------------------
    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'actions':
            return self.element.select('.mdc-card__actions')[0]

        elif name is 'action_buttons':
            return self.element.select('.mdc-card__action-buttons')[0]

        elif name is 'action_icons':
            return self.element.select('.mdc-card__action-icons')[0]


    #----------------------------------------------------------------------
    @classmethod
    def add_action_button(cls, element, *args, **kwargs):
        """"""

        button = MDCButton(*args, **kwargs)
        button.class_name += ' mdc-card__action mdc-card__action--button'
        try:
            cls['action_buttons'] <= button
        except:
            cls['actions'] <= button
        #else:
            #button = MDCIconToggle()
            #button.class_name += ' mdc-card__action mdc-card__action--icon'
            #cls['action_icons'] <= button

        return button

    #----------------------------------------------------------------------
    @classmethod
    def add_action_icontoggle(cls, element, *args, **kwargs):
        """"""
        button = MDCIconToggle(*args, **kwargs)
        button.class_name += ' mdc-card__action mdc-card__action--icon'
        cls['action_icons'] <= button

        return button

    #----------------------------------------------------------------------
    @classmethod
    def add_action_icon(cls, element, icon, *args, **kwargs):
        """"""
        button = MDCButton(icon=icon, *args, **kwargs)
        button.class_name += ' mdc-card__action mdc-card__action--icon'
        cls['action_icons'] <= button
        return button




    ##----------------------------------------------------------------------
    #@classmethod
    #def title(self, mdc, text):
        #""""""
        #self['title'].text = text


