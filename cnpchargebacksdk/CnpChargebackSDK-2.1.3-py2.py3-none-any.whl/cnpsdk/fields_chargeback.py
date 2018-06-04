# ./fields_chargeback.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:37e810e0ed20ae97cbb857a604d79e40b685ff87
# Generated 2018-04-18 13:50:46.537333 by PyXB version 1.2.5 using Python 2.7.14.final.0
# Namespace http://www.vantivcnp.com/chargebacks

from __future__ import unicode_literals
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import io
import pyxb.utils.utility
import pyxb.utils.domutils
import sys
import pyxb.utils.six as _six
# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:05b9e53e-4331-11e8-ad50-001a4a010781')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.5'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# A holder for module-level binding classes so we can access them from
# inside class definitions where property names may conflict.
_module_typeBindings = pyxb.utils.utility.Object()

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.NamespaceForURI('http://www.vantivcnp.com/chargebacks', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.

    @param xml_text An XML document.  This should be data (Python 2
    str or Python 3 bytes), or a text (Python 2 unicode or Python 3
    str) in the L{pyxb._InputEncoding} encoding.

    @keyword default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement, default_namespace=default_namespace)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    xmld = xml_text
    if isinstance(xmld, _six.text_type):
        xmld = xmld.encode(pyxb._InputEncoding)
    saxer.parse(io.BytesIO(xmld))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, default_namespace)


# Atomic simple type: [anonymous]
class STD_ANON (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 76, 8)
    _Documentation = None
STD_ANON._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(25))
STD_ANON._CF_minLength = pyxb.binding.facets.CF_minLength(value=pyxb.binding.datatypes.nonNegativeInteger(1))
STD_ANON._InitializeFacetMap(STD_ANON._CF_maxLength,
   STD_ANON._CF_minLength)
_module_typeBindings.STD_ANON = STD_ANON

# Atomic simple type: [anonymous]
class STD_ANON_ (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 84, 8)
    _Documentation = None
STD_ANON_._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(4000))
STD_ANON_._CF_minLength = pyxb.binding.facets.CF_minLength(value=pyxb.binding.datatypes.nonNegativeInteger(1))
STD_ANON_._InitializeFacetMap(STD_ANON_._CF_maxLength,
   STD_ANON_._CF_minLength)
_module_typeBindings.STD_ANON_ = STD_ANON_

# Atomic simple type: {http://www.vantivcnp.com/chargebacks}activityType
class activityType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'activityType')
    _XSDLocation = pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 113, 2)
    _Documentation = None
activityType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=activityType, enum_prefix=None)
activityType.ASSIGN_TO_USER = activityType._CF_enumeration.addEnumeration(unicode_value='ASSIGN_TO_USER', tag='ASSIGN_TO_USER')
activityType.ADD_NOTE = activityType._CF_enumeration.addEnumeration(unicode_value='ADD_NOTE', tag='ADD_NOTE')
activityType.MERCHANT_ACCEPTS_LIABILITY = activityType._CF_enumeration.addEnumeration(unicode_value='MERCHANT_ACCEPTS_LIABILITY', tag='MERCHANT_ACCEPTS_LIABILITY')
activityType.MERCHANT_REPRESENT = activityType._CF_enumeration.addEnumeration(unicode_value='MERCHANT_REPRESENT', tag='MERCHANT_REPRESENT')
activityType.MERCHANT_RESPOND = activityType._CF_enumeration.addEnumeration(unicode_value='MERCHANT_RESPOND', tag='MERCHANT_RESPOND')
activityType.MERCHANT_REQUESTS_ARBITRATION = activityType._CF_enumeration.addEnumeration(unicode_value='MERCHANT_REQUESTS_ARBITRATION', tag='MERCHANT_REQUESTS_ARBITRATION')
activityType._InitializeFacetMap(activityType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'activityType', activityType)
_module_typeBindings.activityType = activityType

# Complex type {http://www.vantivcnp.com/chargebacks}chargebackApiActivity with content type ELEMENT_ONLY
class chargebackApiActivity (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.vantivcnp.com/chargebacks}chargebackApiActivity with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'chargebackApiActivity')
    _XSDLocation = pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 14, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.vantivcnp.com/chargebacks}activityDate uses Python identifier activityDate
    __activityDate = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'activityDate'), 'activityDate', '__httpwww_vantivcnp_comchargebacks_chargebackApiActivity_httpwww_vantivcnp_comchargebacksactivityDate', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 16, 6), )

    
    activityDate = property(__activityDate.value, __activityDate.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}activityType uses Python identifier activityType
    __activityType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'activityType'), 'activityType', '__httpwww_vantivcnp_comchargebacks_chargebackApiActivity_httpwww_vantivcnp_comchargebacksactivityType', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 17, 6), )

    
    activityType = property(__activityType.value, __activityType.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}fromQueue uses Python identifier fromQueue
    __fromQueue = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'fromQueue'), 'fromQueue', '__httpwww_vantivcnp_comchargebacks_chargebackApiActivity_httpwww_vantivcnp_comchargebacksfromQueue', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 18, 6), )

    
    fromQueue = property(__fromQueue.value, __fromQueue.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}toQueue uses Python identifier toQueue
    __toQueue = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'toQueue'), 'toQueue', '__httpwww_vantivcnp_comchargebacks_chargebackApiActivity_httpwww_vantivcnp_comchargebackstoQueue', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 19, 6), )

    
    toQueue = property(__toQueue.value, __toQueue.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}settlementAmount uses Python identifier settlementAmount
    __settlementAmount = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'settlementAmount'), 'settlementAmount', '__httpwww_vantivcnp_comchargebacks_chargebackApiActivity_httpwww_vantivcnp_comchargebackssettlementAmount', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 20, 6), )

    
    settlementAmount = property(__settlementAmount.value, __settlementAmount.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}settlementCurrencyType uses Python identifier settlementCurrencyType
    __settlementCurrencyType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'settlementCurrencyType'), 'settlementCurrencyType', '__httpwww_vantivcnp_comchargebacks_chargebackApiActivity_httpwww_vantivcnp_comchargebackssettlementCurrencyType', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 21, 6), )

    
    settlementCurrencyType = property(__settlementCurrencyType.value, __settlementCurrencyType.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}notes uses Python identifier notes
    __notes = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'notes'), 'notes', '__httpwww_vantivcnp_comchargebacks_chargebackApiActivity_httpwww_vantivcnp_comchargebacksnotes', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 22, 6), )

    
    notes = property(__notes.value, __notes.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}assignedTo uses Python identifier assignedTo
    __assignedTo = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'assignedTo'), 'assignedTo', '__httpwww_vantivcnp_comchargebacks_chargebackApiActivity_httpwww_vantivcnp_comchargebacksassignedTo', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 23, 6), )

    
    assignedTo = property(__assignedTo.value, __assignedTo.set, None, None)

    _ElementMap.update({
        __activityDate.name() : __activityDate,
        __activityType.name() : __activityType,
        __fromQueue.name() : __fromQueue,
        __toQueue.name() : __toQueue,
        __settlementAmount.name() : __settlementAmount,
        __settlementCurrencyType.name() : __settlementCurrencyType,
        __notes.name() : __notes,
        __assignedTo.name() : __assignedTo
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.chargebackApiActivity = chargebackApiActivity
Namespace.addCategoryObject('typeBinding', 'chargebackApiActivity', chargebackApiActivity)


# Complex type {http://www.vantivcnp.com/chargebacks}chargebackApiCase with content type ELEMENT_ONLY
class chargebackApiCase (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.vantivcnp.com/chargebacks}chargebackApiCase with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'chargebackApiCase')
    _XSDLocation = pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 27, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.vantivcnp.com/chargebacks}caseId uses Python identifier caseId
    __caseId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'caseId'), 'caseId', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackscaseId', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 29, 6), )

    
    caseId = property(__caseId.value, __caseId.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}merchantId uses Python identifier merchantId
    __merchantId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'merchantId'), 'merchantId', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksmerchantId', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 30, 6), )

    
    merchantId = property(__merchantId.value, __merchantId.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}dayIssuedByBank uses Python identifier dayIssuedByBank
    __dayIssuedByBank = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'dayIssuedByBank'), 'dayIssuedByBank', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksdayIssuedByBank', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 31, 6), )

    
    dayIssuedByBank = property(__dayIssuedByBank.value, __dayIssuedByBank.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}dateReceivedByVantivCnp uses Python identifier dateReceivedByVantivCnp
    __dateReceivedByVantivCnp = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'dateReceivedByVantivCnp'), 'dateReceivedByVantivCnp', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksdateReceivedByVantivCnp', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 32, 6), )

    
    dateReceivedByVantivCnp = property(__dateReceivedByVantivCnp.value, __dateReceivedByVantivCnp.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}vantivCnpTxnId uses Python identifier vantivCnpTxnId
    __vantivCnpTxnId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'vantivCnpTxnId'), 'vantivCnpTxnId', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksvantivCnpTxnId', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 33, 6), )

    
    vantivCnpTxnId = property(__vantivCnpTxnId.value, __vantivCnpTxnId.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}cycle uses Python identifier cycle
    __cycle = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'cycle'), 'cycle', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackscycle', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 34, 6), )

    
    cycle = property(__cycle.value, __cycle.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}orderId uses Python identifier orderId
    __orderId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'orderId'), 'orderId', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksorderId', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 35, 6), )

    
    orderId = property(__orderId.value, __orderId.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}cardNumberLast4 uses Python identifier cardNumberLast4
    __cardNumberLast4 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'cardNumberLast4'), 'cardNumberLast4', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackscardNumberLast4', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 36, 6), )

    
    cardNumberLast4 = property(__cardNumberLast4.value, __cardNumberLast4.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}cardType uses Python identifier cardType
    __cardType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'cardType'), 'cardType', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackscardType', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 37, 6), )

    
    cardType = property(__cardType.value, __cardType.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}chargebackAmount uses Python identifier chargebackAmount
    __chargebackAmount = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'chargebackAmount'), 'chargebackAmount', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackschargebackAmount', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 38, 6), )

    
    chargebackAmount = property(__chargebackAmount.value, __chargebackAmount.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}chargebackCurrencyType uses Python identifier chargebackCurrencyType
    __chargebackCurrencyType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'chargebackCurrencyType'), 'chargebackCurrencyType', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackschargebackCurrencyType', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 39, 6), )

    
    chargebackCurrencyType = property(__chargebackCurrencyType.value, __chargebackCurrencyType.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}originalTxnDay uses Python identifier originalTxnDay
    __originalTxnDay = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'originalTxnDay'), 'originalTxnDay', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksoriginalTxnDay', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 40, 6), )

    
    originalTxnDay = property(__originalTxnDay.value, __originalTxnDay.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}chargebackType uses Python identifier chargebackType
    __chargebackType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'chargebackType'), 'chargebackType', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackschargebackType', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 41, 6), )

    
    chargebackType = property(__chargebackType.value, __chargebackType.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}representedAmount uses Python identifier representedAmount
    __representedAmount = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'representedAmount'), 'representedAmount', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksrepresentedAmount', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 42, 6), )

    
    representedAmount = property(__representedAmount.value, __representedAmount.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}representedCurrencyType uses Python identifier representedCurrencyType
    __representedCurrencyType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'representedCurrencyType'), 'representedCurrencyType', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksrepresentedCurrencyType', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 43, 6), )

    
    representedCurrencyType = property(__representedCurrencyType.value, __representedCurrencyType.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}reasonCode uses Python identifier reasonCode
    __reasonCode = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'reasonCode'), 'reasonCode', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksreasonCode', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 44, 6), )

    
    reasonCode = property(__reasonCode.value, __reasonCode.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}reasonCodeDescription uses Python identifier reasonCodeDescription
    __reasonCodeDescription = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'reasonCodeDescription'), 'reasonCodeDescription', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksreasonCodeDescription', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 45, 6), )

    
    reasonCodeDescription = property(__reasonCodeDescription.value, __reasonCodeDescription.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}currentQueue uses Python identifier currentQueue
    __currentQueue = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'currentQueue'), 'currentQueue', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackscurrentQueue', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 46, 6), )

    
    currentQueue = property(__currentQueue.value, __currentQueue.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}fraudNotificationStatus uses Python identifier fraudNotificationStatus
    __fraudNotificationStatus = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'fraudNotificationStatus'), 'fraudNotificationStatus', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksfraudNotificationStatus', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 47, 6), )

    
    fraudNotificationStatus = property(__fraudNotificationStatus.value, __fraudNotificationStatus.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}acquirerReferenceNumber uses Python identifier acquirerReferenceNumber
    __acquirerReferenceNumber = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'acquirerReferenceNumber'), 'acquirerReferenceNumber', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksacquirerReferenceNumber', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 48, 6), )

    
    acquirerReferenceNumber = property(__acquirerReferenceNumber.value, __acquirerReferenceNumber.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}chargebackReferenceNumber uses Python identifier chargebackReferenceNumber
    __chargebackReferenceNumber = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'chargebackReferenceNumber'), 'chargebackReferenceNumber', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackschargebackReferenceNumber', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 49, 6), )

    
    chargebackReferenceNumber = property(__chargebackReferenceNumber.value, __chargebackReferenceNumber.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}preArbitrationAmount uses Python identifier preArbitrationAmount
    __preArbitrationAmount = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'preArbitrationAmount'), 'preArbitrationAmount', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackspreArbitrationAmount', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 50, 6), )

    
    preArbitrationAmount = property(__preArbitrationAmount.value, __preArbitrationAmount.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}preArbitrationCurrencyType uses Python identifier preArbitrationCurrencyType
    __preArbitrationCurrencyType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'preArbitrationCurrencyType'), 'preArbitrationCurrencyType', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackspreArbitrationCurrencyType', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 51, 6), )

    
    preArbitrationCurrencyType = property(__preArbitrationCurrencyType.value, __preArbitrationCurrencyType.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}merchantTxnId uses Python identifier merchantTxnId
    __merchantTxnId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'merchantTxnId'), 'merchantTxnId', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksmerchantTxnId', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 52, 6), )

    
    merchantTxnId = property(__merchantTxnId.value, __merchantTxnId.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}fraudNotificationDate uses Python identifier fraudNotificationDate
    __fraudNotificationDate = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'fraudNotificationDate'), 'fraudNotificationDate', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksfraudNotificationDate', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 53, 6), )

    
    fraudNotificationDate = property(__fraudNotificationDate.value, __fraudNotificationDate.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}bin uses Python identifier bin
    __bin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'bin'), 'bin', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksbin', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 54, 6), )

    
    bin = property(__bin.value, __bin.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}token uses Python identifier token
    __token = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'token'), 'token', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackstoken', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 55, 6), )

    
    token = property(__token.value, __token.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}historicalWinPercentage uses Python identifier historicalWinPercentage
    __historicalWinPercentage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'historicalWinPercentage'), 'historicalWinPercentage', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackshistoricalWinPercentage', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 56, 6), )

    
    historicalWinPercentage = property(__historicalWinPercentage.value, __historicalWinPercentage.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}customerId uses Python identifier customerId
    __customerId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'customerId'), 'customerId', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackscustomerId', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 57, 6), )

    
    customerId = property(__customerId.value, __customerId.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}paymentAmount uses Python identifier paymentAmount
    __paymentAmount = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'paymentAmount'), 'paymentAmount', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackspaymentAmount', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 58, 6), )

    
    paymentAmount = property(__paymentAmount.value, __paymentAmount.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}paymentSecondaryAmount uses Python identifier paymentSecondaryAmount
    __paymentSecondaryAmount = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'paymentSecondaryAmount'), 'paymentSecondaryAmount', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebackspaymentSecondaryAmount', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 59, 6), )

    
    paymentSecondaryAmount = property(__paymentSecondaryAmount.value, __paymentSecondaryAmount.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}replyByDay uses Python identifier replyByDay
    __replyByDay = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'replyByDay'), 'replyByDay', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksreplyByDay', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 60, 6), )

    
    replyByDay = property(__replyByDay.value, __replyByDay.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}activity uses Python identifier activity
    __activity = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'activity'), 'activity', '__httpwww_vantivcnp_comchargebacks_chargebackApiCase_httpwww_vantivcnp_comchargebacksactivity', True, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 61, 6), )

    
    activity = property(__activity.value, __activity.set, None, None)

    _ElementMap.update({
        __caseId.name() : __caseId,
        __merchantId.name() : __merchantId,
        __dayIssuedByBank.name() : __dayIssuedByBank,
        __dateReceivedByVantivCnp.name() : __dateReceivedByVantivCnp,
        __vantivCnpTxnId.name() : __vantivCnpTxnId,
        __cycle.name() : __cycle,
        __orderId.name() : __orderId,
        __cardNumberLast4.name() : __cardNumberLast4,
        __cardType.name() : __cardType,
        __chargebackAmount.name() : __chargebackAmount,
        __chargebackCurrencyType.name() : __chargebackCurrencyType,
        __originalTxnDay.name() : __originalTxnDay,
        __chargebackType.name() : __chargebackType,
        __representedAmount.name() : __representedAmount,
        __representedCurrencyType.name() : __representedCurrencyType,
        __reasonCode.name() : __reasonCode,
        __reasonCodeDescription.name() : __reasonCodeDescription,
        __currentQueue.name() : __currentQueue,
        __fraudNotificationStatus.name() : __fraudNotificationStatus,
        __acquirerReferenceNumber.name() : __acquirerReferenceNumber,
        __chargebackReferenceNumber.name() : __chargebackReferenceNumber,
        __preArbitrationAmount.name() : __preArbitrationAmount,
        __preArbitrationCurrencyType.name() : __preArbitrationCurrencyType,
        __merchantTxnId.name() : __merchantTxnId,
        __fraudNotificationDate.name() : __fraudNotificationDate,
        __bin.name() : __bin,
        __token.name() : __token,
        __historicalWinPercentage.name() : __historicalWinPercentage,
        __customerId.name() : __customerId,
        __paymentAmount.name() : __paymentAmount,
        __paymentSecondaryAmount.name() : __paymentSecondaryAmount,
        __replyByDay.name() : __replyByDay,
        __activity.name() : __activity
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.chargebackApiCase = chargebackApiCase
Namespace.addCategoryObject('typeBinding', 'chargebackApiCase', chargebackApiCase)


# Complex type {http://www.vantivcnp.com/chargebacks}chargebackRetrievalResponse with content type ELEMENT_ONLY
class chargebackRetrievalResponse_ (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.vantivcnp.com/chargebacks}chargebackRetrievalResponse with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'chargebackRetrievalResponse')
    _XSDLocation = pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 65, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.vantivcnp.com/chargebacks}transactionId uses Python identifier transactionId
    __transactionId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'transactionId'), 'transactionId', '__httpwww_vantivcnp_comchargebacks_chargebackRetrievalResponse__httpwww_vantivcnp_comchargebackstransactionId', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 67, 6), )

    
    transactionId = property(__transactionId.value, __transactionId.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}chargebackCase uses Python identifier chargebackCase
    __chargebackCase = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'chargebackCase'), 'chargebackCase', '__httpwww_vantivcnp_comchargebacks_chargebackRetrievalResponse__httpwww_vantivcnp_comchargebackschargebackCase', True, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 68, 6), )

    
    chargebackCase = property(__chargebackCase.value, __chargebackCase.set, None, None)

    _ElementMap.update({
        __transactionId.name() : __transactionId,
        __chargebackCase.name() : __chargebackCase
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.chargebackRetrievalResponse_ = chargebackRetrievalResponse_
Namespace.addCategoryObject('typeBinding', 'chargebackRetrievalResponse', chargebackRetrievalResponse_)


# Complex type {http://www.vantivcnp.com/chargebacks}chargebackUpdateRequest with content type ELEMENT_ONLY
class chargebackUpdateRequest_ (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.vantivcnp.com/chargebacks}chargebackUpdateRequest with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'chargebackUpdateRequest')
    _XSDLocation = pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 72, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.vantivcnp.com/chargebacks}activityType uses Python identifier activityType
    __activityType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'activityType'), 'activityType', '__httpwww_vantivcnp_comchargebacks_chargebackUpdateRequest__httpwww_vantivcnp_comchargebacksactivityType', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 74, 6), )

    
    activityType = property(__activityType.value, __activityType.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}assignedTo uses Python identifier assignedTo
    __assignedTo = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'assignedTo'), 'assignedTo', '__httpwww_vantivcnp_comchargebacks_chargebackUpdateRequest__httpwww_vantivcnp_comchargebacksassignedTo', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 75, 6), )

    
    assignedTo = property(__assignedTo.value, __assignedTo.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}note uses Python identifier note
    __note = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'note'), 'note', '__httpwww_vantivcnp_comchargebacks_chargebackUpdateRequest__httpwww_vantivcnp_comchargebacksnote', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 83, 6), )

    
    note = property(__note.value, __note.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}representedAmount uses Python identifier representedAmount
    __representedAmount = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'representedAmount'), 'representedAmount', '__httpwww_vantivcnp_comchargebacks_chargebackUpdateRequest__httpwww_vantivcnp_comchargebacksrepresentedAmount', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 91, 6), )

    
    representedAmount = property(__representedAmount.value, __representedAmount.set, None, None)

    _ElementMap.update({
        __activityType.name() : __activityType,
        __assignedTo.name() : __assignedTo,
        __note.name() : __note,
        __representedAmount.name() : __representedAmount
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.chargebackUpdateRequest_ = chargebackUpdateRequest_
Namespace.addCategoryObject('typeBinding', 'chargebackUpdateRequest', chargebackUpdateRequest_)


# Complex type {http://www.vantivcnp.com/chargebacks}chargebackUpdateResponse with content type ELEMENT_ONLY
class chargebackUpdateResponse_ (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.vantivcnp.com/chargebacks}chargebackUpdateResponse with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'chargebackUpdateResponse')
    _XSDLocation = pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 95, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.vantivcnp.com/chargebacks}transactionId uses Python identifier transactionId
    __transactionId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'transactionId'), 'transactionId', '__httpwww_vantivcnp_comchargebacks_chargebackUpdateResponse__httpwww_vantivcnp_comchargebackstransactionId', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 97, 6), )

    
    transactionId = property(__transactionId.value, __transactionId.set, None, None)

    _ElementMap.update({
        __transactionId.name() : __transactionId
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.chargebackUpdateResponse_ = chargebackUpdateResponse_
Namespace.addCategoryObject('typeBinding', 'chargebackUpdateResponse', chargebackUpdateResponse_)


# Complex type {http://www.vantivcnp.com/chargebacks}errorResponse with content type ELEMENT_ONLY
class errorResponse_ (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.vantivcnp.com/chargebacks}errorResponse with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'errorResponse')
    _XSDLocation = pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 101, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.vantivcnp.com/chargebacks}errors uses Python identifier errors
    __errors = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'errors'), 'errors', '__httpwww_vantivcnp_comchargebacks_errorResponse__httpwww_vantivcnp_comchargebackserrors', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 103, 6), )

    
    errors = property(__errors.value, __errors.set, None, None)

    _ElementMap.update({
        __errors.name() : __errors
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.errorResponse_ = errorResponse_
Namespace.addCategoryObject('typeBinding', 'errorResponse', errorResponse_)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    """Complex type [anonymous] with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 104, 8)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.vantivcnp.com/chargebacks}error uses Python identifier error
    __error = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'error'), 'error', '__httpwww_vantivcnp_comchargebacks_CTD_ANON_httpwww_vantivcnp_comchargebackserror', True, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 106, 12), )

    
    error = property(__error.value, __error.set, None, None)

    _ElementMap.update({
        __error.name() : __error
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON = CTD_ANON


# Complex type {http://www.vantivcnp.com/chargebacks}chargebackDocumentUploadResponse with content type ELEMENT_ONLY
class chargebackDocumentUploadResponse_ (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.vantivcnp.com/chargebacks}chargebackDocumentUploadResponse with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'chargebackDocumentUploadResponse')
    _XSDLocation = pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 124, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.vantivcnp.com/chargebacks}merchantId uses Python identifier merchantId
    __merchantId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'merchantId'), 'merchantId', '__httpwww_vantivcnp_comchargebacks_chargebackDocumentUploadResponse__httpwww_vantivcnp_comchargebacksmerchantId', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 126, 6), )

    
    merchantId = property(__merchantId.value, __merchantId.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}caseId uses Python identifier caseId
    __caseId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'caseId'), 'caseId', '__httpwww_vantivcnp_comchargebacks_chargebackDocumentUploadResponse__httpwww_vantivcnp_comchargebackscaseId', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 127, 6), )

    
    caseId = property(__caseId.value, __caseId.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}documentId uses Python identifier documentId
    __documentId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'documentId'), 'documentId', '__httpwww_vantivcnp_comchargebacks_chargebackDocumentUploadResponse__httpwww_vantivcnp_comchargebacksdocumentId', True, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 128, 6), )

    
    documentId = property(__documentId.value, __documentId.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}responseCode uses Python identifier responseCode
    __responseCode = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'responseCode'), 'responseCode', '__httpwww_vantivcnp_comchargebacks_chargebackDocumentUploadResponse__httpwww_vantivcnp_comchargebacksresponseCode', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 129, 6), )

    
    responseCode = property(__responseCode.value, __responseCode.set, None, None)

    
    # Element {http://www.vantivcnp.com/chargebacks}responseMessage uses Python identifier responseMessage
    __responseMessage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'responseMessage'), 'responseMessage', '__httpwww_vantivcnp_comchargebacks_chargebackDocumentUploadResponse__httpwww_vantivcnp_comchargebacksresponseMessage', False, pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 130, 6), )

    
    responseMessage = property(__responseMessage.value, __responseMessage.set, None, None)

    _ElementMap.update({
        __merchantId.name() : __merchantId,
        __caseId.name() : __caseId,
        __documentId.name() : __documentId,
        __responseCode.name() : __responseCode,
        __responseMessage.name() : __responseMessage
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.chargebackDocumentUploadResponse_ = chargebackDocumentUploadResponse_
Namespace.addCategoryObject('typeBinding', 'chargebackDocumentUploadResponse', chargebackDocumentUploadResponse_)


chargebackRetrievalResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'chargebackRetrievalResponse'), chargebackRetrievalResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 4, 2))
Namespace.addCategoryObject('elementBinding', chargebackRetrievalResponse.name().localName(), chargebackRetrievalResponse)

chargebackUpdateRequest = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'chargebackUpdateRequest'), chargebackUpdateRequest_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 6, 2))
Namespace.addCategoryObject('elementBinding', chargebackUpdateRequest.name().localName(), chargebackUpdateRequest)

chargebackUpdateResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'chargebackUpdateResponse'), chargebackUpdateResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 8, 2))
Namespace.addCategoryObject('elementBinding', chargebackUpdateResponse.name().localName(), chargebackUpdateResponse)

errorResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'errorResponse'), errorResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 10, 2))
Namespace.addCategoryObject('elementBinding', errorResponse.name().localName(), errorResponse)

chargebackDocumentUploadResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'chargebackDocumentUploadResponse'), chargebackDocumentUploadResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 12, 2))
Namespace.addCategoryObject('elementBinding', chargebackDocumentUploadResponse.name().localName(), chargebackDocumentUploadResponse)



chargebackApiActivity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'activityDate'), pyxb.binding.datatypes.date, scope=chargebackApiActivity, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 16, 6)))

chargebackApiActivity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'activityType'), pyxb.binding.datatypes.string, scope=chargebackApiActivity, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 17, 6)))

chargebackApiActivity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'fromQueue'), pyxb.binding.datatypes.string, scope=chargebackApiActivity, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 18, 6)))

chargebackApiActivity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'toQueue'), pyxb.binding.datatypes.string, scope=chargebackApiActivity, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 19, 6)))

chargebackApiActivity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'settlementAmount'), pyxb.binding.datatypes.long, scope=chargebackApiActivity, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 20, 6)))

chargebackApiActivity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'settlementCurrencyType'), pyxb.binding.datatypes.string, scope=chargebackApiActivity, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 21, 6)))

chargebackApiActivity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'notes'), pyxb.binding.datatypes.string, scope=chargebackApiActivity, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 22, 6)))

chargebackApiActivity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'assignedTo'), pyxb.binding.datatypes.string, scope=chargebackApiActivity, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 23, 6)))

def _BuildAutomaton ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton
    del _BuildAutomaton
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 16, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 17, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 18, 6))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 19, 6))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 20, 6))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 21, 6))
    counters.add(cc_5)
    cc_6 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 22, 6))
    counters.add(cc_6)
    cc_7 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 23, 6))
    counters.add(cc_7)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiActivity._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'activityDate')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 16, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiActivity._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'activityType')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 17, 6))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiActivity._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'fromQueue')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 18, 6))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiActivity._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'toQueue')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 19, 6))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiActivity._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'settlementAmount')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 20, 6))
    st_4 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_5, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiActivity._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'settlementCurrencyType')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 21, 6))
    st_5 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_6, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiActivity._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'notes')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 22, 6))
    st_6 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiActivity._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'assignedTo')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 23, 6))
    st_7 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_5, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_5, False) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_6, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_6, False) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_7._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
chargebackApiActivity._Automaton = _BuildAutomaton()




chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'caseId'), pyxb.binding.datatypes.long, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 29, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'merchantId'), pyxb.binding.datatypes.long, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 30, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'dayIssuedByBank'), pyxb.binding.datatypes.date, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 31, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'dateReceivedByVantivCnp'), pyxb.binding.datatypes.date, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 32, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'vantivCnpTxnId'), pyxb.binding.datatypes.long, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 33, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'cycle'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 34, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'orderId'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 35, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'cardNumberLast4'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 36, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'cardType'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 37, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'chargebackAmount'), pyxb.binding.datatypes.long, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 38, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'chargebackCurrencyType'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 39, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'originalTxnDay'), pyxb.binding.datatypes.date, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 40, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'chargebackType'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 41, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'representedAmount'), pyxb.binding.datatypes.long, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 42, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'representedCurrencyType'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 43, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'reasonCode'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 44, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'reasonCodeDescription'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 45, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'currentQueue'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 46, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'fraudNotificationStatus'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 47, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'acquirerReferenceNumber'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 48, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'chargebackReferenceNumber'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 49, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'preArbitrationAmount'), pyxb.binding.datatypes.long, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 50, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'preArbitrationCurrencyType'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 51, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'merchantTxnId'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 52, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'fraudNotificationDate'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 53, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'bin'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 54, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'token'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 55, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'historicalWinPercentage'), pyxb.binding.datatypes.long, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 56, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'customerId'), pyxb.binding.datatypes.string, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 57, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'paymentAmount'), pyxb.binding.datatypes.long, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 58, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'paymentSecondaryAmount'), pyxb.binding.datatypes.long, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 59, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'replyByDay'), pyxb.binding.datatypes.date, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 60, 6)))

chargebackApiCase._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'activity'), chargebackApiActivity, scope=chargebackApiCase, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 61, 6)))

def _BuildAutomaton_ ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_
    del _BuildAutomaton_
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 29, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 30, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 31, 6))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 32, 6))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 33, 6))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 34, 6))
    counters.add(cc_5)
    cc_6 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 35, 6))
    counters.add(cc_6)
    cc_7 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 36, 6))
    counters.add(cc_7)
    cc_8 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 37, 6))
    counters.add(cc_8)
    cc_9 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 38, 6))
    counters.add(cc_9)
    cc_10 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 39, 6))
    counters.add(cc_10)
    cc_11 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 40, 6))
    counters.add(cc_11)
    cc_12 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 41, 6))
    counters.add(cc_12)
    cc_13 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 42, 6))
    counters.add(cc_13)
    cc_14 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 43, 6))
    counters.add(cc_14)
    cc_15 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 44, 6))
    counters.add(cc_15)
    cc_16 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 45, 6))
    counters.add(cc_16)
    cc_17 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 46, 6))
    counters.add(cc_17)
    cc_18 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 47, 6))
    counters.add(cc_18)
    cc_19 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 48, 6))
    counters.add(cc_19)
    cc_20 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 49, 6))
    counters.add(cc_20)
    cc_21 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 50, 6))
    counters.add(cc_21)
    cc_22 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 51, 6))
    counters.add(cc_22)
    cc_23 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 52, 6))
    counters.add(cc_23)
    cc_24 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 53, 6))
    counters.add(cc_24)
    cc_25 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 54, 6))
    counters.add(cc_25)
    cc_26 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 55, 6))
    counters.add(cc_26)
    cc_27 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 56, 6))
    counters.add(cc_27)
    cc_28 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 57, 6))
    counters.add(cc_28)
    cc_29 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 58, 6))
    counters.add(cc_29)
    cc_30 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 59, 6))
    counters.add(cc_30)
    cc_31 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 60, 6))
    counters.add(cc_31)
    cc_32 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 61, 6))
    counters.add(cc_32)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'caseId')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 29, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'merchantId')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 30, 6))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'dayIssuedByBank')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 31, 6))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'dateReceivedByVantivCnp')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 32, 6))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'vantivCnpTxnId')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 33, 6))
    st_4 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_5, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'cycle')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 34, 6))
    st_5 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_6, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'orderId')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 35, 6))
    st_6 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'cardNumberLast4')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 36, 6))
    st_7 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_8, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'cardType')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 37, 6))
    st_8 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_9, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'chargebackAmount')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 38, 6))
    st_9 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_10, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'chargebackCurrencyType')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 39, 6))
    st_10 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_11, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'originalTxnDay')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 40, 6))
    st_11 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_12, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'chargebackType')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 41, 6))
    st_12 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_13, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'representedAmount')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 42, 6))
    st_13 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_14, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'representedCurrencyType')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 43, 6))
    st_14 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_15, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'reasonCode')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 44, 6))
    st_15 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_16, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'reasonCodeDescription')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 45, 6))
    st_16 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_16)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_17, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'currentQueue')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 46, 6))
    st_17 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_17)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_18, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'fraudNotificationStatus')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 47, 6))
    st_18 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_18)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_19, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'acquirerReferenceNumber')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 48, 6))
    st_19 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_19)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_20, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'chargebackReferenceNumber')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 49, 6))
    st_20 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_20)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_21, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'preArbitrationAmount')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 50, 6))
    st_21 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_21)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_22, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'preArbitrationCurrencyType')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 51, 6))
    st_22 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_22)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_23, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'merchantTxnId')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 52, 6))
    st_23 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_23)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_24, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'fraudNotificationDate')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 53, 6))
    st_24 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_24)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_25, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'bin')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 54, 6))
    st_25 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_25)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_26, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'token')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 55, 6))
    st_26 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_26)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_27, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'historicalWinPercentage')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 56, 6))
    st_27 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_27)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_28, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'customerId')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 57, 6))
    st_28 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_28)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_29, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'paymentAmount')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 58, 6))
    st_29 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_29)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_30, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'paymentSecondaryAmount')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 59, 6))
    st_30 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_30)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_31, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'replyByDay')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 60, 6))
    st_31 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_31)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_32, False))
    symbol = pyxb.binding.content.ElementUse(chargebackApiCase._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'activity')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 61, 6))
    st_32 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_32)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_5, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_5, False) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_6, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_6, False) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_7, False) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_8, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_8, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_8, False) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_9, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_9, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_9, False) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_10, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_10, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_10, False) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_11, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_11, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_11, False) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_12, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_12, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_12, False) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_13, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_13, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_13, False) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_14, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_14, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_14, False) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_15, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_15, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_15, False) ]))
    st_15._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_16, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_16, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_16, False) ]))
    st_16._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_17, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_17, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_17, False) ]))
    st_17._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_18, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_18, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_18, False) ]))
    st_18._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_19, True) ]))
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_19, False) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_19, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_19, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_19, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_19, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_19, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_19, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_19, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_19, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_19, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_19, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_19, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_19, False) ]))
    st_19._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_20, True) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_20, False) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_20, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_20, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_20, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_20, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_20, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_20, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_20, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_20, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_20, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_20, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_20, False) ]))
    st_20._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_21, True) ]))
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_21, False) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_21, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_21, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_21, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_21, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_21, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_21, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_21, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_21, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_21, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_21, False) ]))
    st_21._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_22, True) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_22, False) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_22, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_22, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_22, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_22, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_22, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_22, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_22, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_22, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_22, False) ]))
    st_22._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_23, True) ]))
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_23, False) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_23, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_23, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_23, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_23, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_23, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_23, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_23, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_23, False) ]))
    st_23._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_24, [
        fac.UpdateInstruction(cc_24, True) ]))
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_24, False) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_24, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_24, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_24, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_24, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_24, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_24, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_24, False) ]))
    st_24._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_25, [
        fac.UpdateInstruction(cc_25, True) ]))
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_25, False) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_25, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_25, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_25, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_25, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_25, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_25, False) ]))
    st_25._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_26, [
        fac.UpdateInstruction(cc_26, True) ]))
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_26, False) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_26, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_26, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_26, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_26, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_26, False) ]))
    st_26._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_27, [
        fac.UpdateInstruction(cc_27, True) ]))
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_27, False) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_27, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_27, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_27, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_27, False) ]))
    st_27._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_28, [
        fac.UpdateInstruction(cc_28, True) ]))
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_28, False) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_28, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_28, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_28, False) ]))
    st_28._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_29, [
        fac.UpdateInstruction(cc_29, True) ]))
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_29, False) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_29, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_29, False) ]))
    st_29._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_30, [
        fac.UpdateInstruction(cc_30, True) ]))
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_30, False) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_30, False) ]))
    st_30._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_31, [
        fac.UpdateInstruction(cc_31, True) ]))
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_31, False) ]))
    st_31._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_32, [
        fac.UpdateInstruction(cc_32, True) ]))
    st_32._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
chargebackApiCase._Automaton = _BuildAutomaton_()




chargebackRetrievalResponse_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'transactionId'), pyxb.binding.datatypes.long, scope=chargebackRetrievalResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 67, 6)))

chargebackRetrievalResponse_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'chargebackCase'), chargebackApiCase, scope=chargebackRetrievalResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 68, 6)))

def _BuildAutomaton_2 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_2
    del _BuildAutomaton_2
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 67, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 68, 6))
    counters.add(cc_1)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(chargebackRetrievalResponse_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'transactionId')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 67, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(chargebackRetrievalResponse_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'chargebackCase')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 68, 6))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
chargebackRetrievalResponse_._Automaton = _BuildAutomaton_2()




chargebackUpdateRequest_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'activityType'), activityType, scope=chargebackUpdateRequest_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 74, 6)))

chargebackUpdateRequest_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'assignedTo'), STD_ANON, scope=chargebackUpdateRequest_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 75, 6)))

chargebackUpdateRequest_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'note'), STD_ANON_, scope=chargebackUpdateRequest_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 83, 6)))

chargebackUpdateRequest_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'representedAmount'), pyxb.binding.datatypes.long, scope=chargebackUpdateRequest_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 91, 6)))

def _BuildAutomaton_3 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_3
    del _BuildAutomaton_3
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 75, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 83, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 91, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(chargebackUpdateRequest_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'activityType')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 74, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(chargebackUpdateRequest_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'assignedTo')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 75, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(chargebackUpdateRequest_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'note')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 83, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(chargebackUpdateRequest_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'representedAmount')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 91, 6))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
chargebackUpdateRequest_._Automaton = _BuildAutomaton_3()




chargebackUpdateResponse_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'transactionId'), pyxb.binding.datatypes.long, scope=chargebackUpdateResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 97, 6)))

def _BuildAutomaton_4 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_4
    del _BuildAutomaton_4
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 97, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(chargebackUpdateResponse_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'transactionId')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 97, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
chargebackUpdateResponse_._Automaton = _BuildAutomaton_4()




errorResponse_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'errors'), CTD_ANON, scope=errorResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 103, 6)))

def _BuildAutomaton_5 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_5
    del _BuildAutomaton_5
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 103, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(errorResponse_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'errors')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 103, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
errorResponse_._Automaton = _BuildAutomaton_5()




CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'error'), pyxb.binding.datatypes.string, scope=CTD_ANON, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 106, 12)))

def _BuildAutomaton_6 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_6
    del _BuildAutomaton_6
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 106, 12))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'error')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 106, 12))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
CTD_ANON._Automaton = _BuildAutomaton_6()




chargebackDocumentUploadResponse_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'merchantId'), pyxb.binding.datatypes.long, scope=chargebackDocumentUploadResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 126, 6)))

chargebackDocumentUploadResponse_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'caseId'), pyxb.binding.datatypes.long, scope=chargebackDocumentUploadResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 127, 6)))

chargebackDocumentUploadResponse_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'documentId'), pyxb.binding.datatypes.string, scope=chargebackDocumentUploadResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 128, 6)))

chargebackDocumentUploadResponse_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'responseCode'), pyxb.binding.datatypes.string, scope=chargebackDocumentUploadResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 129, 6)))

chargebackDocumentUploadResponse_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'responseMessage'), pyxb.binding.datatypes.string, scope=chargebackDocumentUploadResponse_, location=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 130, 6)))

def _BuildAutomaton_7 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_7
    del _BuildAutomaton_7
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 128, 6))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(chargebackDocumentUploadResponse_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'merchantId')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 126, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(chargebackDocumentUploadResponse_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'caseId')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 127, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(chargebackDocumentUploadResponse_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'documentId')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 128, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(chargebackDocumentUploadResponse_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'responseCode')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 129, 6))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(chargebackDocumentUploadResponse_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'responseMessage')), pyxb.utils.utility.Location('/usr/local/litle-home/hvora/git/python/cnp-chargeback-sdk-python/schema/chargeback-api-v2.1.xsd', 130, 6))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    st_4._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
chargebackDocumentUploadResponse_._Automaton = _BuildAutomaton_7()

