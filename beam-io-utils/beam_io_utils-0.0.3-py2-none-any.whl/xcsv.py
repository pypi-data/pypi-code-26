import csv

from apache_beam import PTransform # pylint: disable=no-name-in-module
from apache_beam.coders.coders import StrUtf8Coder
from apache_beam.io import filesystem, filebasedsource, filebasedsink, Write


# TODO: This is only being used in this file... but it seems like a useful util in general.
# It would be good to be able to use it somewhere else...
# NOTE: This needs to be tested with multiple input types.
class FileHandleToIterator(object):

  def __init__(self, file_handle):
    self.file_handle = file_handle

  def __iter__(self):
    return self

  def next(self):
    line = self.file_handle.readline()
    if line == None or line == "":
      raise StopIteration
    return line


class CSVFileBasedSource(filebasedsource.FileBasedSource):

  def __init__(self,
               file_pattern,
               min_bundle_size=0,
               compression_type=filesystem.CompressionTypes.AUTO,
               splittable=True,
               validate=True,
               fieldnames=None,
               restkey=None,
               restval=None,
               dialect='excel'):

    self.fieldnames = fieldnames
    self.restkey = restkey
    self.restval = restval
    self.dialect = dialect

    super(self.__class__, self).__init__(
        file_pattern,
        min_bundle_size=0,
        compression_type=filesystem.CompressionTypes.AUTO,
        splittable=True,
        validate=True)

  def read_records(self, file_name, offset_range_tracker):
    file_handle = self.open_file(file_name)
    iterator = FileHandleToIterator(file_handle)

    reader = csv.DictReader(
        iterator,
        fieldnames=self.fieldnames,
        restkey=self.restkey,
        restval=self.restval,
        dialect=self.dialect)

    return reader


class CSVFileSink(filebasedsink.FileBasedSink):

  def __init__(self,
               fieldnames,
               file_path_prefix,
               file_name_suffix=".csv",
               num_shards=1,
               shard_name_template=None,
               coder=StrUtf8Coder(),
               compression_type=filesystem.CompressionTypes.AUTO,
               restval="",
               extrasaction="raise",
               dialect="excel",
               include_header=True):

    super(self.__class__, self).__init__(
        file_path_prefix=file_path_prefix,
        file_name_suffix=file_name_suffix,
        num_shards=num_shards,
        shard_name_template=shard_name_template,
        coder=coder,
        compression_type=compression_type)

    self.cache = dict()

    self.fieldnames = fieldnames
    self.restval = restval
    self.extrasaction = extrasaction
    self.dialect = dialect
    self.include_header = include_header

  def open(self, temp_path):
    file_handle = super(self.__class__, self).open(temp_path)
    writer = csv.DictWriter(
        file_handle,
        fieldnames=self.fieldnames,
        restval=self.restval,
        extrasaction=self.extrasaction,
        dialect=self.dialect)

    if self.include_header is True:
      writer.writeheader()

    self.cache[file_handle] = writer

    return file_handle

  def write_record(self, file_handle, element):
    writer = self.cache[file_handle]
    writer.writerow(element)

  def close(self, file_handle):
    file_handle.close()


class WriteToCSV(PTransform):

  def __init__(self,
               fieldnames,
               file_path_prefix,
               file_name_suffix=".csv",
               num_shards=1,
               shard_name_template=None,
               coder=StrUtf8Coder(),
               compression_type=filesystem.CompressionTypes.AUTO,
               restval="",
               extrasaction="raise",
               dialect="excel",
               include_header=True):

    self.sink = CSVFileSink(
        fieldnames=fieldnames,
        file_path_prefix=file_path_prefix,
        file_name_suffix=file_name_suffix,
        num_shards=num_shards,
        shard_name_template=shard_name_template,
        coder=coder,
        compression_type=compression_type,
        restval=restval,
        extrasaction=extrasaction,
        dialect=dialect,
        include_header=include_header)

  def expand(self, collection):
    return collection | Write(self.sink)
