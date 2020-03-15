from collections import OrderedDict
from FIXFieldsDefinitions import fields_definitions


meta_fields = fields_definitions.get_meta_fields(4.4)


class FIXField(object):

    def __init__(self, ID=None, name=None, value=None, message=None):
        self.ID = ID
        self.name = name
        self.value = value
        self.message = message
        self.meta_field = self.get_meta_field()

    def resolve_reference(self):
        self.name = sel

    def set_value(self, value):
        self.value = value

    def link_message(self, message):
        self.message = message

    def get_meta_field(self):
        if self.ID is not None:
            return meta_fields[ID]
        else:
            for mf in meta_fields:
                if mf.name == self.name:
                    return mf

    def __getattr__(self, name):
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
            return OrderedDict
        elif isinstance(fields, list):
            return OrderedDict([(f.ID, f) for f in fields])
        else:
            return fields

    def add_field(self, field):
        if field.is_header or field.is_trailer:
            raise TypeError(f"[FIXMessage] Fail to add field [{field}], it cannot be a header or trailer. is_header: [{field.is_header}], is_trailer: [{field.is_trailer}]")
        self.fields.append(field)

    def add_header(self, header):
        if not field.is_header:
            raise TypeError(f"[FIXMessage] Fail to add field as header [{header}], it's not constructed as a header. Please check your code")
        self.headers.append(header)

    def add_trailer(self, trailer):
        if not trailer.is_trailer:
            raise TypeError(f"[FIXMessage] Fail to add field as trailer [{trailer}], it's not constructed as a trailer. Please check your code")
        self.trailers.append(trailer)


if __name__ == "__main__":
    ff = FIXField()
    print(ff.meta_field)
