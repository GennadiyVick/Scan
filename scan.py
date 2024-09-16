#!/usr/bin/python3
import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from mainwindowgui import Ui_MainWindow
from PIL import Image
import sane
from pdfscan import PdfScan
from pathlib import Path
from previewdialog import previewImage
from settingsdialog import SettingsDialog, showSettings
from lang import Lang
from updatescannerpopup import PopupWidget
import subprocess


currentversion = '1.2.4'

changes = [{'version': '1.2.4', 'description': 'Добавлена кнопка удалить страницу в окне сканирования PDF, '
                                               'прочие мелкие исправления и улучшения.'}, ]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, qApp):
        super(MainWindow, self).__init__()
        self.lang = Lang()
        lang_keys = list(self.lang.dic['languages'].keys())
        sets = QtCore.QSettings(os.path.join('RoganovSoft', 'Scan'), "config")
        i = int(sets.value("Settings/language_index", 0))
        if i > 0:
            self.lang.lang = lang_keys[i - 1]
        self.qApp = qApp
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, self.lang)
        self.ui.l_author.setText(self.ui.l_author.text() + ' v.' + str(currentversion) + '  ')
        self.appdir = os.path.dirname(os.path.realpath(__file__))
        self.ui.bUpdateSource.clicked.connect(self.updatesource)
        self.ui.cbSource.activated.connect(self.devicechange)
        self.ui.cbFeeder.clicked.connect(self.updatefeederduplex)
        self.ui.bDir.clicked.connect(self.setautosavedir)
        self.ui.bFileName.setVisible(False)
        self.ui.bSet.clicked.connect(self.showsettings)
        self.devices = []
        self.dev = None
        self.ui.bScan.clicked.connect(self.scan)
        self.ui.bScan.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F3))
        self.ui.bScanPdf.clicked.connect(self.scanpdf)
        self.ui.bScanPdf.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F4))
        self.ui.bHelp.clicked.connect(self.showhelp)
        self.ui.bHelp.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F1))
        self.updateonstart = True
        self.pagesize = ''
        self.loadset()
        self.currentdeviceindex = -1
        self.devicepagesize = (0, 0)
        completer = QtWidgets.QCompleter(self)
        self.fsModel = QtWidgets.QFileSystemModel(completer)
        self.fsModel.setRootPath(os.path.expanduser("~"))
        self.fsModel.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
        completer.setModel(self.fsModel)
        self.ui.eDir.setCompleter(completer)

        self.move(QtWidgets.QApplication.desktop().screen().rect().center() - self.rect().center())
        if self.updateonstart:
            self.updatesource()

    def loadset(self):
        sets = QtCore.QSettings(os.path.join('RoganovSoft', 'Scan'), "config")
        i = int(sets.value("Settings/papersize", 0))
        self.pagesize = SettingsDialog.sizes[i]
        self.updateonstart = sets.value("Settings/updatedevices_on_start", 'true') == 'true'
        self.lastdir = sets.value('Main/lastdir', str(Path.home()))
        self.jpegcompression = int(sets.value('Scan/compression', self.ui.spinBox_2.value()))
        self.ui.spinBox_2.setValue(self.jpegcompression)
        self.ui.spinBox.setValue(int(sets.value('Scan/dpi', self.ui.spinBox.value())))
        colored = sets.value('Scan/colored', 'true') == 'true'
        self.ui.rbColored.setChecked(colored)
        self.ui.rbGrayscale.setChecked(not colored)
        self.ui.cbPostView.setChecked(sets.value('Scan/postview', 'false') == 'true')
        self.ui.cbDuplex.setChecked(sets.value('Scan/duplex', 'false') == 'true')
        self.ui.cbFeeder.setChecked(sets.value('Scan/feeder', 'false') == 'true')
        self.ui.gbAutoSave.setChecked(sets.value('Scan/autosave', 'false') == 'true')
        self.ui.cbFileName.setCurrentText(sets.value('Scan/filename', ''))
        self.ui.eDir.setText(sets.value('Scan/directory', ''))
        itemscount = sets.beginReadArray("filenames")
        for i in range(itemscount):
            sets.setArrayIndex(i)
            fn = sets.value('filename', '')
            if len(fn) > 1:
                self.ui.cbFileName.addItem(fn)
        sets.endArray()

    def saveset(self):
        sets = QtCore.QSettings(os.path.join('RoganovSoft', 'Scan'), "config")
        sets.setValue('Main/lastdir', self.lastdir)
        sets.setValue('Scan/compression', self.ui.spinBox_2.value())
        sets.setValue('Scan/dpi', self.ui.spinBox.value())
        sets.setValue('Scan/colored', self.ui.rbColored.isChecked())
        sets.setValue('Scan/postview', self.ui.cbPostView.isChecked())
        sets.setValue('Scan/duplex', self.ui.cbDuplex.isChecked())
        sets.setValue('Scan/feeder', self.ui.cbFeeder.isChecked())
        sets.setValue('Scan/autosave', self.ui.gbAutoSave.isChecked())
        sets.setValue('Scan/filename', self.ui.cbFileName.currentText())
        sets.setValue('Scan/directory', self.ui.eDir.text())
        sets.beginWriteArray("filenames")
        for i in range(self.ui.cbFileName.count()):
            sets.setArrayIndex(i)
            sets.setValue('filename', self.ui.cbFileName.itemText(i))
        sets.endArray()

    def doUpdateSource(self):
        sane.exit()
        sane.init()
        self.devices = sane.get_devices(True)
        self.ui.cbSource.clear()
        for dev in self.devices:
            self.ui.cbSource.addItem(dev[2])
        if len(self.devices) > 0:
            self.ui.cbSource.setCurrentIndex(0)
            self.devicechange(0)
        self.popup.close()
        self.popup = None

    def updatesource(self):
        self.popup = PopupWidget(self.lang, self)
        self.popup.show()
        QtCore.QTimer.singleShot(50, self.doUpdateSource)

    def updatefeederduplex(self):
        e = self.ui.cbFeeder.isEnabled()
        if e != self.feeder_enabled:
            self.ui.cbFeeder.setEnabled(self.feeder_enabled)
            if not self.feeder_enabled: self.ui.cbFeeder.setChecked(False)

        self.ui.cbDuplex.setEnabled(self.feeder_enabled and self.ui.cbFeeder.isChecked() and self.duplex_enabled)
        if not self.ui.cbDuplex.isEnabled() and self.ui.cbDuplex.isChecked():
            self.ui.cbDuplex.setChecked(False)

        if self.ui.cbFeeder.isEnabled() and self.ui.cbFeeder.isChecked():
            self.ui.cbPostView.setEnabled(False)
            self.ui.cbPostView.setChecked(False)
        else:
            self.ui.cbPostView.setEnabled(True)

    def devicechange(self, index):
        if index < 0 or index >= len(self.devices):
            return
        #if index == self.currentdeviceindex: return
        if self.dev != None:
            self.dev.close()
            self.dev = None
        try:
            self.dev = sane.open(self.devices[index][0])
        except Exception as e:
            print(str(e))
            QtWidgets.QMessageBox.information(self, self.lang.tr('error'), self.lang.tr('notopendevice'))
            return
        self.duplex_enabled = False
        self.feeder_enabled = False
        op = self.dev.get_options()
        for o in op:
            if o[1] == 'source':
                source = o[8]
                self.feeder_enabled = 'ADF Front' in source or 'ADF Back' in source or 'ADF Duplex' in source
                self.duplex_enabled = 'ADF Duplex' in source
                break
        self.updatefeederduplex()
        self.currentdeviceindex = index
        self.devicepagesize = (self.dev.br_x, self.dev.br_y)

    def setScanArea(self, area):
        if self.dev is None:
            return False
        else:
            self.dev.tl_x = 0
            self.dev.tl_y = 0
            if area == 'A4' or area == 'a4':
                self.dev.br_x = 210
                self.dev.br_y = 297
            elif area == 'A5' or area == 'a5':
                self.dev.br_x = 148
                self.dev.br_y = 210
            elif area == 'A6' or area == 'a6':
                self.dev.br_x = 105
                self.dev.br_y = 148
            elif area == 'Legal' or area == 'legal':
                self.dev.br_x = 216
                self.dev.br_y = 356
            else:
                self.dev.br_x = 216
                self.dev.br_y = 279
            return True

    def preparescan(self):
        if self.dev == None:
            print('device not assigned')
            return False
        try:
            if self.ui.cbDuplex.isChecked():
                self.dev.source = 'ADF Duplex'
            elif self.ui.cbFeeder.isChecked():
                self.dev.source = 'ADF Front'
            else:
                self.dev.source = 'Flatbed'
            self.dev.depth = 8
            self.dev.mode = 'Color' if self.ui.rbColored.isChecked() else 'Gray'  #Color or Gray
            self.dev.resolution = self.ui.spinBox.value()
            if len(self.pagesize) > 1:
                self.setScanArea(self.pagesize)
            self.jpegcompression = self.ui.spinBox_2.value()
            #print(self.dev.br_x, self.dev.br_y)
        except Exception as e:
            print(str(e))
            return False
        else:
            return True

    def doStart(self):
        try:
            self.dev.start()
        except Exception as e:
            print(str(e))
            return False
        else:
            return True

    def scanpdf(self):
        if self.dev == None:
            QtWidgets.QMessageBox.information(self, self.lang.tr('attension'), self.lang.tr('devicenotselected'))
            return
        if self.ui.gbAutoSave.isChecked():
            if self.ui.eDir.text() == '' or not os.path.isdir(self.ui.eDir.text()):
                QtWidgets.QMessageBox.information(self, self.lang.tr('attension'), self.lang.tr('directorynotspec'))
                return
            if len(self.ui.cbFileName.currentText()) < 2:
                QtWidgets.QMessageBox.information(self, self.lang.tr('attension'), self.lang.tr('documentnotspec'))
                return
        if not self.preparescan():
            QtWidgets.QMessageBox.information(self, self.lang.tr('error'), self.lang.tr('errorprepare'))
            return
        fn = ''
        if self.ui.gbAutoSave.isChecked():
            fn = os.path.join(self.ui.eDir.text(), self.ui.cbFileName.currentText())
        d = PdfScan(self.lang, self.appdir, self.dev, self.jpegcompression, fn, self)
        i = d.exec()

    def scan(self):
        if self.dev == None:
            QtWidgets.QMessageBox.information(self, self.lang.tr('attension'), self.lang.tr('devicenotselected'))
            return
        if self.ui.gbAutoSave.isChecked():
            if self.ui.eDir.text() == '' or not os.path.isdir(self.ui.eDir.text()):
                QtWidgets.QMessageBox.information(self, self.lang.tr('attension'), self.lang.tr('directorynotspec'))
                return
            if len(self.ui.cbFileName.currentText()) < 2:
                QtWidgets.QMessageBox.information(self, self.lang.tr('attension'), self.lang.tr('documentnotspec'))
                return
            self.addfilenametolist()

        if not self.preparescan():
            QtWidgets.QMessageBox.information(self, self.lang.tr('error'), self.lang.tr('errorprepare'))
            return
        selectedsource = self.dev.source
        if selectedsource == 'Flatbed':
            if self.doStart():
                img = self.dev.snap()
                if self.ui.cbPostView.isChecked():
                    tfn = os.path.join(self.appdir, 'temp.png')
                    img.save(tfn)
                    if previewImage(tfn, self.lang, isjpeg=False):
                        img = Image.open(tfn)
                        os.remove(tfn)
                    else:
                        os.remove(tfn)
                        return
                if self.ui.gbAutoSave.isChecked():
                    i = 0
                    fn = self.ui.cbFileName.currentText()
                    if fn[-4:] == '.jpg':
                        fn = fn[:-4]
                    fn = os.path.join(self.ui.eDir.text(), fn)
                    while os.path.exists(f'{fn}_{i}.jpg'):
                        i += 1
                    fn = f'{fn}_{i}.jpg'
                else:
                    #self.lastdir,
                    fn, ext = QtWidgets.QFileDialog.getSaveFileName(self, self.lang.tr("saveas"),
                                                                    os.path.join(self.lastdir, "untitled"), ".jpg")
                    if len(fn) < 2: return
                    if fn[-len(ext):] != ext:
                        fn += ext
                    self.lastdir = os.path.dirname(fn)
                img.save(fn, quality=self.jpegcompression)
        else:
            #folder = QtWidgets.QFileDialog.getExistingDirectory(self, caption, defaultdir)
            if self.ui.gbAutoSave.isChecked():
                fn = os.path.join(self.ui.eDir.text(), self.ui.cbFileName.currentText())
            else:
                fn, ext = QtWidgets.QFileDialog.getSaveFileName(self.lastdir, self.lang.tr("saveas"), "untitled",
                                                                ".jpg")
                if len(fn) < 2: return
                self.lastdir = os.path.dirname(fn)
            if fn[-4:] == '.jpg':
                fn = fn[:-4]
            i = 0
            onescanned = False
            while self.doStart():
                img = self.dev.snap(True)
                onescanned = True
                while os.path.exists(f'{fn}_{i}.jpg'): i += 1
                img.save(f'{fn}_{i}.jpg', quality=self.jpegcompression)
                i += 1
            if not onescanned:
                QtWidgets.QMessageBox.information(self, self.lang.tr('error'), self.lang.tr('nodocument'))

    def setautosavedir(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(self, self.lang.tr('openfolder'), self.lastdir,
                                                         QtWidgets.QFileDialog.ShowDirsOnly
                                                         | QtWidgets.QFileDialog.DontResolveSymlinks)
        if len(dir) > 2:
            self.ui.eDir.setText(dir)
            self.lastdir = dir

    def addfilenametolist(self):
        fn = self.ui.cbFileName.currentText()
        fnl = fn.lower()
        for i in range(self.ui.cbFileName.count()):
            it = self.ui.cbFileName.itemText(i)
            if fnl == it.lower():
                if i == 0:
                    if fn != it:
                        self.ui.cbFileName.setItemText(i, fn)
                else:
                    self.ui.cbFileName.removeItem(i)
                    self.ui.cbFileName.insertItem(0, fn)
                return
        self.ui.cbFileName.insertItem(0, fn)
        c = self.ui.cbFileName.count()
        if c > 30:
            self.ui.cbFileName.removeItem(c - 1)

    def closeEvent(self, event):
        if self.dev != None:
            self.dev.close()
        sane.exit()
        self.saveset()
        super(MainWindow, self).closeEvent(event)

    def showsettings(self):
        s = showSettings(self.lang, self)
        if 'size' in s:
            self.pagesize = s['size']

    def showhelp(self):
        subprocess.Popen(['firefox', os.path.join(self.appdir, 'help.html')])


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(':/icon.png'))
    themedir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'darktheme')
    fn = os.path.join(themedir, 'theme.qrc')
    if os.path.isfile(fn):
        with open(fn, 'r') as f:
            theme = f.read()
        theme = theme.replace('current_directory', themedir)
        app.setStyleSheet(theme)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
