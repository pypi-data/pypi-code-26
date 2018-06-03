# layouts tests

import layouts
import pytest

@pytest.fixture
def layout_mgr():
    '''
    Layout manager setup
    '''
    return layouts.Layouts()

@pytest.fixture
def default_layout(layout_mgr):
    '''
    Retrieve default layout
    '''
    layout_name = 'default'
    return layout_mgr.get_layout(layout_name)

def test_list_layouts(layout_mgr):
    '''
    Make sure we can retrieve at least one layout
    '''
    assert layout_mgr.list_layouts()

def test_default_layout(default_layout):
    '''
    Make sure we can retrieve the default layout
    '''
    layout_name = 'default'
    assert default_layout.name() == layout_name

def test_locale_lookup(layout_mgr):
    '''
    Make sure the HID locale lookup is behaving correctly
    '''
    layout_name = 'default'
    layout = layout_mgr.get_layout(layout_name)
    assert layout.locale() == (0, 'Undefined')

    layout_name = 'en_US'
    layout = layout_mgr.get_layout(layout_name)
    assert layout.locale() == (33, 'US')

def test_usb_hid_keyboard_code_squash(layout_mgr):
    '''
    Test to make sure HID keyboard codes are squashed as expected
    '''
    #layout_name = 'default'
    #layout = layout_mgr.get_layout(layout_name)
    # TODO - Need example to squash

def test_string_compose(default_layout):
    '''
    Test string compose from a layout
    '''
    test_string = 'Hello World!'
    result = default_layout.compose(test_string)

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

    # Convert list of list to a list of tuples
    result_set = map(tuple, result)
    compare_set = map(tuple, compare)

    # Compare elements
    failed_compares = []
    for item in zip(result_set, compare_set):
        print(item)
        if item[0] != item[1]:
            failed_compares.append(item)

    assert not failed_compares

def test_string_compose_minimal(default_layout):
    '''
    Test string compose from a layout, using minimal clears
    '''
    test_string = 'Hello World!'
    result = default_layout.compose(test_string, minimal_clears=True)

    # Empty combos are used to clear key-state
    compare = [
        ["Shift", "H"],
        ["E"],
        ["L"], [],
        ["L"],
        ["O"],
        ["Space"],
        ["Shift", "W"],
        ["O"],
        ["R"],
        ["L"],
        ["D"],
        ["Shift", "1"], [],
    ]

    # Convert list of list to a list of tuples
    result_set = map(tuple, result)
    compare_set = map(tuple, compare)

    # Compare elements
    failed_compares = []
    for item in zip(result_set, compare_set):
        print(item)
        if item[0] != item[1]:
            failed_compares.append(item)

    assert not failed_compares

