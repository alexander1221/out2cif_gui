import os
from os import listdir
from os.path import isfile, join

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow, QApplication

import out2cif
from out2cifgui44 import Ui_MainWindow


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
        print('ClearButtonPressed')

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

        out2cif.main(list_of_files_2_save, path_to_save)


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
