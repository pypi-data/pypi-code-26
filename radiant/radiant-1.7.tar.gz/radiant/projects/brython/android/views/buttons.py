from mdcframework.mdc import MDCButton, MDCFab, MDCIconToggle, MDCTopAppBar, MDCDrawer

from mdcframework.base import MDCView
from browser import html

########################################################################
class Buttons(MDCView):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        super().__init__(parent)

        #self.toolbar.mdc['icon'].bind('click', lambda ev:self.main.drawer.mdc.open())


    #----------------------------------------------------------------------
    def build(self):
        """"""
        parent = html.DIV()
        self.topappbar = MDCTopAppBar('Buttons')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container


        code =  '''
button = MDCButton('Button', raised=False, ripple=True)
container <= button

button2 = MDCButton('Button no ripple', raised=False, ripple=False)
container <= button2
        '''
        self.main.brython_code_sample('Button', code, container)


        code =  '''
button = MDCButton('Button raised', raised=True, ripple=True)
container <= button
        '''
        self.main.brython_code_sample('Button raised', code, container)


        code =  '''
button = MDCButton('Button disabled', raised=True, ripple=True, disabled=True)
container <= button
        '''
        self.main.brython_code_sample('Button disabled', code, container)


        code =  '''
button = MDCButton('Button', icon='favorite', raised=True, ripple=True)
container <= button
        '''
        self.main.brython_code_sample('Icon Button', code, container)


        code =  '''
button = MDCButton('Button', icon='favorite', raised=True, ripple=True, reversed=True)
container <= button
        '''
        self.main.brython_code_sample('Icon Button Reversed', code, container)


        code =  '''
button = MDCButton('Button Outlined', raised=False, ripple=True, outlined=True)
container <= button
        '''
        self.main.brython_code_sample('Outlined Button', code, container)


        code =  '''
button = MDCButton('Button Unelevated', raised=False, ripple=True, unelevated=True)
container <= button
        '''
        self.main.brython_code_sample('Unelevated Button', code, container)


        code =  '''
button = MDCFab('favorite')
container <= button
        '''
        self.main.brython_code_sample('Floating Action Button', code, container)


        code =  '''
button = MDCFab('favorite', mini=True)
container <= button
        '''
        self.main.brython_code_sample('Floating Action Button Mini', code, container)


        code =  '''
button = MDCIconToggle('favorite', 'favorite_border')
container <= button
        '''
        self.main.brython_code_sample('Icon Toggle Buttons ', code, container)


        code =  '''
button = MDCButton(icon='favorite', raised=False)
container <= button
        '''
        self.main.brython_code_sample('Icon Buttons ', code, container)


        return parent


