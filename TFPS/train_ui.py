import threading

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from data.data import read_data, check_data_exists, get_location_id
from train import train_with_args
from data.scats import ScatsDB
from utility import ConsoleStream, get_setting


class UiTrain(object):
    """ The user interface for the training part of the program """
    def __init__(self, main):
        # Sets up a thread for the train function so the GUI won't be blocked from updating
        self.thread = threading.Thread(target=self.train)

        self.scats_info = {}

        # Initialises all widgets
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
        self.epochs_value_label = QtWidgets.QLabel(self.main_widget)
        self.epochs_label = QtWidgets.QLabel(self.main_widget)
        self.epoch_label_layout = QtWidgets.QVBoxLayout()
        self.batches_value_label = QtWidgets.QLabel(self.main_widget)
        self.batches_label = QtWidgets.QLabel(self.main_widget)
        self.batch_label_layout = QtWidgets.QVBoxLayout()
        self.lag_value_label = QtWidgets.QLabel(self.main_widget)
        self.lag_label = QtWidgets.QLabel(self.main_widget)
        self.lag_label_layout = QtWidgets.QVBoxLayout()
        self.training_settings_layout = QtWidgets.QHBoxLayout()

        # Makes the console output to the EditText control
        sys.stdout = ConsoleStream(text_output=self.display_output)

    def __del__(self):
        # Reset console output if the interface is closed
        sys.stdout = sys.__stdout__


    def load(self):
        """ Loads the excel data into the program """
        # Let the user know the program is loading
        QApplication.setOverrideCursor(Qt.WaitCursor)
        read_data("data/Scats Data October 2006.xls")

        # Re-initialise the widgets now that data has been loaded
        self.junction_combo_box.clear()
        self.scats_number_combo_box.clear()
        self.model_combo_box.clear()
        self.init_widgets()

        # Restore the cursor so that the user knows that they can interact with the program again
        QApplication.restoreOverrideCursor()


    def display_output(self, text):
        """ Adds text to the output control

        Parameters:
            text  (String): text from the console output
        """
        cursor = self.output_text_edit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.output_text_edit.setTextCursor(cursor)
        self.output_text_edit.ensureCursorVisible()


    def setup(self):
        """ Constructs the form, setting fonts, icons, layouts, etc... """
        default_font = QtGui.QFont()
        default_font.setFamily("Arial")
        default_font.setPointSize(10)

        label_font = QtGui.QFont()
        label_font.setFamily("Arial")
        label_font.setPointSize(10)
        label_font.setBold(True)
        label_font.setWeight(75)

        self.main.setObjectName("main_window")
        self.main.resize(600, 300)
        self.main_widget.setObjectName("main_widget")
        self.main.setWindowIcon(QtGui.QIcon('images/traffic_jam_64px.png'))
        self.vertical_layout.setObjectName("vertical_layout")
        self.scats_data_layout.setObjectName("scats_data_layout")
        self.scats_data_label.setFont(default_font)
        self.scats_data_label.setObjectName("scats_data_label")
        self.scats_data_layout.addWidget(self.scats_data_label)
        self.status_label.setFont(default_font)
        self.status_label.setObjectName("status_label")
        self.scats_data_layout.addWidget(self.status_label)
        self.load_push_button.setFont(default_font)
        self.load_push_button.setObjectName("load_push_button")
        self.scats_data_layout.addWidget(self.load_push_button)
        self.vertical_layout.addLayout(self.scats_data_layout)
        self.settings_layout.setFormAlignment(QtCore.Qt.AlignCenter)
        self.settings_layout.setObjectName("settings_layout")
        self.model_label.setFont(default_font)
        self.model_label.setObjectName("model_label")
        self.settings_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.model_label)
        self.model_combo_box.setFont(default_font)
        self.model_combo_box.setObjectName("model_combo_box")
        self.settings_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.model_combo_box)
        self.scats_number_label.setFont(default_font)
        self.scats_number_label.setObjectName("scats_number_label")
        self.settings_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.scats_number_label)
        self.scats_number_combo_box.setFont(default_font)
        self.scats_number_combo_box.setObjectName("scats_number_combo_box")
        self.settings_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.scats_number_combo_box)
        self.junction_label.setFont(default_font)
        self.junction_label.setObjectName("junction_label")
        self.settings_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.junction_label)
        self.junction_combo_box.setFont(default_font)
        self.junction_combo_box.setObjectName("junction_combo_box")
        self.settings_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.junction_combo_box)
        self.vertical_layout.addLayout(self.settings_layout)
        self.training_settings_layout.setObjectName("training_settings_layout")
        self.lag_label_layout.setObjectName("lag_label_layout")
        self.lag_label.setAlignment(QtCore.Qt.AlignCenter)
        self.lag_label.setObjectName("lag_label")
        self.lag_label.setFont(label_font)
        self.lag_label_layout.addWidget(self.lag_label)
        self.lag_value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.lag_value_label.setObjectName("lag_value_label")
        self.lag_label_layout.addWidget(self.lag_value_label)
        self.training_settings_layout.addLayout(self.lag_label_layout)
        self.batch_label_layout.setObjectName("batch_label_layout")
        self.batches_label.setFont(label_font)
        self.batches_label.setAlignment(QtCore.Qt.AlignCenter)
        self.batches_label.setObjectName("batches_label")
        self.batch_label_layout.addWidget(self.batches_label)
        self.batches_value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.batches_value_label.setObjectName("batches_value_label")
        self.batch_label_layout.addWidget(self.batches_value_label)
        self.training_settings_layout.addLayout(self.batch_label_layout)
        self.epoch_label_layout.setObjectName("epoch_label_layout")
        self.epochs_label.setAlignment(QtCore.Qt.AlignCenter)
        self.epochs_label.setObjectName("epochs_label")
        self.epochs_label.setFont(label_font)
        self.epoch_label_layout.addWidget(self.epochs_label)
        self.epochs_value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.epochs_value_label.setObjectName("epochs_value_label")
        self.epoch_label_layout.addWidget(self.epochs_value_label)
        self.training_settings_layout.addLayout(self.epoch_label_layout)
        self.vertical_layout.addLayout(self.training_settings_layout)
        self.train_push_button.setFont(default_font)
        self.train_push_button.setObjectName("train_push_button")
        self.vertical_layout.addWidget(self.train_push_button)
        self.vertical_layout.addWidget(self.train_push_button)
        self.horizontal_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.horizontal_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.horizontal_line.setObjectName("horizontal_line")
        self.vertical_layout.addWidget(self.horizontal_line)
        self.output_text_edit.setReadOnly(True)
        self.output_text_edit.setObjectName("output_text_edit")

        default_font.setPointSize(8)
        default_font.setFamily("Consolas")

        self.output_text_edit.setFont(default_font)
        self.vertical_layout.addWidget(self.output_text_edit)
        main_window.setCentralWidget(self.main_widget)

        self.set_text(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

        self.init_widgets()


    def set_text(self, main):
        """ Sets the text for all the controls

        Parameters:
            main  (QMainWindow): the parent object for the interface
        """
        translate = QtCore.QCoreApplication.translate
        config = get_setting("train")

        main.setWindowTitle(translate("main_window", "TFPS - Train Model"))
        self.scats_data_label.setText(translate("main_window", "Scats Data October 2006 Loaded:"))
        self.status_label.setText(
            translate("main_window",
                       "<html><head/><body><p><span style=\" color:#ff0000;\">No</span></p></body></html>"))
        self.load_push_button.setText(translate("main_window", "Load"))
        self.model_label.setText(translate("main_window", "Model"))
        self.scats_number_label.setText(translate("main_window", "Scats Number"))
        self.junction_label.setText(translate("main_window", "Junction"))
        self.lag_label.setText(translate("mainWindow", "Lag"))
        self.lag_value_label.setText(translate("mainWindow", str(config["lag"])))
        self.batches_label.setText(translate("mainWindow", "Batches"))
        self.batches_value_label.setText(translate("mainWindow", str(config["batch"])))
        self.epochs_label.setText(translate("mainWindow", "Epochs"))
        self.epochs_value_label.setText(translate("mainWindow", str(config["epochs"])))
        self.train_push_button.setText(translate("main_window", "Train"))


    def scats_number_changed(self):
        """ Updates the junction combo box when the scats number is changed """
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
        """ Passes the training parameters to the program """
        scats_number = self.scats_number_combo_box.itemText(self.scats_number_combo_box.currentIndex()).lower()
        junction = get_location_id(self.junction_combo_box.itemText(self.junction_combo_box.currentIndex()))
        model = self.model_combo_box.itemText(self.model_combo_box.currentIndex()).lower()

        train_with_args(scats_number, junction, model)


    def init_widgets(self):
        """ Sets up the widgets depending on certain conditions """
        _translate = QtCore.QCoreApplication.translate

        # Checks to see if there is already a database with the VicRoads data
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

        # Adds functionality to the buttons
        self.load_push_button.clicked.connect(self.load)
        self.train_push_button.clicked.connect(self.thread.start)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = UiTrain(main_window)
    ui.setup()
    main_window.show()
    sys.exit(app.exec_())
