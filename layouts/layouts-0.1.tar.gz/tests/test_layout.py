# layouts tests

import layouts
import pytest

@pytest.fixture
def layout_mgr():
    '''
    Layout manager setup
    '''
    return layouts.Layouts()

def test_list_layouts(layout_mgr):
    '''
    Make sure we can retrieve at least one layout
    '''
    assert layout_mgr.list_layouts()

def test_default_layout(layout_mgr):
    '''
    Make sure we can retrieve the default layout
    '''
    layout_name = 'default'
    layout = layout_mgr.get_layout(layout_name)
    assert layout.name() == layout_name

def test_usb_hid_keyboard_code_squash(layout_mgr):
    '''
    Test to make sure HID keyboard codes are squashed as expected
    '''
    #layout_name = 'default'
    #layout = layout_mgr.get_layout(layout_name)
    # TODO - Need example to squash

def test_string_compose(layout_mgr):
    '''
    Test string compose from a layout
    '''
    layout_name = 'default'
    layout = layout_mgr.get_layout(layout_name)

    test_string = 'Hello World!'
    result = layout.compose(test_string)
    print(result)

    # Empty combos are used to clear key-state
    compare = [
        ["Shift", "H"], [],
        ["E"], [],
        ["L"], [],
        ["L"], [],
        ["O"], [],
        ["Space"], [],
        ["Shift", "W"], [],
        ["O"], [],
        ["R"], [],
        ["L"], [],
        ["D"], [],
        ["Shift", "1"], [],
    ]

    # Convert list of list to sets of tuples
    result_set = set(map(tuple, result))
    compare_set = set(map(tuple, compare))

    difference = result_set ^ compare_set
    assert not difference

