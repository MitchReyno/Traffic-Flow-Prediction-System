import json
from PyQt5 import QtCore

settings: {}
with open('config.json', 'r') as f:
    settings = json.load(f)


def get_setting(key):
    return settings[key]


class ConsoleStream(QtCore.QObject):
    text_output = QtCore.pyqtSignal(str)

    def write(self, text):
        self.text_output.emit(str(text))

    def flush(self):
        pass
