import reprlib
import logging
from copy import deepcopy
from collections import abc, OrderedDict, defaultdict
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class FIXFieldsDefinitions(object):

    ALLOWED_VERSIONS = ('common', 4.2, 4.3, 4.4)

    def __init__(self):
        self._data = {}

    def read_yaml(self, path):
        with open(path, 'r') as fd:
            stream = fd.read()
            self.data = load(stream, Loader=Loader)
            self.meta_fields = self.parse_data()

    def parse_data(self):
        meta_fields = defaultdict(OrderedDict)
        data = deepcopy(self._data)
        data_common = data.pop('common', {})

        for vers, vers_data in data.items():
            if vers not in self.ALLOWED_VERSIONS:
                logging.error(f"[ParseData] Fail to parse data [{reprlib.repr(self._data)}], invalid version string key [{vers}], only [{self.ALLOWED_VERSIONS}] are allowed, skipping this entry")
                continue

            """
            Merge common and version specific
            """
            final_vers_data = deepcopy(data_common)
            for f_id, f_data in vers_data.items():
                if f_id in final_vers_data:
                    final_vers_data[f_id].update(f_data)
                else:
                    final_vers_data[f_id] = f_data

            """
            Construct MetaFIXField from merged dict
            """
            for f_id in sorted(final_vers_data.keys()):
                f_data = final_vers_data[f_id]

                ID = f_id
                name = f_data.get('name')
                version = f_data.get('version', vers)
                values = f_data.get('values', None)
                regex = f_data.get('regex', None)
                is_header = f_data.get('is_header', False)
                is_trailer = f_data.get('is_trailer', False)

                meta_fields[vers][f_id] = MetaFIXField(f_id, name, version, values, regex, is_header, is_trailer)

        return meta_fields

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, abc.Mapping):
            raise TypeError(f"[LoadData] Failed to laod data [{reprlib.repr(self._data)}], expecting a Mapping class instance (e.g. dict) but received [{type(value)}]")
        self._data = value

    def get_meta_fields(self, version):
        return self.meta_fields[version]


class MetaFIXField(object):

    """
    This class only serves a field definition object representation, it's not the proper class for a specific field in a specific message
    """

    def __init__(self, ID, name, version=None, values=None, regex=None, is_header=False, is_trailer=False):
        self.ID = ID
        self.name = name
        self.version = version
        self.values = values
        self.regex = regex
        self.is_header = is_header
        self.is_trailer = is_trailer

    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, value):
        if not isinstance(value, int):
            raise TypeError(f"[SingleField] Fail to set/construct single field ID, expecting int class instance but received [{value}] of type [{type(value)}]")
        self._ID = value


class FIXFieldValue(object):

    def __init__(self, meta_fix_field, value, description):
        self.meta_fix_field = meta_fix_field
        self.value = value
        self.description = description


fields_definitions = FIXFieldsDefinitions()
fields_definitions.read_yaml('/home/ec2-user/FIXEngine/FIXFieldsDefinitions.yaml')
