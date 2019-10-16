import json
from PyQt5 import QtCore

settings: {}
# Loads the settings into a dictionary
with open('config.json', 'r') as f:
    settings = json.load(f)


def get_setting(key):
    """ Gets a setting value

    Parameters:
        key  (String): the specific setting
    """
    return settings[key]

def is_int(val):
    if type(val) == int:
        return True
    else:
        if val.is_integer():
            return True
        else:
            return False


class ConsoleStream(QtCore.QObject):
    """ Handles the system-specific functions for stdout """
    text_output = QtCore.pyqtSignal(str)

    def write(self, text):
        """ Writes to the EditText control

        Parameters:
            text  (String): text from the console output
        """
        self.text_output.emit(str(text))

    def flush(self):
        """ Does nothing, here so the compiler doesn't complain """
        pass
