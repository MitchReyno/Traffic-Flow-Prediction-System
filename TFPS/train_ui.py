import threading

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from data.data import read_data, check_data_exists, resolve_location_id
from train import train_with_args
from data.scats import ScatsDB
from utility import ConsoleStream


def load():
    QApplication.setOverrideCursor(Qt.WaitCursor)
    read_data("data/Scats Data October 2006.xls")
    QApplication.restoreOverrideCursor()


class UiTrain(object):
    def __init__(self):
        self.scats_info = {}
        sys.stdout = ConsoleStream(text_output=self.display_output)


    def __del__(self):
        sys.stdout = sys.__stdout__


    def multithreaded_output(self):
        self.thread = threading.Thread(target=self.train)
        self.thread.start()


    def display_output(self, text):
        cursor = self.outputTextEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.outputTextEdit.setTextCursor(cursor)
        self.outputTextEdit.ensureCursorVisible()


    def setup(self, main):
        main.setObjectName("mainWindow")
        main.resize(600, 300)
        self.mainWidget = QtWidgets.QWidget(main)
        self.mainWidget.setObjectName("mainWidget")
        main.setWindowIcon(QtGui.QIcon('images/traffic_jam_64px.png'))
        self.verticalLayout = QtWidgets.QVBoxLayout(self.mainWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scatsDataLayout = QtWidgets.QHBoxLayout()
        self.scatsDataLayout.setObjectName("scatsDataLayout")
        self.scatsDataLabel = QtWidgets.QLabel(self.mainWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.scatsDataLabel.setFont(font)
        self.scatsDataLabel.setObjectName("scatsDataLabel")
        self.scatsDataLayout.addWidget(self.scatsDataLabel)
        self.statusLabel = QtWidgets.QLabel(self.mainWidget)
        self.statusLabel.setFont(font)
        self.statusLabel.setObjectName("statusLabel")
        self.scatsDataLayout.addWidget(self.statusLabel)
        self.loadPushButton = QtWidgets.QPushButton(self.mainWidget)
        self.loadPushButton.setFont(font)
        self.loadPushButton.setObjectName("loadPushButton")
        self.scatsDataLayout.addWidget(self.loadPushButton)
        self.verticalLayout.addLayout(self.scatsDataLayout)
        self.settingsLayout = QtWidgets.QFormLayout()
        self.settingsLayout.setFormAlignment(QtCore.Qt.AlignCenter)
        self.settingsLayout.setObjectName("settingsLayout")
        self.modelLabel = QtWidgets.QLabel(self.mainWidget)
        self.modelLabel.setFont(font)
        self.modelLabel.setObjectName("modelLabel")
        self.settingsLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.modelLabel)
        self.modelComboBox = QtWidgets.QComboBox(self.mainWidget)
        self.modelComboBox.setFont(font)
        self.modelComboBox.setObjectName("modelComboBox")
        self.settingsLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.modelComboBox)
        self.scatsNumberLabel = QtWidgets.QLabel(self.mainWidget)
        self.scatsNumberLabel.setFont(font)
        self.scatsNumberLabel.setObjectName("scatsNumberLabel")
        self.settingsLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.scatsNumberLabel)
        self.scatsNumberComboBox = QtWidgets.QComboBox(self.mainWidget)
        self.scatsNumberComboBox.setFont(font)
        self.scatsNumberComboBox.setObjectName("scatsNumberComboBox")
        self.settingsLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.scatsNumberComboBox)
        self.junctionLabel = QtWidgets.QLabel(self.mainWidget)
        self.junctionLabel.setFont(font)
        self.junctionLabel.setObjectName("junctionLabel")
        self.settingsLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.junctionLabel)
        self.junctionComboBox = QtWidgets.QComboBox(self.mainWidget)
        self.junctionComboBox.setFont(font)
        self.junctionComboBox.setObjectName("junctionComboBox")
        self.settingsLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.junctionComboBox)
        self.verticalLayout.addLayout(self.settingsLayout)
        self.trainPushButton = QtWidgets.QPushButton(self.mainWidget)
        self.trainPushButton.setFont(font)
        self.trainPushButton.setObjectName("trainPushButton")
        self.verticalLayout.addWidget(self.trainPushButton)
        self.verticalLayout.addWidget(self.trainPushButton)
        self.horizontalLine = QtWidgets.QFrame(self.mainWidget)
        self.horizontalLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.horizontalLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.horizontalLine.setObjectName("horizontalLine")
        self.verticalLayout.addWidget(self.horizontalLine)
        self.outputTextEdit = QtWidgets.QPlainTextEdit(self.mainWidget)
        self.outputTextEdit.setReadOnly(True)
        self.outputTextEdit.setObjectName("outputTextEdit")
        font.setPointSize(10)
        self.outputTextEdit.setFont(font)
        self.verticalLayout.addWidget(self.outputTextEdit)
        mainWindow.setCentralWidget(self.mainWidget)

        self.translate(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

        self.init_widgets()

    def translate(self, main):
        _translate = QtCore.QCoreApplication.translate
        main.setWindowTitle(_translate("mainWindow", "TFPS - Train Model"))
        self.scatsDataLabel.setText(_translate("mainWindow", "Scats Data October 2006 Loaded:"))
        self.statusLabel.setText(_translate("mainWindow", "<html><head/><body><p><span style=\" color:#ff0000;\">No</span></p></body></html>"))
        self.loadPushButton.setText(_translate("mainWindow", "Load"))
        self.modelLabel.setText(_translate("mainWindow", "Model"))
        self.scatsNumberLabel.setText(_translate("mainWindow", "Scats Number"))
        self.junctionLabel.setText(_translate("mainWindow", "Junction"))
        self.trainPushButton.setText(_translate("mainWindow", "Train"))


    def scats_number_changed(self):
        index = self.scatsNumberComboBox.currentIndex()
        value = self.scatsNumberComboBox.itemText(index)

        if value == "All" or value == "":
            self.junctionComboBox.setCurrentIndex(0)
            self.junctionComboBox.setEnabled(False)
        else:
            self.junctionComboBox.clear()
            self.junctionComboBox.addItem("All")

            for junction in self.scats_info[value]:
                self.junctionComboBox.addItem(junction)

            self.junctionComboBox.setEnabled(True)

    def train(self):
        scats_number = self.scatsNumberComboBox.itemText(self.scatsNumberComboBox.currentIndex()).lower()
        junction = resolve_location_id(self.junctionComboBox.itemText(self.junctionComboBox.currentIndex()))
        model = self.modelComboBox.itemText(self.modelComboBox.currentIndex()).lower()

        train_with_args(scats_number, junction, model)


    def init_widgets(self):
        _translate = QtCore.QCoreApplication.translate
        if check_data_exists():
            self.statusLabel.setText(_translate("mainWindow",
                                                "<html><head/><body><p><span style=\" color:#00FF00;\">Yes</span></p></body></html>"))
            self.loadPushButton.setEnabled(False)
            self.scatsNumberComboBox.addItem("All")
            self.junctionComboBox.addItem("All")
        else:
            self.trainPushButton.setEnabled(False)
            self.scatsNumberComboBox.setEnabled(False)
            self.scatsNumberComboBox.addItem("None")
            self.junctionComboBox.addItem("None")

        self.junctionComboBox.setEnabled(False)

        self.scatsNumberComboBox.currentIndexChanged.connect(self.scats_number_changed)

        models = ['LSTM', 'GRU', 'SAEs']
        for model in models:
            self.modelComboBox.addItem(model)

        with ScatsDB() as s:
            scats_numbers = s.get_all_scats_numbers()

            for scats in scats_numbers:
                self.scatsNumberComboBox.addItem(str(scats))

                locations = []
                for junction in s.get_scats_approaches(scats):
                    location_name = s.get_location_name(scats, junction)
                    locations.append(location_name)

                self.scats_info[str(scats)] = locations

        self.loadPushButton.clicked.connect(load)
        self.trainPushButton.clicked.connect(self.multithreaded_output)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("QPlainTextEdit {background-color: black; color:limegreen}")
    mainWindow = QtWidgets.QMainWindow()
    ui = UiTrain()
    ui.setup(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())

