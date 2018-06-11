# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.


import logging

import mock

from cubicweb.devtools import testlib

from cubes.sentry.patches import (
    add_sentry_support,
    logger as sentry_cube_logger,
)


class LoggerConfigTC(testlib.CubicWebTC):

    @classmethod
    def setUpClass(cls):
        super(LoggerConfigTC, cls).setUpClass()
        add_sentry_support('https://public:secret@example.com/123',
                           logging.ERROR)

    def test_emit_on_exception(self):
        logger = logging.getLogger('test_logger')
        logger.setLevel(logging.ERROR)
        try:
            raise Exception("Excepted")
        except Exception:
            with mock.patch(
                    'raven.handlers.logging.SentryHandler.emit') as emit:
                logger.exception("Catched")

                emit.assert_called_once()
                self.assertEquals(emit.call_args[0][0].msg, "Catched")

    def test_do_not_emit_on_sentry_cube_logs(self):
        try:
            raise Exception("Excepted")
        except Exception:
            with mock.patch(
                    'raven.handlers.logging.SentryHandler.emit') as emit:
                sentry_cube_logger.exception("Not emitted")

                emit.assert_not_called()
