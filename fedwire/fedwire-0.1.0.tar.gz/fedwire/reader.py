# https://github.com/Bubbassauro/FedwireMessage/blob/master/FieldFormats/Wire.cs
# https://github.com/rawamba/FedWireParser/blob/master/FedWireParser/WireBO.cs


















# import collections
# import contextlib
# import datetime
# import itertools

# import bryl

# class Reader(bryl.LineReader):
#     error_types = (Malformed, Record.field_type.error_type)

#     record_types = dict(
#         (record_cls.record_type.value, record_cls)
#         for record_cls in [
#             FileHeader,
#             CompanyBatchHeader,
#             EntryDetail,
#             EntryDetailAddendum,
#             CompanyBatchControl,
#             FileControl,
#         ]
#     )

#     def filter(self, *record_types):
#         for record in self:
#             if any(
#                    isinstance(record, record_type)
#                    for record_type in record_types
#                 ):
#                 yield record

#     # bryl.LineReader

#     record_type = Record

#     @staticmethod
#     def as_record_type(reader, data, offset):
#         record_type = reader.record_type.load(data).record_type
#         if record_type in reader.record_types:
#             return reader.record_types[record_type]
#         raise reader.malformed(
#             offset, 'unexpected record_type {0}'.format(record_type),
#         )

#     # structured

#     def file_header(self):
#         return self.next_record(FileHeader)

#     def company_batches(self):
#         while True:
#             header = self.next_record(CompanyBatchHeader, None)
#             if not header:
#                 break
#             yield header

#     def entries(self):
#         while True:
#             detail = self.entry_detail()
#             if not detail:
#                 break
#             addenda = self.entry_addenda()
#             yield Entry(detail=detail, addenda=addenda)

#     def entry_detail(self, default=None):
#         return self.next_record(EntryDetail, default)

#     def entry_addenda(self, default=None):
#         addenda = []
#         while True:
#             record = self.next_record(EntryDetailAddendum, None)
#             if not record:
#                 break
#             addenda.append(record)
#         return addenda

#     def company_batch_control(self):
#         return self.next_record(CompanyBatchControl)

#     def file_control(self):
#         return self.next_record(FileControl)
