import re
import logging
from collections import OrderedDict
from FIXFieldsDefinitions import fields_definitions


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


META_FIELDS = fields_definitions.get_meta_fields(4.4)


class FIXField(object):

    FIX_FIELD_REGEX = r"\d+=.*"

    def __init__(self, ID=None, name=None, value=None, message=None):
        self.ID = ID if isinstance(ID, int) else int(ID)
        self.name = name
        self.value = value
        self.message = message
        self.meta_field = self._get_meta_field()

    def set_value(self, value):
        self.value = value

    def link_message(self, message):
        self.message = message

    def _get_meta_field(self):
        if self.ID is not None:
            return META_FIELDS[self.ID]
        else:
            for mf in META_FIELDS:
                if mf.name == self.name:
                    return mf

    def __getattr__(self, name):
        """
        attribtue access like .is_header, .is_trailer will be delegated to self.meta_field.is_header/is_trailer
        """
        return getattr(self.meta_field, name)

    def __repr__(self):
        return f"{self.ID}={self.value}{self.delimeter}"

    __str__ = __repr__


class FIXMessage(object):

    def __init__(self, headers=None, fields=None, trailers=None, delimeter='\x01'):
        self.headers = self._convert_fields(headers)
        self.fields = self._convert_fields(fields)
        self.trailers = self._convert_fields(trailers)
        self.delimeter = delimeter

    def _convert_fields(self, fields):
        if fields is None:
            return OrderedDict()
        elif isinstance(fields, list):
            return OrderedDict([(f.ID, f) for f in fields])
        else:
            return fields

    def add_field(self, field):
        if field.is_header or field.is_trailer:
            raise TypeError(f"[FIXMessage] Fail to add field [{field}], it cannot be a header or trailer. is_header: [{field.is_header}], is_trailer: [{field.is_trailer}]")
        self.fields[field.ID] = field

    def add_header(self, field):
        if not field.is_header:
            raise TypeError(f"[FIXMessage] Fail to add field as header [{field}], it's not constructed as a header. Please check your code")
        self.headers[field.ID] = field

    def add_trailer(self, field):
        if not field.is_trailer:
            raise TypeError(f"[FIXMessage] Fail to add field as trailer [{field}], it's not constructed as a trailer. Please check your code")
        self.trailers[field.ID] = field

    def complete(self):
        """
        Validate body length, checksum, etc
        """
        pass

    def load_string(self, string):
        string = string.strip()
        logger.debug(f"[FIXMessage] Parsing string [{string}] into FIX Message")
        fields = string.split(self.delimeter)
        for f in fields:
            ID, value = f.split('=', 1)
            fix_field = FIXField(ID, value=value, message=self)
            if fix_field.is_header:
                logger.debug(f"[FIXMessage] Adding field [{ID}={value}] as a header")
                self.add_header(fix_field)
            elif fix_field.is_trailer:
                logger.debug(f"[FIXMessage] Adding field [{ID}={value}] as a trailer")
                self.add_trailer(fix_field)
            else:
                logger.debug(f"[FIXMessage] Adding field [{ID}={value}] as a body field")
                self.add_field(fix_field)


if __name__ == "__main__":
    ff = FIXField()
    print(ff.meta_field)
