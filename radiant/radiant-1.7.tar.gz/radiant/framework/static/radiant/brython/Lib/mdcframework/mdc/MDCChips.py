"""
Brython MDCComponent: MDCChips
==============================


"""


from .core import MDCTemplate


########################################################################
class MDCChipSet(MDCTemplate):
    """"""

    NAME = 'chips', 'MDCChipSet'

    CSS_classes = {
        #'fixed':  'mdc-toolbar--fixed',
        #'waterfall': 'mdc-toolbar--waterfall',
        #'flexible': 'mdc-toolbar--flexible',
        #'fixed_lastrow_only': 'mdc-toolbar--fixed-lastrow-only',
    }

    #----------------------------------------------------------------------
    def __new__(self, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element



    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
            <div class="mdc-chip-set">
            </div>
        """

        return cls.render_html(code, context)


    #----------------------------------------------------------------------
    @classmethod
    def add_chip(cls, element, text, leading=None, trailing=None, selected=False):
        """"""

        if selected:
            selected = 'mdc-chip--selected'
        else:
            selected = ''

        if leading:
            code = '''
                <div class="mdc-chip {selected}">
                  <i class="material-icons mdc-chip__icon mdc-chip__icon--leading">{leading}</i>
                  <div class="mdc-chip__text">{text}</div>
                </div>
            '''.format(text=text, leading=leading, selected=selected)
        elif trailing:
            code = '''
                <div class="mdc-chip {selected}">
                  <div class="mdc-chip__text">{text}</div>
                  <i class="material-icons mdc-chip__icon mdc-chip__icon--trailing">{trailing}</i>
                </div>
            '''.format(text=text, trailing=trailing, selected=selected)

        else:
            code =  '''
                <div class="mdc-chip {selected}" tabindex="0">
                  <div class="mdc-chip__text">{text}</div>
                </div>
                  '''.format(text=text, selected=selected)

        chip = cls.render_str(code)
        cls.element <= chip
        return chip


    #----------------------------------------------------------------------
    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'selected':
            chips = self.element.select('.mdc-chip--selected')
            return [c.id for c in chips]
        #elif name is 'items':
            #return self.element.select('.mdc-list .mdc-list-item')

        #elif name is 'title':
            #return self.element.select('.mdc-toolbar__title')[0]


