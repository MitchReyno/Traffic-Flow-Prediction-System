import threading

from PyQt5 import QtCore, QtGui, QtWidgets

from data.scats import ScatsData
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

OUTPUT_FONT = QtGui.QFont()
OUTPUT_FONT.setPointSize(8)
OUTPUT_FONT.setFamily("Consolas")


class UiTrain(object):
    """ The user interface for the training part of the program """
    def __init__(self, main):
        self.threads = []
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
        self.continue_train_checkbox = QtWidgets.QCheckBox(self.main_widget)

        self.main.setObjectName("main_window")
        self.main_widget.setObjectName("main_widget")
        self.vertical_layout.setObjectName("vertical_layout")
        self.settings_layout.setObjectName("settings_layout")
        self.model_label.setObjectName("model_label")
        self.model_combo_box.setObjectName("model_combo_box")
        self.scats_number_label.setObjectName("scats_number_label")
        self.scats_number_combo_box.setObjectName("scats_number_combo_box")
        self.junction_label.setObjectName("junction_label")
        self.junction_combo_box.setObjectName("junction_combo_box")
        self.training_settings_layout.setObjectName("training_settings_layout")
        self.lag_label_layout.setObjectName("lag_label_layout")
        self.lag_label.setObjectName("lag_label")
        self.lag_value_label.setObjectName("lag_value_label")
        self.batch_label_layout.setObjectName("batch_label_layout")
        self.batches_label.setObjectName("batches_label")
        self.batches_value_label.setObjectName("batches_value_label")
        self.epoch_label_layout.setObjectName("epoch_label_layout")
        self.epochs_label.setObjectName("epochs_label")
        self.epochs_value_label.setObjectName("epochs_value_label")
        self.train_push_button.setObjectName("train_push_button")
        self.continue_train_checkbox.setObjectName("continue_train_checkbox")
        self.horizontal_line.setObjectName("horizontal_line")
        self.output_text_edit.setObjectName("output_text_edit")

        # Makes the console output to the EditText control
        sys.stdout = ConsoleStream(text_output=self.display_output)

    def __del__(self):
        # Reset console output if the interface is closed
        sys.stdout = sys.__stdout__

        for thread in self.threads:
            thread.join()

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
        self.vertical_layout.addLayout(self.settings_layout)
        self.vertical_layout.addLayout(self.training_settings_layout)
        self.vertical_layout.addWidget(self.train_push_button)
        self.vertical_layout.addWidget(self.continue_train_checkbox)
        self.vertical_layout.addWidget(self.horizontal_line)
        self.vertical_layout.addWidget(self.output_text_edit)

        # Settings layout setup
        self.settings_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.model_label)
        self.settings_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.model_combo_box)
        self.settings_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.scats_number_label)
        self.settings_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.scats_number_combo_box)
        self.settings_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.junction_label)
        self.settings_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.junction_combo_box)

        # Training settings layout setup
        self.training_settings_layout.addLayout(self.lag_label_layout)
        self.lag_label_layout.addWidget(self.lag_label)
        self.lag_label_layout.addWidget(self.lag_value_label)
        self.training_settings_layout.addLayout(self.batch_label_layout)
        self.batch_label_layout.addWidget(self.batches_label)
        self.batch_label_layout.addWidget(self.batches_value_label)
        self.training_settings_layout.addLayout(self.epoch_label_layout)
        self.epoch_label_layout.addWidget(self.epochs_label)
        self.epoch_label_layout.addWidget(self.epochs_value_label)

        # Horizontal line setup
        self.horizontal_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.horizontal_line.setFrameShadow(QtWidgets.QFrame.Sunken)

        # Output text setup
        self.output_text_edit.setReadOnly(True)

        # Settings layout alignment
        self.settings_layout.setFormAlignment(QtCore.Qt.AlignCenter)
        self.lag_label.setAlignment(QtCore.Qt.AlignCenter)
        self.lag_value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.batches_label.setAlignment(QtCore.Qt.AlignCenter)
        self.batches_value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.epochs_label.setAlignment(QtCore.Qt.AlignCenter)
        self.epochs_value_label.setAlignment(QtCore.Qt.AlignCenter)

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
        self.lag_label.setFont(LABEL_FONT)
        self.batches_label.setFont(LABEL_FONT)
        self.epochs_label.setFont(LABEL_FONT)
        self.train_push_button.setFont(DEFAULT_FONT)
        self.continue_train_checkbox.setFont(DEFAULT_FONT)
        self.output_text_edit.setFont(OUTPUT_FONT)

        translate = QtCore.QCoreApplication.translate
        config = get_setting("train")

        main.setWindowTitle(translate("main_window", "TFPS - Train Model"))
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
        self.continue_train_checkbox.setText("Continue Training")

    def init_widgets(self):
        """ Sets up the widgets """

        _translate = QtCore.QCoreApplication.translate

        models = ["LSTM", "GRU", "SAEs", "FEEDFWD", "DEEPFEEDFWD"]
        for model in models:
            self.model_combo_box.addItem(model)

        scats_numbers = SCATS_DATA.get_all_scats_numbers()

        self.scats_number_combo_box.addItem("All")
        self.junction_combo_box.addItem("All")
        for scats in scats_numbers:
            self.scats_number_combo_box.addItem(str(scats))
            self.scats_info[str(scats)] = SCATS_DATA.get_scats_approaches(scats)
            i = 0
            for location in self.scats_info[str(scats)]:
                self.scats_info[str(scats)][i] = SCATS_DATA.get_location_name(scats, location)
                i += 1
        self.junction_combo_box.setEnabled(False)

        # Adds functionality to the controls
        self.train_push_button.clicked.connect(self.train_process)
        self.scats_number_combo_box.currentIndexChanged.connect(self.scats_number_changed)

    def scats_number_changed(self):
        """ Updates the junction combo box when the scats number is changed """
        index = self.scats_number_combo_box.currentIndex()
        value = self.scats_number_combo_box.itemText(index)

        if value == "All" or value == "":
            self.junction_combo_box.setCurrentIndex(0)
            self.junction_combo_box.setEnabled(False)
        elif value == "None":
            self.scats_number_combo_box.setEnabled(False)
            self.junction_combo_box.setEnabled(False)
        else:
            self.junction_combo_box.clear()

            self.junction_combo_box.addItem("All")
            for junction in self.scats_info[value]:
                self.junction_combo_box.addItem(str(junction))

            self.junction_combo_box.setEnabled(True)

    def train(self):
        """ Passes the training parameters to the program """
        scats_number = self.scats_number_combo_box.itemText(self.scats_number_combo_box.currentIndex())
        if scats_number != "All":
            scats_number = int(scats_number)
        junction = self.junction_combo_box.itemText(self.junction_combo_box.currentIndex())
        if junction != "All":
            junction = int(SCATS_DATA.get_location_id(junction))
        model = self.model_combo_box.itemText(self.model_combo_box.currentIndex()).lower()

        while True:
            train_with_args(scats_number, junction, model)
            if not self.continue_train_checkbox.isChecked():
                break;

    def train_process(self):
        """ Runs the training with threads """
        training_threads = []
        t = threading.Thread(target=self.train)
        training_threads.append(t)
        self.threads.append(t)

        for thread in training_threads:
            thread.start()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = UiTrain(main_window)
    ui.setup()
    main_window.show()
    sys.exit(app.exec_())
