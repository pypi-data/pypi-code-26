# Copyright 2018 Smithsonian Astrophysical Observatory
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import itertools
import logging
import uuid
import warnings

import numpy
from astropy.io import votable
from astropy.table import QTable
from lxml import etree

from rama.framework import BaseType, InstanceId, Attribute, Reference, Composition, SingleReferenceWrapper, \
    RowReferenceWrapper
from rama.reader import Document, Reader
from rama.utils import ADAPTER_PROPERTY_NAME

LOG = logging.getLogger(__name__)


class Votable(Document):
    def __init__(self, xml):
        super().__init__(xml)
        # TBD Maybe I should remove TABLEDATA to reduce the size of the tree. TABLEDATA will be parsed by astropy.
        parser = etree.XMLParser(ns_clean=True)
        tree = etree.parse(xml, parser)
        self.document = tree.getroot()

    def find_instances(self, element_class, context):
        return find_instances(self, element_class, context)


def get_local_name(tag_name):
    return f"*[local-name() = '{tag_name}']"


TEMPLATES = get_local_name("TEMPLATES")
INSTANCE = get_local_name("INSTANCE")
LITERAL = get_local_name("LITERAL")
COLUMN = get_local_name("COLUMN")
REFERENCE = get_local_name("REFERENCE")
COMPOSITION = get_local_name("COMPOSITION")
ATTRIBUTE = get_local_name("ATTRIBUTE")
TABLE = get_local_name("TABLE")
FIELD = get_local_name("FIELD")
PRIMARYKEY = get_local_name("PRIMARYKEY")
FOREIGNKEY = get_local_name("FOREIGNKEY")
PKFIELD = get_local_name("PKFIELD")
IDREF = get_local_name("IDREF")
TARGETID = get_local_name("TARGETID")
ID = "ID"
REF_ATTR = "@ref"
ID_ATTR = f"@{ID}"
NAME_ATTR = "@name"
VALUE_ATTR = "@value"
TYPE_ATTR = "@dmtype"
ROLE_ATTR = "@dmrole"
UNIT_ATTR = "@unit"


def find_instances(votable: Votable, element_class: BaseType, context: Reader):
    return [read_instance(element, context) for element in find(votable, element_class)]


def find(votable: Votable, element_class: BaseType):
    type_id = [element_class.vodml_id, ]
    subtype_ids = [subtype.vodml_id for subtype in element_class.all_subclasses()]
    all_ids = type_id + subtype_ids
    elements = [find_instance_elements(votable.document, id) for id in all_ids]
    elements_flat = list(itertools.chain(*elements))
    return elements_flat


def find_instance_elements(xml_document, vodml_id):
    return xml_document.xpath(get_instance_element_by_id(vodml_id))


def get_instance_element_by_id(vodml_id):
    return get_type_xpath_expression("INSTANCE", vodml_id)


def read_instance(xml_element, context):
    type_id = resolve_type(xml_element)
    element_class = context.get_type_by_id(type_id)
    return make(element_class, xml_element, context)


def parse_column(context, xml_element):
    column_ref = xml_element.xpath(REF_ATTR)[0]
    find_column_xpath = f"//{FIELD}[{ID_ATTR}='{column_ref}']"
    column_elements = xml_element.xpath(find_column_xpath)
    if not column_elements:
        msg = f"Can't find column with ID {column_ref}. Setting values to NaN"
        LOG.warning(msg)
        warnings.warn(msg, SyntaxWarning)
        return numpy.NaN

    column_element = column_elements[0]
    table = parse_table(context, column_element)

    column_ref = context.get_column_mapping(column_ref)
    column = table[column_ref]

    # Another hack: it simplify things if the byte columns are converted to strings... maybe this is an issue
    # in the VOTable parser needing some attention?
    try:
        if column.dtype == 'object':
            column = column.astype('U')
            table[column_ref] = column
    except:
        pass

    name = column_element.xpath(NAME_ATTR)[0]
    column.name = name

    # Kind of a hack, but I couldn't find a better way.
    # For instances with primary keys which use the same column(s) as a different attribute, in some but not all
    # cases changing the column names makes it impossible for the second pass to find the same column implementing a
    # different attribute (for instance, in test5, the same column is used for the primary key and for Source.name)
    # Whether or not this happens seems to depend on what class the column is (e.g. Quantity vs MappedColumn).
    try:
        column = table[column_ref]
    except KeyError:
        context.add_column_mapping(column_ref, name)
    return column


def parse_table(context, column_element):
    table_elements = column_element.xpath(f"parent::{TABLE}")
    if not table_elements:
        raise RuntimeError("COLUMN points to FIELD that does not have a TABLE parent")
    table_element = table_elements[0]
    table_index = int(table_element.xpath(f"count(preceding-sibling::{TABLE})"))

    table_ids = table_element.xpath(ID_ATTR)
    if table_ids:
        no_id = False
        table_id = table_ids[0]
        table = context.get_table_by_id(table_id)
        if table is not None:
            return table
    else:
        no_id = True
        table_id = f"_GENERATED_ID_{table_index}"

    table = QTable(votable.parse_single_table(context.file, table_number=table_index).to_table())

    if no_id:
        table_id = id(table)
        table_element.attrib[ID] = str(table_id)  # We set the attribute so we have an handle if we parse it again

    context.add_table(table_id, table)

    return table


def parse_literal(context, xml_element):
    value = xml_element.xpath(VALUE_ATTR)[0]
    value_type = xml_element.xpath(TYPE_ATTR)[0]
    units = xml_element.xpath(UNIT_ATTR)
    unit = units[0] if units else None
    return context.get_type_by_id(value_type)(value, unit)


def parse_id(context, xml_element, instance_class):
    keys = None
    primary_key_elements = xml_element.xpath(f"./{PRIMARYKEY}")
    if primary_key_elements:
        keys = parse_identifier_field(context, primary_key_elements[0])
    ids = xml_element.xpath(ID_ATTR)
    if not ids:
        # Randomly generate an ID for each instance that doesn't have any.
        id = f"{instance_class.vodml_id}-{str(uuid.uuid4())}"
    else:
        id = ids[0]

    return InstanceId(id, keys)


def parse_identifier_field(context, xml_element):
    pk_fields = xml_element.xpath(f"./{PKFIELD}")
    keys_array = numpy.array([parse_primary_key_field(context, pk_field) for pk_field in pk_fields]).T
    return keys_array


def parse_primary_key_field(context, xml_element):
    literal_elements = xml_element.xpath(f"./{LITERAL}")
    if literal_elements:
        return parse_literal(context, literal_elements[0])
    column_elements = xml_element.xpath(f"./{COLUMN}")
    if column_elements:
        return parse_column(context, column_elements[0]).data


def get_type_xpath_expression(tag_name, type_id):
    tag_selector = get_local_name(tag_name)
    return f"//{tag_selector}[{TYPE_ATTR}='{type_id}']"


def get_role_xpath_expression(tag_name, role_id):
    return f".//{tag_name}[{ROLE_ATTR}='{role_id}']"


def get_local_name(tag_name):
    return f"*[local-name() = '{tag_name}']"


def get_child_selector(tag_name):
    return f"child::{tag_name}"


def get_children(element, child_tag_name):
    return element.xpath(get_child_selector(child_tag_name))


def resolve_type(xml_element):
    element_type = xml_element.xpath(TYPE_ATTR)[0]
    return element_type


def find_element_for_role(xml_element, tag_name, role_id):
    elements = xml_element.xpath(get_role_xpath_expression(tag_name, role_id))
    n_elements = len(elements)

    if n_elements > 1:
        warnings.warn(SyntaxWarning, f"Too many elements with dmrole = {role_id}")

    if n_elements:
        return elements[0]

    return None


def is_template(xml_element):
    has_template_parent = len(xml_element.xpath(f'./parent::{TEMPLATES}')) > 0
    has_column_descendants = len(xml_element.xpath(f'.//{COLUMN}')) > 0
    return has_template_parent or has_column_descendants


def decorate_with_adapter(instance_info):
    decorated_instance = instance_info.instance
    if hasattr(instance_info.instance_class, ADAPTER_PROPERTY_NAME):
        vo_instance = instance_info.instance
        adapter = getattr(instance_info.instance_class, ADAPTER_PROPERTY_NAME)
        decorated_instance = adapter(vo_instance)
        decorated_instance.__vo_object__ = vo_instance
    decorated_instance.__vo_id__ = instance_info.instance_id
    return decorated_instance


def attach_fields(instance_info):
    field_readers = {
        Attribute: parse_attributes,
        Reference: parse_references,
        Composition: parse_composed_instances
    }
    fields = instance_info.instance_class.find_fields()
    for field_name, field_object in fields:
        field_reader = field_readers[field_object.__class__]
        field_instance = field_reader(instance_info.xml_element, field_object, instance_info.context)
        instance_info.instance.set_field(field_name, field_instance)
    return instance_info


def parse_attributes(xml_element, field_object, context):
    xml_element = find_element_for_role(xml_element, ATTRIBUTE, field_object.vodml_id)
    if xml_element is not None:
        values = parse_structured_instances(xml_element, context) +\
                 parse_literals(xml_element, context) +\
                 parse_columns(xml_element, context)
        return field_object.select_return_value(values)


def parse_composed_instances(xml_element, field_object, context):
    xml_element = find_element_for_role(xml_element, COMPOSITION, field_object.vodml_id)
    if xml_element is not None:
        values = parse_structured_instances(xml_element, context)
        return field_object.select_return_value(values)


def parse_references(xml_element, field_object, context):
    # In the votable 1.4 schema there is a choice among IDREF, FOREIGNKEY, and REMOREREFERENCE (currently
    # unsupported). In invalid cases where multiple elements are given, we give precedence to IDREF.

    xml_element = find_element_for_role(xml_element, REFERENCE, field_object.vodml_id)
    if xml_element is not None:
        idref_instances = parse_idref_instances(xml_element, context)
        if idref_instances:
            return field_object.select_return_value(idref_instances)

        foreign_key_instances = parse_foreign_key_instances(xml_element, context)
        if foreign_key_instances:
            return field_object.select_return_value(foreign_key_instances)


def parse_structured_instances(xml_element, context):
    elements = get_children(xml_element, INSTANCE)
    return [read_instance(element, context) for element in elements]


def parse_literals(xml_element, context):
    elements = get_children(xml_element, LITERAL)
    return [parse_literal(context, element) for element in elements]


def parse_columns(xml_element, context):
    elements = get_children(xml_element, COLUMN)
    return [parse_column(context, element) for element in elements]


def parse_idref_instances(xml_element, context):
    elements = get_children(xml_element, IDREF)
    return [parse_idref(element, context) for element in elements]


def parse_foreign_key_instances(xml_element, context):
    elements = get_children(xml_element, FOREIGNKEY)
    return [parse_foreign_key(element, context) for element in elements]


def parse_idref(xml_element, context):
    ref = InstanceId(xml_element.text, None)

    referred_elements = xml_element.xpath(f"//{INSTANCE}[{ID_ATTR}='{ref.id}']")

    if not referred_elements:
        # TODO make a single call?
        msg = f"Dangling reference {ref}"
        warnings.warn(msg, SyntaxWarning)
        LOG.warning(msg)
        return None

    referred_element = referred_elements[0]
    return SingleReferenceWrapper(read_instance(referred_element, context))


def parse_foreign_key(xml_element, context):
    ref = InstanceId(None, parse_identifier_field(context, xml_element))

    target_id = xml_element.xpath(f"./{TARGETID}")[0].text
    referred_elements = xml_element.xpath(f"//*[{ID_ATTR}='{target_id}']/{INSTANCE}")

    instances = [read_instance(referred_element, context)
                 for referred_element in referred_elements]
    instances_index = {tuple(instance.__vo_id__.keys): instance for instance in instances}
    references = [instances_index.get(tuple(key), None) for key in ref.keys]
    return RowReferenceWrapper(references)


def make(instance_class, xml_element, context):
    instance_id = parse_id(context, xml_element, instance_class)
    instance = context.get_instance_by_id(instance_id)
    if instance is not None:
        return instance
    else:
        instance = instance_class()
        instance.is_template = is_template(xml_element)
        instance_info = InstanceInfo(instance, instance_id, instance_class, xml_element, context)
        instance_info = attach_fields(instance_info)
        decorated_instance = decorate_with_adapter(instance_info)
        context.add_instance(decorated_instance)
        return decorated_instance


class InstanceInfo:
    def __init__(self, instance, instance_id, instance_class, xml_element, context):
        self.context = context
        self.xml_element = xml_element
        self.instance_class = instance_class
        self.instance_id = instance_id
        self.instance = instance
