# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: IncomingPushMessageSignal.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='IncomingPushMessageSignal.proto',
  package='relay',
  syntax='proto2',
  serialized_pb=_b('\n\x1fIncomingPushMessageSignal.proto\x12\x05relay\"\xf5\x01\n\x08\x45nvelope\x12\"\n\x04type\x18\x01 \x01(\x0e\x32\x14.relay.Envelope.Type\x12\x0e\n\x06source\x18\x02 \x01(\t\x12\x14\n\x0csourceDevice\x18\x07 \x01(\r\x12\r\n\x05relay\x18\x03 \x01(\t\x12\x11\n\ttimestamp\x18\x05 \x01(\x04\x12\x15\n\rlegacyMessage\x18\x06 \x01(\x0c\x12\x0f\n\x07\x63ontent\x18\x08 \x01(\x0c\"U\n\x04Type\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0e\n\nCIPHERTEXT\x10\x01\x12\x10\n\x0cKEY_EXCHANGE\x10\x02\x12\x11\n\rPREKEY_BUNDLE\x10\x03\x12\x0b\n\x07RECEIPT\x10\x05\"[\n\x07\x43ontent\x12\'\n\x0b\x64\x61taMessage\x18\x01 \x01(\x0b\x32\x12.relay.DataMessage\x12\'\n\x0bsyncMessage\x18\x02 \x01(\x0b\x32\x12.relay.SyncMessage\"\xc9\x01\n\x0b\x44\x61taMessage\x12\x0c\n\x04\x62ody\x18\x01 \x01(\t\x12-\n\x0b\x61ttachments\x18\x02 \x03(\x0b\x32\x18.relay.AttachmentPointer\x12\"\n\x05group\x18\x03 \x01(\x0b\x32\x13.relay.GroupContext\x12\r\n\x05\x66lags\x18\x04 \x01(\r\x12\x13\n\x0b\x65xpireTimer\x18\x05 \x01(\r\"5\n\x05\x46lags\x12\x0f\n\x0b\x45ND_SESSION\x10\x01\x12\x1b\n\x17\x45XPIRATION_TIMER_UPDATE\x10\x02\"\xa7\x05\n\x0bSyncMessage\x12%\n\x04sent\x18\x01 \x01(\x0b\x32\x17.relay.SyncMessage.Sent\x12-\n\x08\x63ontacts\x18\x02 \x01(\x0b\x32\x1b.relay.SyncMessage.Contacts\x12)\n\x06groups\x18\x03 \x01(\x0b\x32\x19.relay.SyncMessage.Groups\x12+\n\x07request\x18\x04 \x01(\x0b\x32\x1a.relay.SyncMessage.Request\x12%\n\x04read\x18\x05 \x03(\x0b\x32\x17.relay.SyncMessage.Read\x12+\n\x07\x62locked\x18\x06 \x01(\x0b\x32\x1a.relay.SyncMessage.Blocked\x1au\n\x04Sent\x12\x13\n\x0b\x64\x65stination\x18\x01 \x01(\t\x12\x11\n\ttimestamp\x18\x02 \x01(\x04\x12#\n\x07message\x18\x03 \x01(\x0b\x32\x12.relay.DataMessage\x12 \n\x18\x65xpirationStartTimestamp\x18\x04 \x01(\x04\x1a\x32\n\x08\x43ontacts\x12&\n\x04\x62lob\x18\x01 \x01(\x0b\x32\x18.relay.AttachmentPointer\x1a\x30\n\x06Groups\x12&\n\x04\x62lob\x18\x01 \x01(\x0b\x32\x18.relay.AttachmentPointer\x1a\x18\n\x07\x42locked\x12\r\n\x05\x61\x64\x64rs\x18\x01 \x03(\t\x1at\n\x07Request\x12-\n\x04type\x18\x01 \x01(\x0e\x32\x1f.relay.SyncMessage.Request.Type\":\n\x04Type\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0c\n\x08\x43ONTACTS\x10\x01\x12\n\n\x06GROUPS\x10\x02\x12\x0b\n\x07\x42LOCKED\x10\x03\x1a)\n\x04Read\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x11\n\ttimestamp\x18\x02 \x01(\x04\"A\n\x11\x41ttachmentPointer\x12\n\n\x02id\x18\x01 \x01(\x06\x12\x13\n\x0b\x63ontentType\x18\x02 \x01(\t\x12\x0b\n\x03key\x18\x03 \x01(\x0c\"\xc3\x01\n\x0cGroupContext\x12\n\n\x02id\x18\x01 \x01(\x0c\x12&\n\x04type\x18\x02 \x01(\x0e\x32\x18.relay.GroupContext.Type\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x0f\n\x07members\x18\x04 \x03(\t\x12(\n\x06\x61vatar\x18\x05 \x01(\x0b\x32\x18.relay.AttachmentPointer\"6\n\x04Type\x12\x0b\n\x07UNKNOWN\x10\x00\x12\n\n\x06UPDATE\x10\x01\x12\x0b\n\x07\x44\x45LIVER\x10\x02\x12\x08\n\x04QUIT\x10\x03\"-\n\x06\x41vatar\x12\x13\n\x0b\x63ontentType\x18\x01 \x01(\t\x12\x0e\n\x06length\x18\x02 \x01(\r\"n\n\x0cGroupDetails\x12\n\n\x02id\x18\x01 \x01(\x0c\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0f\n\x07members\x18\x03 \x03(\t\x12\x1d\n\x06\x61vatar\x18\x04 \x01(\x0b\x32\r.relay.Avatar\x12\x14\n\x06\x61\x63tive\x18\x05 \x01(\x08:\x04true\"Z\n\x0e\x43ontactDetails\x12\x0c\n\x04\x61\x64\x64r\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x1d\n\x06\x61vatar\x18\x03 \x01(\x0b\x32\r.relay.Avatar\x12\r\n\x05\x63olor\x18\x04 \x01(\t')
)



_ENVELOPE_TYPE = _descriptor.EnumDescriptor(
  name='Type',
  full_name='relay.Envelope.Type',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CIPHERTEXT', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='KEY_EXCHANGE', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PREKEY_BUNDLE', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RECEIPT', index=4, number=5,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=203,
  serialized_end=288,
)
_sym_db.RegisterEnumDescriptor(_ENVELOPE_TYPE)

_DATAMESSAGE_FLAGS = _descriptor.EnumDescriptor(
  name='Flags',
  full_name='relay.DataMessage.Flags',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='END_SESSION', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='EXPIRATION_TIMER_UPDATE', index=1, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=532,
  serialized_end=585,
)
_sym_db.RegisterEnumDescriptor(_DATAMESSAGE_FLAGS)

_SYNCMESSAGE_REQUEST_TYPE = _descriptor.EnumDescriptor(
  name='Type',
  full_name='relay.SyncMessage.Request.Type',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CONTACTS', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GROUPS', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BLOCKED', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1166,
  serialized_end=1224,
)
_sym_db.RegisterEnumDescriptor(_SYNCMESSAGE_REQUEST_TYPE)

_GROUPCONTEXT_TYPE = _descriptor.EnumDescriptor(
  name='Type',
  full_name='relay.GroupContext.Type',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='UPDATE', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DELIVER', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='QUIT', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1478,
  serialized_end=1532,
)
_sym_db.RegisterEnumDescriptor(_GROUPCONTEXT_TYPE)


_ENVELOPE = _descriptor.Descriptor(
  name='Envelope',
  full_name='relay.Envelope',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='relay.Envelope.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='source', full_name='relay.Envelope.source', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sourceDevice', full_name='relay.Envelope.sourceDevice', index=2,
      number=7, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='relay', full_name='relay.Envelope.relay', index=3,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='relay.Envelope.timestamp', index=4,
      number=5, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='legacyMessage', full_name='relay.Envelope.legacyMessage', index=5,
      number=6, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='content', full_name='relay.Envelope.content', index=6,
      number=8, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _ENVELOPE_TYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=43,
  serialized_end=288,
)


_CONTENT = _descriptor.Descriptor(
  name='Content',
  full_name='relay.Content',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='dataMessage', full_name='relay.Content.dataMessage', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='syncMessage', full_name='relay.Content.syncMessage', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=290,
  serialized_end=381,
)


_DATAMESSAGE = _descriptor.Descriptor(
  name='DataMessage',
  full_name='relay.DataMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='body', full_name='relay.DataMessage.body', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='attachments', full_name='relay.DataMessage.attachments', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='group', full_name='relay.DataMessage.group', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='flags', full_name='relay.DataMessage.flags', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='expireTimer', full_name='relay.DataMessage.expireTimer', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _DATAMESSAGE_FLAGS,
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=384,
  serialized_end=585,
)


_SYNCMESSAGE_SENT = _descriptor.Descriptor(
  name='Sent',
  full_name='relay.SyncMessage.Sent',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='destination', full_name='relay.SyncMessage.Sent.destination', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='relay.SyncMessage.Sent.timestamp', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='message', full_name='relay.SyncMessage.Sent.message', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='expirationStartTimestamp', full_name='relay.SyncMessage.Sent.expirationStartTimestamp', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=861,
  serialized_end=978,
)

_SYNCMESSAGE_CONTACTS = _descriptor.Descriptor(
  name='Contacts',
  full_name='relay.SyncMessage.Contacts',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='blob', full_name='relay.SyncMessage.Contacts.blob', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=980,
  serialized_end=1030,
)

_SYNCMESSAGE_GROUPS = _descriptor.Descriptor(
  name='Groups',
  full_name='relay.SyncMessage.Groups',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='blob', full_name='relay.SyncMessage.Groups.blob', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1032,
  serialized_end=1080,
)

_SYNCMESSAGE_BLOCKED = _descriptor.Descriptor(
  name='Blocked',
  full_name='relay.SyncMessage.Blocked',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='addrs', full_name='relay.SyncMessage.Blocked.addrs', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1082,
  serialized_end=1106,
)

_SYNCMESSAGE_REQUEST = _descriptor.Descriptor(
  name='Request',
  full_name='relay.SyncMessage.Request',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='relay.SyncMessage.Request.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _SYNCMESSAGE_REQUEST_TYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1108,
  serialized_end=1224,
)

_SYNCMESSAGE_READ = _descriptor.Descriptor(
  name='Read',
  full_name='relay.SyncMessage.Read',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sender', full_name='relay.SyncMessage.Read.sender', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='relay.SyncMessage.Read.timestamp', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1226,
  serialized_end=1267,
)

_SYNCMESSAGE = _descriptor.Descriptor(
  name='SyncMessage',
  full_name='relay.SyncMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sent', full_name='relay.SyncMessage.sent', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='contacts', full_name='relay.SyncMessage.contacts', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='groups', full_name='relay.SyncMessage.groups', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='request', full_name='relay.SyncMessage.request', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='read', full_name='relay.SyncMessage.read', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='blocked', full_name='relay.SyncMessage.blocked', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_SYNCMESSAGE_SENT, _SYNCMESSAGE_CONTACTS, _SYNCMESSAGE_GROUPS, _SYNCMESSAGE_BLOCKED, _SYNCMESSAGE_REQUEST, _SYNCMESSAGE_READ, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=588,
  serialized_end=1267,
)


_ATTACHMENTPOINTER = _descriptor.Descriptor(
  name='AttachmentPointer',
  full_name='relay.AttachmentPointer',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='relay.AttachmentPointer.id', index=0,
      number=1, type=6, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='contentType', full_name='relay.AttachmentPointer.contentType', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='key', full_name='relay.AttachmentPointer.key', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1269,
  serialized_end=1334,
)


_GROUPCONTEXT = _descriptor.Descriptor(
  name='GroupContext',
  full_name='relay.GroupContext',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='relay.GroupContext.id', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='type', full_name='relay.GroupContext.type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='relay.GroupContext.name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='members', full_name='relay.GroupContext.members', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='avatar', full_name='relay.GroupContext.avatar', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _GROUPCONTEXT_TYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1337,
  serialized_end=1532,
)


_AVATAR = _descriptor.Descriptor(
  name='Avatar',
  full_name='relay.Avatar',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='contentType', full_name='relay.Avatar.contentType', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='length', full_name='relay.Avatar.length', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1534,
  serialized_end=1579,
)


_GROUPDETAILS = _descriptor.Descriptor(
  name='GroupDetails',
  full_name='relay.GroupDetails',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='relay.GroupDetails.id', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='relay.GroupDetails.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='members', full_name='relay.GroupDetails.members', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='avatar', full_name='relay.GroupDetails.avatar', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='active', full_name='relay.GroupDetails.active', index=4,
      number=5, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=True,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1581,
  serialized_end=1691,
)


_CONTACTDETAILS = _descriptor.Descriptor(
  name='ContactDetails',
  full_name='relay.ContactDetails',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='addr', full_name='relay.ContactDetails.addr', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='relay.ContactDetails.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='avatar', full_name='relay.ContactDetails.avatar', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='color', full_name='relay.ContactDetails.color', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1693,
  serialized_end=1783,
)

_ENVELOPE.fields_by_name['type'].enum_type = _ENVELOPE_TYPE
_ENVELOPE_TYPE.containing_type = _ENVELOPE
_CONTENT.fields_by_name['dataMessage'].message_type = _DATAMESSAGE
_CONTENT.fields_by_name['syncMessage'].message_type = _SYNCMESSAGE
_DATAMESSAGE.fields_by_name['attachments'].message_type = _ATTACHMENTPOINTER
_DATAMESSAGE.fields_by_name['group'].message_type = _GROUPCONTEXT
_DATAMESSAGE_FLAGS.containing_type = _DATAMESSAGE
_SYNCMESSAGE_SENT.fields_by_name['message'].message_type = _DATAMESSAGE
_SYNCMESSAGE_SENT.containing_type = _SYNCMESSAGE
_SYNCMESSAGE_CONTACTS.fields_by_name['blob'].message_type = _ATTACHMENTPOINTER
_SYNCMESSAGE_CONTACTS.containing_type = _SYNCMESSAGE
_SYNCMESSAGE_GROUPS.fields_by_name['blob'].message_type = _ATTACHMENTPOINTER
_SYNCMESSAGE_GROUPS.containing_type = _SYNCMESSAGE
_SYNCMESSAGE_BLOCKED.containing_type = _SYNCMESSAGE
_SYNCMESSAGE_REQUEST.fields_by_name['type'].enum_type = _SYNCMESSAGE_REQUEST_TYPE
_SYNCMESSAGE_REQUEST.containing_type = _SYNCMESSAGE
_SYNCMESSAGE_REQUEST_TYPE.containing_type = _SYNCMESSAGE_REQUEST
_SYNCMESSAGE_READ.containing_type = _SYNCMESSAGE
_SYNCMESSAGE.fields_by_name['sent'].message_type = _SYNCMESSAGE_SENT
_SYNCMESSAGE.fields_by_name['contacts'].message_type = _SYNCMESSAGE_CONTACTS
_SYNCMESSAGE.fields_by_name['groups'].message_type = _SYNCMESSAGE_GROUPS
_SYNCMESSAGE.fields_by_name['request'].message_type = _SYNCMESSAGE_REQUEST
_SYNCMESSAGE.fields_by_name['read'].message_type = _SYNCMESSAGE_READ
_SYNCMESSAGE.fields_by_name['blocked'].message_type = _SYNCMESSAGE_BLOCKED
_GROUPCONTEXT.fields_by_name['type'].enum_type = _GROUPCONTEXT_TYPE
_GROUPCONTEXT.fields_by_name['avatar'].message_type = _ATTACHMENTPOINTER
_GROUPCONTEXT_TYPE.containing_type = _GROUPCONTEXT
_GROUPDETAILS.fields_by_name['avatar'].message_type = _AVATAR
_CONTACTDETAILS.fields_by_name['avatar'].message_type = _AVATAR
DESCRIPTOR.message_types_by_name['Envelope'] = _ENVELOPE
DESCRIPTOR.message_types_by_name['Content'] = _CONTENT
DESCRIPTOR.message_types_by_name['DataMessage'] = _DATAMESSAGE
DESCRIPTOR.message_types_by_name['SyncMessage'] = _SYNCMESSAGE
DESCRIPTOR.message_types_by_name['AttachmentPointer'] = _ATTACHMENTPOINTER
DESCRIPTOR.message_types_by_name['GroupContext'] = _GROUPCONTEXT
DESCRIPTOR.message_types_by_name['Avatar'] = _AVATAR
DESCRIPTOR.message_types_by_name['GroupDetails'] = _GROUPDETAILS
DESCRIPTOR.message_types_by_name['ContactDetails'] = _CONTACTDETAILS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Envelope = _reflection.GeneratedProtocolMessageType('Envelope', (_message.Message,), dict(
  DESCRIPTOR = _ENVELOPE,
  __module__ = 'IncomingPushMessageSignal_pb2'
  # @@protoc_insertion_point(class_scope:relay.Envelope)
  ))
_sym_db.RegisterMessage(Envelope)

Content = _reflection.GeneratedProtocolMessageType('Content', (_message.Message,), dict(
  DESCRIPTOR = _CONTENT,
  __module__ = 'IncomingPushMessageSignal_pb2'
  # @@protoc_insertion_point(class_scope:relay.Content)
  ))
_sym_db.RegisterMessage(Content)

DataMessage = _reflection.GeneratedProtocolMessageType('DataMessage', (_message.Message,), dict(
  DESCRIPTOR = _DATAMESSAGE,
  __module__ = 'IncomingPushMessageSignal_pb2'
  # @@protoc_insertion_point(class_scope:relay.DataMessage)
  ))
_sym_db.RegisterMessage(DataMessage)

SyncMessage = _reflection.GeneratedProtocolMessageType('SyncMessage', (_message.Message,), dict(

  Sent = _reflection.GeneratedProtocolMessageType('Sent', (_message.Message,), dict(
    DESCRIPTOR = _SYNCMESSAGE_SENT,
    __module__ = 'IncomingPushMessageSignal_pb2'
    # @@protoc_insertion_point(class_scope:relay.SyncMessage.Sent)
    ))
  ,

  Contacts = _reflection.GeneratedProtocolMessageType('Contacts', (_message.Message,), dict(
    DESCRIPTOR = _SYNCMESSAGE_CONTACTS,
    __module__ = 'IncomingPushMessageSignal_pb2'
    # @@protoc_insertion_point(class_scope:relay.SyncMessage.Contacts)
    ))
  ,

  Groups = _reflection.GeneratedProtocolMessageType('Groups', (_message.Message,), dict(
    DESCRIPTOR = _SYNCMESSAGE_GROUPS,
    __module__ = 'IncomingPushMessageSignal_pb2'
    # @@protoc_insertion_point(class_scope:relay.SyncMessage.Groups)
    ))
  ,

  Blocked = _reflection.GeneratedProtocolMessageType('Blocked', (_message.Message,), dict(
    DESCRIPTOR = _SYNCMESSAGE_BLOCKED,
    __module__ = 'IncomingPushMessageSignal_pb2'
    # @@protoc_insertion_point(class_scope:relay.SyncMessage.Blocked)
    ))
  ,

  Request = _reflection.GeneratedProtocolMessageType('Request', (_message.Message,), dict(
    DESCRIPTOR = _SYNCMESSAGE_REQUEST,
    __module__ = 'IncomingPushMessageSignal_pb2'
    # @@protoc_insertion_point(class_scope:relay.SyncMessage.Request)
    ))
  ,

  Read = _reflection.GeneratedProtocolMessageType('Read', (_message.Message,), dict(
    DESCRIPTOR = _SYNCMESSAGE_READ,
    __module__ = 'IncomingPushMessageSignal_pb2'
    # @@protoc_insertion_point(class_scope:relay.SyncMessage.Read)
    ))
  ,
  DESCRIPTOR = _SYNCMESSAGE,
  __module__ = 'IncomingPushMessageSignal_pb2'
  # @@protoc_insertion_point(class_scope:relay.SyncMessage)
  ))
_sym_db.RegisterMessage(SyncMessage)
_sym_db.RegisterMessage(SyncMessage.Sent)
_sym_db.RegisterMessage(SyncMessage.Contacts)
_sym_db.RegisterMessage(SyncMessage.Groups)
_sym_db.RegisterMessage(SyncMessage.Blocked)
_sym_db.RegisterMessage(SyncMessage.Request)
_sym_db.RegisterMessage(SyncMessage.Read)

AttachmentPointer = _reflection.GeneratedProtocolMessageType('AttachmentPointer', (_message.Message,), dict(
  DESCRIPTOR = _ATTACHMENTPOINTER,
  __module__ = 'IncomingPushMessageSignal_pb2'
  # @@protoc_insertion_point(class_scope:relay.AttachmentPointer)
  ))
_sym_db.RegisterMessage(AttachmentPointer)

GroupContext = _reflection.GeneratedProtocolMessageType('GroupContext', (_message.Message,), dict(
  DESCRIPTOR = _GROUPCONTEXT,
  __module__ = 'IncomingPushMessageSignal_pb2'
  # @@protoc_insertion_point(class_scope:relay.GroupContext)
  ))
_sym_db.RegisterMessage(GroupContext)

Avatar = _reflection.GeneratedProtocolMessageType('Avatar', (_message.Message,), dict(
  DESCRIPTOR = _AVATAR,
  __module__ = 'IncomingPushMessageSignal_pb2'
  # @@protoc_insertion_point(class_scope:relay.Avatar)
  ))
_sym_db.RegisterMessage(Avatar)

GroupDetails = _reflection.GeneratedProtocolMessageType('GroupDetails', (_message.Message,), dict(
  DESCRIPTOR = _GROUPDETAILS,
  __module__ = 'IncomingPushMessageSignal_pb2'
  # @@protoc_insertion_point(class_scope:relay.GroupDetails)
  ))
_sym_db.RegisterMessage(GroupDetails)

ContactDetails = _reflection.GeneratedProtocolMessageType('ContactDetails', (_message.Message,), dict(
  DESCRIPTOR = _CONTACTDETAILS,
  __module__ = 'IncomingPushMessageSignal_pb2'
  # @@protoc_insertion_point(class_scope:relay.ContactDetails)
  ))
_sym_db.RegisterMessage(ContactDetails)


# @@protoc_insertion_point(module_scope)
