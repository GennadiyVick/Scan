import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from settingsdialogui import Ui_SettingsDialog

class SettingsDialog(QtWidgets.QDialog):
    sizes = ['','A4','A5', 'A6', 'Legal']

    def __init__(self, lang, parent = None):
        super(SettingsDialog,self).__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self, lang)
        self.ui.cbPaperSize.addItem(lang.tr('default'))
        for i in range(1, len(self.sizes)):
            self.ui.cbPaperSize.addItem(self.sizes[i])
        self.loadsets()

    def accept(self):
        self.savesets()
        super().accept()

    def loadsets(self):
        set = QtCore.QSettings(os.path.join('RoganovSoft', 'Scan'), "config")
        i = int(set.value("Settings/papersize",0))
        self.ui.cbPaperSize.setCurrentIndex(i)
        self.ui.cbUpdateOnStart.setChecked(set.value("Settings/updatedevices_on_start", 'true') == 'true')

    def savesets(self):
        set = QtCore.QSettings(os.path.join('RoganovSoft', 'Scan'), "config")
        set.setValue("Settings/papersize", self.ui.cbPaperSize.currentIndex())
        set.setValue("Settings/updatedevices_on_start", self.ui.cbUpdateOnStart.isChecked())


def showSettings(lang, parent):
    dlg = SettingsDialog(lang, parent)
    if dlg.exec() == 1:
        return {'size':SettingsDialog.sizes[dlg.ui.cbPaperSize.currentIndex()], 'update':dlg.ui.cbUpdateOnStart.isChecked()}
    else:
        return {}

