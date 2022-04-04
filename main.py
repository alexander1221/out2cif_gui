import os
from os import listdir
from os.path import isfile, join

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow, QApplication

import out2cif
from out2cif_gui6 import Ui_MainWindow
from dict_sym_ops import Hall2Number

def getKeysByValue(dictOfElements, valueToFind):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item  in listOfItems:
        if item[1] == valueToFind:
            listOfKeys.append(item[0])
    return  listOfKeys

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        # uic.loadUi('out2cifgui.ui', self)
        self.setupUi(self)
        self.LoadButton.clicked.connect(self.LoadButtonPressed)
        self.ClearButton.clicked.connect(self.ClearButtonPressed)
        self.RunButton.clicked.connect(self.RunButtonPressed)
        self.pushButton.clicked.connect(self.PushButtonPressed)
        self.spinBox.valueChanged.connect(self.return_spg_number)
        self.radioButton.clicked.connect(self.check_radio_buttons)
        self.radioButton_2.clicked.connect(self.check_radio_buttons)
        self.listWidget.itemClicked.connect(self.itemActivated_event)
        #self.SaveButton.clicked.connect(self.SaveButtonPressed)
        QApplication.processEvents()
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stderr = EmittingStream(textWritten=self.badOutputWritten)

    def exportFiles(self, file_name, n):
        default_dir = os.getcwd()
        default_filename = os.path.join(default_dir, file_name)
        if n == 1:
            file_name, _ = QFileDialog.getSaveFileName(self, "save_cif_file", default_filename)
        return file_name

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        QApplication.processEvents()
        cursor = ui.textBrowser_2.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        ui.textBrowser_2.setTextCursor(cursor)
        ui.textBrowser_2.ensureCursorVisible()

    def badOutputWritten(self, text3):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        QApplication.processEvents()
        ui.textBrowser_3.clear()
        cursor3 = ui.textBrowser_3.textCursor()
        cursor3.movePosition(QtGui.QTextCursor.End)
        cursor3.insertText(text3)
        ui.textBrowser_3.setTextCursor(cursor3)
        ui.textBrowser_3.ensureCursorVisible()

    def LoadButtonPressed(self):
        # This is executed when the button is pressed
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Crystal Out Files (*.out)", options=options)
        if self.files:
            print('files_obtained ', self.files)
        for i in self.files:
            # print(i)
            z = i.split('/')[-1]
            ui.textBrowser.append(z)

        print('LoadButtonPressed')

    def ClearButtonPressed(self):
        # This is executed when the button is pressed
        self.files = None
        ui.textBrowser.clear()
        ui.textBrowser_2.clear()
        ui.textBrowser_3.clear()
        ui.listWidget.clear()
        ui.spinBox.clear()
        self.manual_spg_number = None
        self.manual_hall_name = None
        print('ClearButtonPressed')

    def check_radio_buttons(self):
        if self.radioButton.isChecked():
            self.workflow_mode = 1
            space_group_number = None
            Hall_space_group_name = None
            ui.listWidget.clear()
            ui.spinBox.clear()
            print('Auto')
        if self.radioButton_2.isChecked():
            self.workflow_mode = 2
            print('Manual')

    def return_spg_number(self):
        if self.workflow_mode == 2:
            self.space_group_number = self.spinBox.value()
            print(self.space_group_number)
            self.list_of_hals = getKeysByValue(Hall2Number, self.space_group_number)
            print(self.list_of_hals)
            ui.listWidget.clear()
            ui.listWidget.addItems(self.list_of_hals)
            #ui.listWidget.items(self.list_of_hals)

    # def show_hall_list_and_select(self):
    #     self.list_of_hals = getKeysByValue(Hall2Number, self.space_group_number)
    #     print(self.list_of_hals)
    #     #ui.listWidget.clear()
    #     #ui.listWidget.addItems(self.list_of_hals)
    #     ui.listWidget.items(self.list_of_hals)

    def itemActivated_event(self, item):
        self.activated_hall = item.text()
        print(item.text())

    def PushButtonPressed(self):
        # This is executed when the button is pressed
        if self.workflow_mode == 1:
            self.manual_spg_number = 'Auto'
            self.manual_hall_name = 'Auto'
            print('Auto')
        if self.workflow_mode == 2:
            print(self.space_group_number)
            print(self.list_of_hals)
            self.manual_spg_number = self.space_group_number
            self.manual_hall_name = self.activated_hall
            print('Manual')
        print('SetButtonPressed')

    def RunButtonPressed(self):
        # This is executed when the button is pressed
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getOpenFileNames()", " ", "All Files (*);;Crystal Out Files (*.out)", options=options)
        path_to_save = os.path.dirname(file_name)
        list_of_cifs_2_check = [f for f in listdir(path_to_save) if
                                isfile(join(path_to_save, f)) and f.endswith('.cif')]

        print('RunButtonPressed')

        list_of_files_2_save = []

        for file_name in self.files:
            if file_name in list_of_cifs_2_check:
                continue
            list_of_files_2_save.append(file_name)

        out2cif.main(list_of_files_2_save, path_to_save, self.manual_spg_number, self.manual_hall_name)


    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.processEvents()
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
