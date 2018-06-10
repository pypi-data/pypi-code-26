from browser import document
from mdcframework.base import MDCBase
from mdcframework.mdc import *

from browser import html




########################################################################
class Base(MDCBase):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""

        self.load_styles([
            "styles.css",
            "themes.css",
            ])

        #self.load_scripts([

           #])

        super().__init__(*args, **kwargs)


    #----------------------------------------------------------------------
    def brython_code_sample(self, title, code, container, render=True):
        """"""

        title = html.H3(title)
        title.style = {
                'font-weight': 'normal',
        }
        container <= title

        # MDCCards()



        display_code = html.PRE(code)
        display_code.style = {
            # 'border': '1px solid lightgray',
            # 'padding': '0 15px',
            'overflow-x': 'scroll',
            'font-size': '13px',
            'margin': '0',
        }

        card = html.DIV(display_code, Class="mdc-card", style={'padding': '1em',
                                                               'margin': '1em 0px',
                                                               'background-color': 'rgba(77, 182, 172, 0.13)',
                                                               'color': '#3a3a3a',
                                                               })
        # callable <= card

        container <= card

        # container <= display_code
        if render:
            eval(code)

            divisor = html.DIV()
            divisor.style = {
                'height': '34px',
            }

            container <= divisor


main = Base(**{'home': ['home.Home', 'Home', 'home'],
               'python': ['connectpython.Python', 'Python', 'code'],
               'buttons': ['buttons.Buttons', 'Buttons', 'add_circle_outline'],
               'cards': ['cards.Cards', 'Cards', 'picture_in_picture'],
               'chips': ['chips.Chips', 'ChipSet', 'label_outline'],
               'dialog': ['dialogs.Dialogs', 'Dialogs', 'announcement'],
               'elevations': ['elevations.Elevations', 'Elevations', 'filter_none'],
               'formfields': ['formfields.FormField', 'FormFields', 'text_fields'],
               'forms': ['forms.Forms', 'Forms', 'text_fields'],
               'gridlist': ['gridlist.GridLists', 'GridLists', 'view_week'],
               #'imagelist': [ImageList, ['ImageList', 'view_quilt']],
               'layoutgrid': ['layoutgrid.LayoutGrid', 'LayoutGrid', 'view_quilt'],
               'linearprogress': ['linearprogress.LinearProgress', 'LinearProgress', 'more_horiz'],
               'lists': ['lists.Lists', 'Lists', 'list'],
               'menus': ['menus.Menus', 'Menus', 'more_vert'],
               'ripples': ['ripples.Ripples', 'Ripples', 'toll'],
               'shapes': ['shapes.Shapes', 'Shapes', 'format_shapes'],
               'snackbars': ['snackbars.Snackbars', 'Snackbars', 'call_to_action'],
               'tabs': ['tabs.Tabs', 'Tabs', 'tab'],
               'themes': ['themes.Themes', 'Themes', 'color_lens'],
               'topappbar': ['topappbar.TopAppBar', 'TopAppBar', 'featured_play_list'],
               'typography': ['typography.Typography', 'Typography', 'font_download'],
               })

main.generate_drawer()
main.view('home')

try:
    document.select('.splash_loading')[0].remove()
except:
    pass

