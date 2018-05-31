# coding: utf-8

"""
TODO: add a docstring.
"""


import collections
import csv
import numbers
import numpy as np
import re

class Table(object):

    def __init__(self, *column_names):
        assert all(isinstance(column_name, str) for column_name in column_names)
        self._column_names = list(column_names)
        self._data = [np.array([]) for _ in column_names]
        
    
    @property
    def as_dict(self):
        return {key:value for key, value in zip(self._column_names, self._data)}
    
    @property
    def columns(self):
        return self._column_names 
    
    @property
    def data(self):
        return self._data
    
    @property
    def num_columns(self):
        return len(self._column_names)
    
    
    def __getattr__(self, key):
        return self.as_dict[key]
    
    def __getitem__(self, key):
        return self.__getattr__(key)
    
    def __setitem__(self, key, value):
        assert len(value)==len(self), "Invalid number of elements"
        if key in self.columns:
            self._data[self.columns.index(key)] = value
        else:
            self._column_names.append(key)
            self._data.append(np.array(value))
            
    def __setattr__(self, key, value):
        if key in ['_column_names', '_data']:
            super().__setattr__(key, value)
        else:
            self.__setitem__(key, value)
    
    def __delitem__(self, key):
        del_index = self.columns.index(key)
        del self._column_names[del_index]
        del self._data[del_index]
        
    def __delattr__(self, key):
        if key in ['_column_names', '_data']:
            pass
        else:
            self.__delitem__(key)
    
    def append(self, *new_data):
        assert len(new_data)==len(self.columns), 'Number of new item != number of columns'
        if any(isinstance(x, collections.Iterable) for x in new_data):
            assert all(len(new_data[0])==len(x) for x in new_data), 'Appended item must have the same length'
        for index, new_entry in enumerate(new_data):
            new_entry = np.array(new_entry)
            self._data[index] = np.append(self._data[index], new_entry)
        return self
            
    def delete(self, obj=-1):
        for index in range(self.num_columns):
            self._data[index] = np.delete(self._data[index], obj)
        return self
            
    def sort(self, column_name=None, key=None):
        if not column_name:
            column_name = self.columns[0]
            
        assert column_name in self._column_names, 'Column name not in table'
        index = self._column_names.index(column_name)
        if not key:
            key = lambda x: x[index]
        self._data = list(zip(*sorted(zip(*self._data), key=key)))
        return self
        
    def save(self, filename):
        with open(filename, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(self.columns)
            for row in zip(*self._data):
                writer.writerow(row)
        return self
        
    
    @staticmethod
    def from_string(string):
        string = re.sub(r'\t',' ', string)
        string = re.sub(' +',' ', string)    
        lines = [line for line in string.splitlines() if line]
        new_table = Table(*lines[0].split(' '))
        for line in lines[1:]: 
            new_table.append(*[float(x) for x in line.split(' ')])    
        return new_table

                
    @staticmethod
    def load(filename, delimiter=',', **kwargs):
        with open(filename, mode='r') as csv_file:
            has_header = csv.Sniffer().has_header(csv_file.read(1024))
            csv_file.seek(0)
            reader = csv.reader(csv_file, delimiter=delimiter, **kwargs)
            
            first_line = reader.__next__()
            if has_header:
                new_table = Table(*first_line)
            else:
                new_table = Table(*[chr(index + 97) for index, _ in enumerate(first_line)])
                new_table.append(*[float(r) for r in first_line])
            for row in reader:
                new_table.append(*[float(r) for r in row])
        return new_table
    
    def __len__(self):
        return len(self.data[0])
    
    def __str__(self):
        row_format ="{:<20}" * (self.num_columns)
        _str = row_format.format(*self.columns) + '\n' + '-'*self.num_columns*20
        for row in zip(*self._data):
            _str = _str + '\n' + row_format.format(*row)
        return _str
    