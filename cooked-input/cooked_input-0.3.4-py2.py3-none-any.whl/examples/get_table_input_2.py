"""
cooked input examples of getting inputs from tables

Len Wanger, 2017

TODO -
    - basic table
    - basic table with tags
    - multi-column table
    - dynamic table
    - title, header and footer
    - default choice
    - item_data
    - rows_per_page
    - enabled/disabled
    - filtered
    - actions
    - navigation keys

    - table: options
        required            requires an entry if True, exits the menu on blank entry if False
        add_exit            automatically adds a MenuItem to exit the menu (MENU_ADD_EXIT - default) or return to the
                            parent menu (MENU_ADD_RETURN), or not to add a MenuItem at all (False)
        action_dict         a dictionary of values to pass to action functions. Used to provide context to the action
        case_sensitive      whether choosing menu items should be case sensitive (True) or not (False - default)
        item_filter         a function used to determine which menu items to display. An item is display if the function returns True for the item.
                                All items are displayed if item_filter is None (default)
        refresh             refresh menu items each time the menu is shown (True - default), or just when created (False). Useful for dynamic menus
        item_filter              a function used to filter menu items. MenuItem is shown if returns True, and not if False
        header              a format string to print before the table, can use any value from action_dict as well as pagination information
        footer              a format string to print after the table, can use any values from action_dict as well as pagination information
"""

from cooked_input import get_table_input, Table, TableItem, get_menu

def return_color_str_action(row, action_dict):
    print('row={},  action_dict={}, row.values[0]={}'.format(row, action_dict, row.values[0]))
    return row.values[0]


def red_action(row, action_dict):
    print('Red action: row={},  action_dict={}'.format(row, action_dict))
    if action_dict['live'] is True:
        return 'Live is True!'
    else:
        return 'Better dead than red!'

def return_rgb_action(row, action_dict):
    # print('return_rgb_action: row={},  action_dict={}'.format(row, action_dict))
    return row.values[2]

if __name__ == '__main__':
    if False:
        table_items = [
            #TableItem(col_values, tag=None, action=TABLE_DEFAULT_ACTION, item_data=None, hidden=False, enabled=True):
            TableItem('red'),
            TableItem('blue'),
            TableItem('green'),
        ]

        # get value from table with default action (get row)
        table = Table(table_items, col_names=['Color'])
        color = get_table_input(table, do_action=False)
        color_row = table.do_action(color)
        print('color_str={}, color id={}, color_row={}'.format(color_row, color.tag, color_row))

        # get value from table with specified default action (get values[0] - color name)
        table = Table(table_items, col_names=['Color'], default_action=return_color_str_action, prompt='Color? (Table prompt) ')
        color = get_table_input(table, do_action=False)
        color_str = table.do_action(color)
        print('color_str={}, color={}, color id={}'.format(color_str, color, color.tag))

        # test - do_action = True and action specified on table item
        table_items[0] = TableItem('red', action=red_action)
        table = Table(table_items, col_names=['Color'], default_action=return_color_str_action, action_dict={'live': False})
        color = get_table_input(table, prompt='Color id',
                                convertor_error_fmt='not a valid color id',
                                validator_error_fmt='not a valid color id', do_action=True)
        print('color={}'.format(color))

        # test - running the table
        print('running table...')
        table.run()
        print('done running table...')

        # test default choice
        result = get_menu(['red', 'green', 'blue'], title='Colors', prompt='Choose a color', default_choice='blue', add_exit=False)
        print('result={}'.format(result))

    # Test multiple columns
    if True:
        table_items = [
            # TableItem(col_values, tag=None, action=TABLE_DEFAULT_ACTION, item_data=None, hidden=False, enabled=True):
            TableItem(['red', 'roses are red', (255,0,0)]),
            TableItem(['blue', 'violets are blue', (0,255,0)]),
            TableItem(['green', 'green is the color of my true love\'s eyes', (0,0,255)]),
        ]

        table = Table(table_items, col_names=['Color', 'Ode', 'RGB'], default_action=return_rgb_action)
        rgb = get_table_input(table, prompt='Enter the id of the color you want',
                                convertor_error_fmt='not a valid color id',
                                validator_error_fmt='not a valid color id')
        print('rgb={}, r={}, g={}, b={}'.format(rgb, rgb[0], rgb[1], rgb[2]))



