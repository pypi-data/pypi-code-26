###############################################################################
#
#   Copyright: (c) 2015-2018 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from onyx.core import GetObj, AddObj, ObjNotFound, ObjDbTransaction
from onyx.core import ValueType, GetVal

from .ufo_fund_group import FundGroup
from .ufo_notification_record import NotificationRecord

__all__ = ["AssetManager"]


###############################################################################
class AssetManager(FundGroup):
    """
    Class used to represent an asset manager entity. AssetManager is
    implemented a subclass of FundGroup.
    """
    # -------------------------------------------------------------------------
    @ValueType("Callable")
    def NotificationBySecurity(self, graph, security):
        isin = graph(security, "Isin")
        if isin is None:
            raise RuntimeError("ISIN not available for {0:s}".format(security))

        record_id = "{0:s} - {1:s}".format(self.Name, isin)

        try:
            return graph(record_id, "LastNotification")
        except ObjNotFound:
            return None

    # -------------------------------------------------------------------------
    def notification_of_short_position(self, security, date, units, pct):
        isin = GetVal(security, "Isin")
        if isin is None:
            raise RuntimeError("ISIN not available for {0:s}".format(security))

        record_id = "{0:s} - {1:s}".format(self.Name, isin)

        try:
            record = GetObj(record_id)
        except ObjNotFound:
            record = AddObj(NotificationRecord(Name=record_id))

        with ObjDbTransaction("notification of short position"):
            record.set_dated("Units", date, units)
            record.set_dated("Percentage", date, pct)


# -----------------------------------------------------------------------------
def prepare_for_test():
    pass
