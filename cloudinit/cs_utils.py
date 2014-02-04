import json
import platform

import serial

SERIAL_PORT = '/dev/ttyS1'
if platform.system() == 'Windows':
    SERIAL_PORT = 'COM2'


class Cepko(object):
    request_pattern = "<\n{}\n>"

    def get(self, key="", request_pattern=None):
        if request_pattern is None:
            request_pattern = self.request_pattern
        return CepkoResult(request_pattern.format(key))

    def all(self):
        return self.get()

    def meta(self, key=""):
        request_pattern = self.request_pattern.format("/meta/{}")
        return self.get(key, request_pattern)

    def global_context(self, key=""):
        request_pattern = self.request_pattern.format("/global_context/{}")
        return self.get(key, request_pattern)


class CepkoResult(object):
    def __init__(self, request):
        self.request = request
        self.raw_result = self._execute()
        self.result = self._marshal(self.raw_result)

    def _execute(self):
        connection = serial.Serial(SERIAL_PORT)
        connection.write(self.request)
        return connection.readline().strip('\x04\n')

    def _marshal(self, input):
        try:
            return json.loads(input)
        except ValueError:
            return input

    def __len__(self):
        return self.result.__len__()

    def __getitem__(self, key):
        return self.result.__getitem__(key)

    def __contains__(self, item):
        return self.result.__contains__(item)

    def __iter__(self):
        return self.result.__iter__()
