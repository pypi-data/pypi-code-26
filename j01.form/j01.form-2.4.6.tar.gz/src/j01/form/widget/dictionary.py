###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Dictionary widget
$Id: dictionary.py 4891 2018-06-05 12:32:20Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface

import z3c.form.widget
import z3c.form.converter
import z3c.form.browser.widget
import z3c.form.browser.textarea

from j01.form import interfaces
from j01.form.layer import IFormLayer
from j01.form.widget.widget import WidgetMixin


class DictKeyValueWidget(WidgetMixin, z3c.form.browser.textarea.TextAreaWidget):
    """Input type text widget implementation for dict with key/value values."""

    zope.interface.implementsOnly(interfaces.IDictKeyValueWidget)

    klass = u'dictionary-control form-control'
    css = u'dictionary'
    value = u''

    label = None

    def update(self):
        super(DictKeyValueWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


# converter
class DictKeyValueConverter(z3c.form.converter.BaseDataConverter):
    """Data converter for IDictKeyValueWidget."""

    zope.component.adapts(
        zope.schema.interfaces.IDict, interfaces.IDictKeyValueWidget)

    def toWidgetValue(self, value):
        """Convert from text lines to HTML representation."""
        # if the value is the missing value, then an empty list is produced.
        if value is self.field.missing_value:
            return u''
        elif value is None:
            # in case we use missing_value = {}
            return u''
        res = u''
        for k, v in value.items():
            res += u'%s:%s\n' % (k, v)
        return res

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        if not len(value):
            return self.field.missing_value

        # find key type
        keyType = self.field.key_type._type
        if keyType is None:
            keyType = unicode
        if isinstance(keyType, tuple):
            keyType = keyType[0]

        # find value type
        valueType = self.field.value_type._type
        if isinstance(valueType, tuple):
            valueType = valueType[0]

        mapping = {}
        for entry in value.splitlines():
            if not entry:
                # ignore leading and ending empty linebreaks
                continue
            k, v = entry.split(':')
            mapping[keyType(k.strip())] = valueType(v.strip())
        return mapping


def getDictKeyValueWidget(field, request):
    """IFieldWidget factory for DictKeyValueWidget."""

    return z3c.form.widget.FieldWidget(field, DictKeyValueWidget(request))


################################################################################
#
# proxy widget

class ProxyWidget(DictKeyValueWidget):
    """Proxy protocol:url widget with support for ":" in url:port"""

    zope.interface.implements(interfaces.IProxyWidget)


# converter
class ProxyWidgetConverter(DictKeyValueConverter):
    """Data converter for IProxyWidget"""

    zope.component.adapts(zope.schema.interfaces.IDict, interfaces.IProxyWidget)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        if not len(value):
            return self.field.missing_value

        # find key type
        keyType = self.field.key_type._type
        if keyType is None:
            keyType = unicode
        if isinstance(keyType, tuple):
            keyType = keyType[0]

        # find value type
        valueType = self.field.value_type._type
        if isinstance(valueType, tuple):
            valueType = valueType[0]

        mapping = {}
        for entry in value.splitlines():
            if not entry:
                # ignore leading and ending empty linebreaks
                continue
            parts = entry.split(':')
            if len(parts) == 2:
                k, v = parts
            elif len(parts) > 2:
                k = parts[0]
                v = ':'.join(parts[1:])
            else:
                # parts < 2, that's a bad value (missing : separator)
                return mapping
            mapping[keyType(k.strip())] = valueType(v.strip())
        return mapping


def getProxyWidget(field, request):
    """IFieldWidget factory for ProxyWidget."""
    return z3c.form.widget.FieldWidget(field, ProxyWidget(request))
