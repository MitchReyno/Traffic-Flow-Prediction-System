import os
import threading

from PyQt5 import QtCore, QtGui, QtWidgets
from sklearn.preprocessing import MinMaxScaler

from data.scats import ScatsData
from predictor import Predictor
from train import train_with_args
from utility import ConsoleStream, get_setting


SCATS_DATA = ScatsData()

DEFAULT_FONT = QtGui.QFont()
DEFAULT_FONT.setFamily("Arial")
DEFAULT_FONT.setPointSize(10)

LABEL_FONT = QtGui.QFont()
LABEL_FONT.setFamily("Arial")
LABEL_FONT.setPointSize(10)
LABEL_FONT.setBold(True)
LABEL_FONT.setWeight(75)


class UIPredict(object):
    def __init__(self, main):
        self.threads = []
        self.scats_info = {}

        self.model_type = None;

        # Initialises all widgets
        self.main = main
        self.main_widget = QtWidgets.QWidget(main)
        self.predict_push_button = QtWidgets.QPushButton(self.main_widget)
        self.junction_combo_box = QtWidgets.QComboBox(self.main_widget)
        self.junction_label = QtWidgets.QLabel(self.main_widget)
        self.scats_number_combo_box = QtWidgets.QComboBox(self.main_widget)
        self.scats_number_label = QtWidgets.QLabel(self.main_widget)
        self.model_combo_box = QtWidgets.QComboBox(self.main_widget)
        self.model_label = QtWidgets.QLabel(self.main_widget)
        self.date_input = QtWidgets.QDateTimeEdit(self.main_widget)
        self.date_input_label = QtWidgets.QLabel(self.main_widget)
        self.settings_layout = QtWidgets.QFormLayout()
        self.vertical_layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.model_type_layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.model_type_radio_label = QtWidgets.QLabel(self.main_widget)
        self.model_type_radio_generalised = QtWidgets.QRadioButton(self.main_widget)
        self.model_type_radio_junction = QtWidgets.QRadioButton(self.main_widget)
        self.horizontal_line = QtWidgets.QFrame(self.main_widget)
        self.horizontal_line2 = QtWidgets.QFrame(self.main_widget)
        self.date_time_layout = QtWidgets.QFormLayout()
        self.text_output = QtWidgets.QLabel()

        self.main.setObjectName("main_window")
        self.main_widget.setObjectName("main_widget")
        self.vertical_layout.setObjectName("vertical_layout")
        self.settings_layout.setObjectName("settings_layout")
        self.model_label.setObjectName("model_label")
        self.date_input.setObjectName("date_input")
        self.date_input_label.setObjectName("date_input_label")
        self.model_combo_box.setObjectName("model_combo_box")
        self.scats_number_label.setObjectName("scats_number_label")
        self.scats_number_combo_box.setObjectName("scats_number_combo_box")
        self.junction_label.setObjectName("junction_label")
        self.junction_combo_box.setObjectName("junction_combo_box")
        self.predict_push_button.setObjectName("predict_push_button")
        self.horizontal_line.setObjectName("horizontal_line")
        self.horizontal_line2.setObjectName("horizontal_line2")
        self.model_type_layout.setObjectName("model_type_layout")
        self.model_type_radio_label.setObjectName("model_type_radio_label")
        self.model_type_radio_generalised.setObjectName("model_type_radio_generalised")
        self.model_type_radio_junction.setObjectName("model_type_radio_junction")
        self.model_type_radio_generalised.model_type = "Generalised"
        self.model_type_radio_junction.model_type = "Junction"
        self.date_time_layout.setObjectName("date_time_layout")
        self.text_output.setObjectName("text_output")

    def __del__(self):
        for thread in self.threads:
            thread.join()

    def setup(self):
        """ Constructs the form, setting fonts, icons, layouts, etc... """
        self.set_text(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)
        self.init_layouts()
        self.init_widgets()

    def init_layouts(self):
        """ Creates all of the layout and widget nesting """

        # Main window setup
        main_window.setCentralWidget(self.main_widget)
        self.main.resize(1200, 600)
        self.main.setWindowIcon(QtGui.QIcon('images/traffic_jam_64px.png'))

        # Vertical layout setup
        self.vertical_layout.addLayout(self.model_type_layout)
        self.vertical_layout.addWidget(self.horizontal_line)
        self.vertical_layout.addLayout(self.settings_layout)
        self.vertical_layout.addWidget(self.horizontal_line2)
        self.vertical_layout.addLayout(self.date_time_layout)
        self.vertical_layout.addWidget(self.predict_push_button)
        self.vertical_layout.addWidget(self.text_output)

        self.model_type_layout.addWidget(self.model_type_radio_label)
        self.model_type_layout.addWidget(self.model_type_radio_generalised)
        self.model_type_layout.addWidget(self.model_type_radio_junction)

        self.date_time_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.date_input_label)
        self.date_time_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.date_input)

        # Settings layout setup
        self.settings_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.model_label)
        self.settings_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.model_combo_box)
        self.settings_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.scats_number_label)
        self.settings_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.scats_number_combo_box)
        self.settings_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.junction_label)
        self.settings_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.junction_combo_box)

        # Horizontal line setup
        self.horizontal_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.horizontal_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.horizontal_line2.setFrameShape(QtWidgets.QFrame.HLine)
        self.horizontal_line2.setFrameShadow(QtWidgets.QFrame.Sunken)

    def set_text(self, main):
        """ Sets the text for all the controls

        Parameters:
            main  (QMainWindow): the parent object for the interface
        """

        self.model_label.setFont(DEFAULT_FONT)
        self.model_combo_box.setFont(DEFAULT_FONT)
        self.scats_number_label.setFont(DEFAULT_FONT)
        self.scats_number_combo_box.setFont(DEFAULT_FONT)
        self.junction_label.setFont(DEFAULT_FONT)
        self.junction_combo_box.setFont(DEFAULT_FONT)
        self.date_input.setFont(DEFAULT_FONT)
        self.date_input_label.setFont(DEFAULT_FONT)
        self.predict_push_button.setFont(DEFAULT_FONT)
        self.model_type_radio_label.setFont(DEFAULT_FONT)
        self.model_type_radio_generalised.setFont(DEFAULT_FONT)
        self.model_type_radio_junction.setFont(DEFAULT_FONT)
        self.text_output.setFont(DEFAULT_FONT)

        translate = QtCore.QCoreApplication.translate

        main.setWindowTitle(translate("main_window", "TFPS - Predict Junction Traffic"))
        self.model_label.setText(translate("main_window", "Model"))
        self.scats_number_label.setText(translate("main_window", "Scats Number"))
        self.junction_label.setText(translate("main_window", "Junction"))
        self.date_input_label.setText(translate("main_window", "Date/Time"))
        self.predict_push_button.setText(translate("main_window", "Predict"))
        self.model_type_radio_label.setText(translate("main_window", "Model Type"))
        self.model_type_radio_generalised.setText(translate("main_window", "Generalised"))
        self.model_type_radio_junction.setText(translate("main_window", "Individual Junctions"))
        self.text_output.setText(translate("main_window", ""))

    def init_widgets(self):
        """ Sets up the widgets """

        _translate = QtCore.QCoreApplication.translate

        models = ["LSTM", "GRU", "SAEs", "FEEDFWD", "DEEPFEEDFWD"]
        for model in models:
            self.model_combo_box.addItem(model)

        scats_numbers = SCATS_DATA.get_all_scats_numbers()

        self.scats_number_combo_box.addItem("")
        self.junction_combo_box.addItem("")
        for scats in scats_numbers:
            self.scats_number_combo_box.addItem(str(scats))
            self.scats_info[str(scats)] = SCATS_DATA.get_scats_approaches(scats)
            i = 0
            for location in self.scats_info[str(scats)]:
                self.scats_info[str(scats)][i] = SCATS_DATA.get_location_name(scats, location)
                i += 1
        self.junction_combo_box.setEnabled(False)
        self.junction_label.setVisible(False)
        self.junction_combo_box.setVisible(False)
        self.predict_push_button.setEnabled(False)

        # Adds functionality to the controls
        self.predict_push_button.clicked.connect(self.predict)
        self.scats_number_combo_box.currentIndexChanged.connect(self.scats_number_changed)
        self.junction_combo_box.currentIndexChanged.connect(self.junction_number_changed)

        self.model_type_radio_generalised.toggled.connect(lambda:self.model_type_changed(self.model_type_radio_generalised))
        self.model_type_radio_junction.toggled.connect(lambda:self.model_type_changed(self.model_type_radio_junction))

    def model_type_changed(self, radioButton):
        if radioButton.isChecked():
            self.model_type = radioButton.model_type
        self.element_changed()

    def scats_number_changed(self):
        """ Updates the junction combo box when the scats number is changed """
        index = self.scats_number_combo_box.currentIndex()
        value = self.scats_number_combo_box.itemText(index)

        if value == "":
            self.junction_combo_box.setEnabled(False)
            self.junction_label.setVisible(False)
            self.junction_combo_box.setVisible(False)
        else:
            self.junction_combo_box.clear()

            self.junction_combo_box.addItem("")
            for junction in self.scats_info[value]:
                self.junction_combo_box.addItem(str(junction))

            self.junction_combo_box.setEnabled(True)
            self.junction_label.setVisible(True)
            self.junction_combo_box.setVisible(True)
        self.element_changed()

    def junction_number_changed(self):
        self.element_changed()

    def element_changed(self):
        scats_combo_value = self.scats_number_combo_box.itemText(self.scats_number_combo_box.currentIndex())
        junction_combo_value = self.junction_combo_box.itemText(self.junction_combo_box.currentIndex())
        self.predict_push_button.setEnabled(scats_combo_value != "" and junction_combo_value != "" and self.model_type is not None)

    def predict(self):
        scats_number = int(self.scats_number_combo_box.itemText(self.scats_number_combo_box.currentIndex()))
        junction_combo_value = self.junction_combo_box.itemText(self.junction_combo_box.currentIndex())
        network_type = self.model_combo_box.itemText(self.model_combo_box.currentIndex()).lower()
        if self.model_type == "Generalised":
            model_file = f"model/{network_type}/Generalised/Model.h5"
            if os.path.isfile(model_file):
                predictor = Predictor(model_file, network_type)
                junction_id = int(SCATS_DATA.get_location_id(junction_combo_value))
                lat, long = SCATS_DATA.get_positional_data(scats_number, junction_id)
                input = [{
                    "latitude": lat,
                    "longitude": long,
                    "direction": junction_id,
                    "time": self.date_input.dateTime().toString("hh:mm"),
                    "date": self.date_input.dateTime().toString("dd/MM/yyyy")
                }]
                prediction = int(predictor.make_prediction(input)[0][0]*1000)
                self.text_output.setText(f"{prediction} cars predicted")
            else:
                self.text_output.setText("Model file not found")
        elif self.model_type == "Junction":
            junction_id = int(SCATS_DATA.get_location_id(junction_combo_value))
            model_file = f"model/{network_type}/{scats_number}/{junction_id}.h5"
            if os.path.isfile(model_file):
                predictor = Predictor(model_file, network_type)
                prediction = predictor.make_prediction_from_individual(scats_number, junction_id, self.date_input.dateTime().toString("hh:mm"))
                self.text_output.setText(f"{prediction} cars predicted")
            else:
                self.text_output.setText("Model file not found")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = UIPredict(main_window)
    ui.setup()
    main_window.show()
    sys.exit(app.exec_())
