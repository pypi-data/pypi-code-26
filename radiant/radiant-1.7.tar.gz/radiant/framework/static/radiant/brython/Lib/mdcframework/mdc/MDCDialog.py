"""
Brython MDCComponent: MDCDialog
===============================


"""

from .core import MDCTemplate
from .MDCButton import MDCButton

########################################################################
class MDCDialog(MDCTemplate):
    """"""

    NAME = 'dialog', 'MDCDialog'

    CSS_classes = {

        #'_16_9': 'mdc-card__media--16-9',
        #'square': 'mdc-card__media--square',
    }

    MDC_optionals = {

        'scrollable': 'mdc-dialog__body--scrollable',
        #'full_bleed': 'mdc-card__actions--full-bleed',
        #'icon': '<i class="material-icons mdc-button__icon" aria-hidden="true">{icon}</i>',
        #'disabled': 'disabled',

    }

    #----------------------------------------------------------------------
    def __new__(self, title='', content='', scrollable=False, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element



    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""

        cls.ID = cls.new_id()
        context['id'] = cls.ID

        code = """
            <aside id="{id}"
              class="mdc-dialog"
              role="alertdialog"
              aria-labelledby="{id}-label"
              aria-describedby="{id}-description">
              <div class="mdc-dialog__surface">
                <header class="mdc-dialog__header">
                  <h2 id="{id}-label" class="mdc-dialog__header__title">
                    {title}
                  </h2>
                </header>
                <section id="{id}-description" class="mdc-dialog__body {scrollable}">
                  {content}
                </section>
                <footer class="mdc-dialog__footer">
                </footer>
              </div>
              <div class="mdc-dialog__backdrop"></div>
            </aside>
        """

        return cls.render_html(code, context)

     #<button type="button" class="mdc-button mdc-dialog__footer__button mdc-dialog__footer__button--accept">Accept</button>




    #----------------------------------------------------------------------
    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'footer':
            return self.element.select('.mdc-dialog__footer')[0]

        elif name is 'header':
            return self.element.select('.mdc-dialog__header')[0]

        elif name is 'body':
            return self.element.select('.mdc-dialog__body')[0]

        elif name is 'title':
            return self.element.select('.mdc-dialog__header__title')[0]

        #elif name is 'action_icons':
            #return self.element.select('.mdc-card__action-icons')[0]


    #----------------------------------------------------------------------
    @classmethod
    def add_footer_button(cls, element, *args, **kwargs):
        """"""

        button = MDCButton(*args, **kwargs)
        button.class_name += ' mdc-dialog__footer__button'

        if kwargs.get('cancel', False):
            button.class_name += ' mdc-dialog__footer__button--cancel'
        elif kwargs.get('accept', False):
            button.class_name += ' mdc-dialog__footer__button--accept'

        if kwargs.get('action', False):
            button.class_name += ' mdc-dialog__action'

        cls['footer'] <= button
        return button


    ##----------------------------------------------------------------------
    #@classmethod
    #def show(cls, *args, **kwargs):
        #""""""
        ##dialog = window.mdc.dialog.MDCDialog.new(document.querySelector('#{}'.format(cls.ID)))
        #dialog.show()


    #----------------------------------------------------------------------
    #@classmethod
    #def close(cls, *args, **kwargs):
        #""""""
        #dialog = window.mdc.dialog.MDCDialog.new(document.querySelector('#{}'.format(cls.ID)))
        #dialog.close()


    ##----------------------------------------------------------------------
    #@classmethod
    #def open(cls, *args, **kwargs):
        #""""""
        #dialog = window.mdc.dialog.MDCDialog.new(document.querySelector('#{}'.format(cls.ID)))
        #return dialog.open
