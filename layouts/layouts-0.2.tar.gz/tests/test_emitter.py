# layouts tests

import layouts
import layouts.emitter
import pytest

@pytest.fixture
def layout_mgr():
    '''
    Layout manager setup
    '''
    return layouts.Layouts()

def test_c_defines(layout_mgr):
    '''
    Make sure we can generate c defines
    '''
    layout_name = 'default'
    layout = layout_mgr.get_layout(layout_name)

    assert layouts.emitter.basic_c_defines(layout)

