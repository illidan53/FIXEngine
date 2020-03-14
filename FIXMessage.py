import logging
from collections import OrderedDict
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class FIXField(object):

    """
    This class only serves a field definition object representation, it's not the proper class for a specific field in a specific message
    """

    def __init__(self, ID, name, allowed_values=None, regex=None, is_header=False, is_trailer=False):
        self.ID = ID
        self.name = name
        self.allowed_values = allowed_values
        self.regex = regex
        self.is_header = is_header
        self.is_trailer = is_trailer


class FIXFieldsDefinition(object):

    def __init__(self):
        self.data = None

    def read_yaml(self, path, version=None):
        with open(path, 'r') as fd:
            stream = fd.read()
            self.data = load(stream, Loader=Loader)


class FIXMessage(object):

    def __init__(self, line, delimeter='\x01'):
        self.line = line
        self.delimeter = delimeter
        self.data_dict = self.load_line(line)

    def load_line(self, line):
        ret = OrderedDict()
