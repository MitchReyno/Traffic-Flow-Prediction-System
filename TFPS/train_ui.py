import threading

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from data.data import read_data, check_data_exists, resolve_location_id
from train import train_with_args
from data.scats import ScatsDB
from utility import ConsoleStream


class UiTrain(object):
    def __init__(self, main):
        self.thread = threading.Thread(target=self.train)

        self.main = main
        self.main_widget = QtWidgets.QWidget(main)
        self.output_text_edit = QtWidgets.QPlainTextEdit(self.main_widget)
        self.horizontal_line = QtWidgets.QFrame(self.main_widget)
        self.train_push_button = QtWidgets.QPushButton(self.main_widget)
        self.junction_combo_box = QtWidgets.QComboBox(self.main_widget)
        self.junction_label = QtWidgets.QLabel(self.main_widget)
        self.scats_number_combo_box = QtWidgets.QComboBox(self.main_widget)
        self.scats_number_label = QtWidgets.QLabel(self.main_widget)
        self.model_combo_box = QtWidgets.QComboBox(self.main_widget)
        self.model_label = QtWidgets.QLabel(self.main_widget)
        self.settings_layout = QtWidgets.QFormLayout()
        self.load_push_button = QtWidgets.QPushButton(self.main_widget)
        self.status_label = QtWidgets.QLabel(self.main_widget)
        self.scats_data_label = QtWidgets.QLabel(self.main_widget)
        self.scats_data_layout = QtWidgets.QHBoxLayout()
        self.vertical_layout = QtWidgets.QVBoxLayout(self.main_widget)

        self.scats_info = {}

        sys.stdout = ConsoleStream(text_output=self.display_output)


    def __del__(self):
        sys.stdout = sys.__stdout__


    def load(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        read_data("data/Scats Data October 2006.xls")
        self.junction_combo_box.clear()
        self.scats_number_combo_box.clear()
        self.model_combo_box.clear()
        self.init_widgets()
        QApplication.restoreOverrideCursor()


    def display_output(self, text):
        cursor = self.output_text_edit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.output_text_edit.setTextCursor(cursor)
        self.output_text_edit.ensureCursorVisible()

    def setup(self):
        font = QtGui.QFont()
        font.setPointSize(12)
        self.main.setObjectName("main_window")
        self.main.resize(600, 300)
        self.main_widget.setObjectName("main_widget")
        self.main.setWindowIcon(QtGui.QIcon('images/traffic_jam_64px.png'))
        self.vertical_layout.setObjectName("vertical_layout")
        self.scats_data_layout.setObjectName("scats_data_layout")
        self.scats_data_label.setFont(font)
        self.scats_data_label.setObjectName("scats_data_label")
        self.scats_data_layout.addWidget(self.scats_data_label)
        self.status_label.setFont(font)
        self.status_label.setObjectName("status_label")
        self.scats_data_layout.addWidget(self.status_label)
        self.load_push_button.setFont(font)
        self.load_push_button.setObjectName("load_push_button")
        self.scats_data_layout.addWidget(self.load_push_button)
        self.vertical_layout.addLayout(self.scats_data_layout)
        self.settings_layout.setFormAlignment(QtCore.Qt.AlignCenter)
        self.settings_layout.setObjectName("settings_layout")
        self.model_label.setFont(font)
        self.model_label.setObjectName("model_label")
        self.settings_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.model_label)
        self.model_combo_box.setFont(font)
        self.model_combo_box.setObjectName("model_combo_box")
        self.settings_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.model_combo_box)
        self.scats_number_label.setFont(font)
        self.scats_number_label.setObjectName("scats_number_label")
        self.settings_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.scats_number_label)
        self.scats_number_combo_box.setFont(font)
        self.scats_number_combo_box.setObjectName("scats_number_combo_box")
        self.settings_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.scats_number_combo_box)
        self.junction_label.setFont(font)
        self.junction_label.setObjectName("junction_label")
        self.settings_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.junction_label)
        self.junction_combo_box.setFont(font)
        self.junction_combo_box.setObjectName("junction_combo_box")
        self.settings_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.junction_combo_box)
        self.vertical_layout.addLayout(self.settings_layout)
        self.train_push_button.setFont(font)
        self.train_push_button.setObjectName("train_push_button")
        self.vertical_layout.addWidget(self.train_push_button)
        self.vertical_layout.addWidget(self.train_push_button)
        self.horizontal_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.horizontal_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.horizontal_line.setObjectName("horizontal_line")
        self.vertical_layout.addWidget(self.horizontal_line)
        self.output_text_edit.setReadOnly(True)
        self.output_text_edit.setObjectName("output_text_edit")
        font.setPointSize(10)
        self.output_text_edit.setFont(font)
        self.vertical_layout.addWidget(self.output_text_edit)
        main_window.setCentralWidget(self.main_widget)

        self.translate(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

        self.init_widgets()

    def translate(self, main):
        _translate = QtCore.QCoreApplication.translate
        main.setWindowTitle(_translate("main_window", "TFPS - Train Model"))
        self.scats_data_label.setText(_translate("main_window", "Scats Data October 2006 Loaded:"))
        self.status_label.setText(
            _translate("main_window",
                       "<html><head/><body><p><span style=\" color:#ff0000;\">No</span></p></body></html>"))
        self.load_push_button.setText(_translate("main_window", "Load"))
        self.model_label.setText(_translate("main_window", "Model"))
        self.scats_number_label.setText(_translate("main_window", "Scats Number"))
        self.junction_label.setText(_translate("main_window", "Junction"))
        self.train_push_button.setText(_translate("main_window", "Train"))

    def scats_number_changed(self):
        index = self.scats_number_combo_box.currentIndex()
        value = self.scats_number_combo_box.itemText(index)

        if value == "All" or value == "":
            self.junction_combo_box.setCurrentIndex(0)
            self.junction_combo_box.setEnabled(False)
        else:
            self.junction_combo_box.clear()

            self.junction_combo_box.addItem("All")
            for junction in self.scats_info[value]:
                self.junction_combo_box.addItem(junction)

            self.junction_combo_box.setEnabled(True)

    def train(self):
        scats_number = self.scats_number_combo_box.itemText(self.scats_number_combo_box.currentIndex()).lower()
        junction = resolve_location_id(self.junction_combo_box.itemText(self.junction_combo_box.currentIndex()))
        model = self.model_combo_box.itemText(self.model_combo_box.currentIndex()).lower()

        train_with_args(scats_number, junction, model)

    def init_widgets(self):
        _translate = QtCore.QCoreApplication.translate

        if check_data_exists():
            self.status_label.setText(_translate("main_window",
                                                 "<html><head/><body><p><span style=\" color:#00FF00;\">Yes</span></p>"
                                                 "</body></html>"))
            self.load_push_button.setEnabled(False)
            self.scats_number_combo_box.addItem("All")
            self.junction_combo_box.addItem("All")
            self.scats_number_combo_box.setEnabled(True)
            self.train_push_button.setEnabled(True)
        else:
            self.train_push_button.setEnabled(False)
            self.scats_number_combo_box.setEnabled(False)
            self.scats_number_combo_box.addItem("None")
            self.junction_combo_box.addItem("None")

        self.junction_combo_box.setEnabled(False)

        self.scats_number_combo_box.currentIndexChanged.connect(self.scats_number_changed)

        models = ['LSTM', 'GRU', 'SAEs']
        for model in models:
            self.model_combo_box.addItem(model)

        with ScatsDB() as s:
            scats_numbers = s.get_all_scats_numbers()

            for scats in scats_numbers:
                self.scats_number_combo_box.addItem(str(scats))

                locations = []
                for junction in s.get_scats_approaches(scats):
                    location_name = s.get_location_name(scats, junction)
                    locations.append(location_name)

                self.scats_info[str(scats)] = locations

        self.load_push_button.clicked.connect(self.load)
        self.train_push_button.clicked.connect(self.thread.start)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("QPlainTextEdit {background-color: black; color:limegreen}")
    main_window = QtWidgets.QMainWindow()
    ui = UiTrain(main_window)
    ui.setup()
    main_window.show()
    sys.exit(app.exec_())
