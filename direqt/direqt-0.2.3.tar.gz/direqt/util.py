"""Utility Functions."""
import os

__all__ = [
    'detect_gae',
]


def detect_gae():
    """Determine whether or not we're running on GAE.

    The SERVER_SOFTWARE variable starts with 'Development/' when running via
    dev_appserver.py.

    Returns:
      True iff we're running on GAE.
    """
    server_software = os.environ.get('SERVER_SOFTWARE', '')
    return (server_software.startswith('Development/') or
            server_software.startswith('Google App Engine/'))
