from PyQt5 import QtCore, QtGui, QtWidgets
from data.data import read_data, check_data_exists
from data.scats import ScatsDB

class UiTrain(object):
    def __init__(self):
        self.scats_info = {}


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
                self.junctionComboBox.addItem(str(junction))

            self.junctionComboBox.setEnabled(True)


    def init_widgets(self):
        _translate = QtCore.QCoreApplication.translate
        if check_data_exists():
            self.statusLabel.setText(_translate("mainWindow",
                                                "<html><head/><body><p><span style=\" color:#00FF00;\">Yes</span></p></body></html>"))
            self.loadPushButton.setEnabled(False)
        else:
            self.trainPushButton.setEnabled(False)

        self.scatsNumberComboBox.currentIndexChanged.connect(self.scats_number_changed)

        self.scatsNumberComboBox.addItem("All")
        self.junctionComboBox.addItem("All")
        self.junctionComboBox.setEnabled(False)

        models = ['LSTM', 'GRU', 'SAEs']
        for model in models:
            self.modelComboBox.addItem(model)

        with ScatsDB() as s:
            scats_numbers = s.get_all_scats_numbers()

            for scats in scats_numbers:
                self.scatsNumberComboBox.addItem(str(scats))
                self.scats_info[str(scats)] = s.get_scats_approaches(scats)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = UiTrain()
    ui.setup(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())

