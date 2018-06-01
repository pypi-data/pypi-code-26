# layouts cache download tests

import layouts
import pytest

def test_local_cache():
    '''
    Test local cache check
    '''
    # TODO - Implement local cache
    pass

def test_github_cache():
    '''
    Test GitHub cache
    '''
    # TODO (HaaTa) - Make sure test is actually working as expected (i.e. clearing cache and downloading)
    mgr = layouts.Layouts(force_refresh=True)
    assert mgr.list_layouts()

