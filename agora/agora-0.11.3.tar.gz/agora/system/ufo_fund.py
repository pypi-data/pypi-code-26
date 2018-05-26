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

from onyx.core import Structure
from onyx.core import CreateInMemory, Archivable, ValueType
from onyx.core import ReferenceField, FloatField

from onyx.core import DiscardInheritedAttribute
from onyx.core import MktIndirectionFactory, EnforceArchivableEntitlements

from .ufo_portfolio import Portfolio as UfoPortfolio
from ..risk.decorators import WithRiskValueTypes

__all__ = ["Fund"]


###############################################################################
@WithRiskValueTypes
@EnforceArchivableEntitlements("Database", "ArchivedOverwritable")
@DiscardInheritedAttribute(["Children"])
class Fund(UfoPortfolio, Archivable):
    """
    Class used to represent an investment Fund. This is implemented as a
    subclass of Portfolio.
    """
    # --- this portfolio captures all investments
    Portfolio = ReferenceField(obj_type="Portfolio")
    # --- this book captures subscriptions/redemptions as well as costs and
    #     amortized costs
    CashAccount = ReferenceField(obj_type="Book")

    # -------------------------------------------------------------------------
    @ValueType()
    def Children(self, graph):
        port_kids = graph(graph(self, "Portfolio"), "Children")
        cash_kids = graph(graph(self, "CashAccount"), "Children")
        return port_kids + cash_kids

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def PortfolioBy(self, graph, key=None, value=None):
        children = Structure()
        for book in graph(self, "Books"):
            parms = graph(book, "AttributionParms")
            if value in parms[key]:
                children += Structure({book: 1.0 / len(parms[key])})

        name = "Tmp {0:s} - {1:s}".format(self.Name, value)
        ccy = graph(self, "Denominated")
        port = UfoPortfolio(Name=name, Denominated=ccy, Children=children)
        port = CreateInMemory(port)

        return port.Name

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def FilteredChildren(self, graph, target=None, level=0):
        if level == 0:
            kids = [kid for kid in graph(self, "Children") if target in kid]
            kids = Structure.fromkeys(kids, 1)
        elif level == 1:
            kids = Structure()
            for port in graph(self, "Children"):
                gradkids = graph(port, "Children")
                gradkids = [gk for gk in gradkids if target in gk]
                kids += Structure.fromkeys(gradkids, 1)
        else:
            raise RuntimeError("level cannot be higher than 1")
        return kids

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def Aggregate(self, graph, target=None, level=0):
        kids = graph(self, "FilteredChildren", target=target, level=level)
        name = "Tmp {0:s} - {1:s}".format(self.Name, target)
        ccy = graph(self, "Denominated")
        port = UfoPortfolio(Name=name, Denominated=ccy, Children=kids)
        port = CreateInMemory(port)
        return port.Name

    # -------------------------------------------------------------------------
    @MktIndirectionFactory(FloatField)
    def Nav(self, graph):
        pass

    # -------------------------------------------------------------------------
    @MktIndirectionFactory(FloatField)
    def Gav(self, graph):
        pass

    # -------------------------------------------------------------------------
    @MktIndirectionFactory(FloatField)
    def Aum(self, graph):
        pass

    # -------------------------------------------------------------------------
    @MktIndirectionFactory(FloatField)
    def NumberOfShares(self, graph):
        pass

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def NavCurve(self, graph, start=None, end=None):
        return self.get_history("Nav", start, end)

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def GavCurve(self, graph, start=None, end=None):
        return self.get_history("Gav", start, end)

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def AumCurve(self, graph, start=None, end=None):
        return self.get_history("Aum", start, end)
