import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import Image
from pdfscangui import Ui_PdfScanDialog
from pathlib import Path
from previewdialog import previewImage


class PdfScan(QtWidgets.QDialog):
    def __init__(self, lang, appdir, dev, jpegquality, savefn, parent = None):
        super(PdfScan,self).__init__(parent)
        self.lang = lang
        self.ui = Ui_PdfScanDialog()
        self.ui.setupUi(self, self.lang)
        self.loadsets()
        self.dev = dev
        self.parent = parent
        self.jpegquality = jpegquality
        self.savefn = savefn
        self.appdir = appdir
        self.cachedir = os.path.join(appdir,'cache')
        if not os.path.isdir(self.cachedir):
            os.mkdir(self.cachedir)
        self.ui.bScan.clicked.connect(self.scan)
        self.ui.bSave.clicked.connect(self.save)
        self.ui.bUp.clicked.connect(self.moveup)
        self.ui.bDown.clicked.connect(self.movedown)
        self.ui.bRotate.clicked.connect(self.rotate)
        self.ui.bCrop.clicked.connect(self.crop)
        self.ui.lw.itemClicked.connect(self.itemClick)
        #self.ui.lw.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.loadimages()

    def loadsets(self):
        sets = QtCore.QSettings(os.path.join('RoganovSoft', 'Scan'), "config")
        x = int(sets.value("PdfScan/left",0))
        y = int(sets.value("PdfScan/top",0))
        w = int(sets.value("PdfScan/width",0))
        h = int(sets.value("PdfScan/height",0))
        if x != 0 and y != 0:
            self.move(x,y)
        if w != 0 and h != 0:
            self.resize(w,h)

    def savesets(self):
        sets = QtCore.QSettings(os.path.join('RoganovSoft', 'Scan'), "config")
        p = self.pos()
        sets.setValue("PdfScan/left",p.x())
        sets.setValue("PdfScan/top",p.y())
        sets.setValue("PdfScan/width",self.width())
        sets.setValue("PdfScan/height",self.height())


    def loadimages(self):
        files = os.listdir(self.cachedir)
        for f in files:
            if 'image_' in f:
                im = Image.open(os.path.join(self.cachedir, f))
                im.thumbnail((160,160))
                tfn = os.path.join(self.cachedir, 'tumb.jpg')
                im.save(tfn)
                item = QtWidgets.QListWidgetItem()
                item.setText(os.path.join(self.cachedir, f))
                item.setIcon(QtGui.QIcon(tfn))
                self.ui.lw.addItem(item)


    def done(self, r):
        clear = True
        if r == 0:
            if os.path.exists(os.path.join(self.cachedir, 'image_0.jpg')):
                res = QtWidgets.QMessageBox.question(self, self.lang.tr('cacheimages'),self.lang.tr("removefiles"), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if res == QtWidgets.QMessageBox.Yes:
                    clear = True
                else:
                    clear = False
        if clear: self.clearcache()
        self.savesets()
        super(PdfScan,self).done(r)

    def clearcache(self):
        files = os.listdir(self.cachedir)
        for fn in files:
            os.remove(os.path.join(self.cachedir, fn))

    def doStart(self):
        try:
            self.dev.start()
        except Exception as e:
            print(str(e))
            return False
        else:
            return True

    def scan(self):
        selectedsource = self.dev.source
        if selectedsource == 'Flatbed':
            if not self.doStart():
                QtWidgets.QMessageBox.information(self,self.lang.tr('error'),self.lang.tr('nodocument'))
                return
            im = self.dev.snap()
            fn = os.path.join(self.cachedir,'image')
            i = 0
            while os.path.exists(f'{fn}_{i}.jpg'): i += 1
            fn = f'{fn}_{i}.jpg'
            im.save(fn)
            im.thumbnail((160,160))
            tfn = os.path.join(self.cachedir, 'tumb.jpg')
            im.save(tfn)
            item = QtWidgets.QListWidgetItem()
            item.setText(fn)
            item.setIcon(QtGui.QIcon(tfn))
            self.ui.lw.addItem(item)
        else:
            onescanned = False
            while self.doStart():
                im = self.dev.snap(True)
                onescanned = True
                fn = os.path.join(self.cachedir,'image')
                i = 0
                while os.path.exists(f'{fn}_{i}.jpg'): i += 1
                fn = f'{fn}_{i}.jpg'
                im.save(fn)
                im.thumbnail((160,160))
                tfn = os.path.join(self.cachedir, 'tumb.jpg')
                im.save(tfn)
                item = QtWidgets.QListWidgetItem()
                item.setText(fn)
                item.setIcon(QtGui.QIcon(tfn))
                self.ui.lw.addItem(item)
            if not onescanned:
                QtWidgets.QMessageBox.information(self,self.lang.tr('error'),self.lang.tr('nodocumentfeeder'))


    def save(self):
        if self.ui.lw.count() == 0:
            QtWidgets.QMessageBox.information(self,self.lang.tr('wtf'),self.lang.tr('emptypdf'))
            return
        if len(self.savefn) > 1:
            i = 0
            while os.path.exists(f'{self.savefn}_{i}.pdf'):
                i += 1
            pfn = f'{self.savefn}_{i}.pdf'
        else:
            if self.parent != None:
                lastdir = self.parent.lastdir
            else:
                lastdir = str(Path.home())
            pfn, ext = QtWidgets.QFileDialog.getSaveFileName(self, self.lang.tr("saveas"), os.path.join(lastdir, "untitled"), ".pdf")
            if pfn == None or len(pfn) < 2: return
            lastdir = os.path.dirname(pfn)
            if self.parent != None:
                self.parent.lastdir = lastdir
            if pfn[-4:] != ext:
                pfn += ext

        images = []
        for i in range(self.ui.lw.count()):
            item = self.ui.lw.item(i)
            fn = item.text()
            images.append(Image.open(fn))
        if len(images) > 0:
            images[0].save(
                pfn, "PDF" ,resolution=self.dev.resolution, quality=self.jpegquality, save_all=True, append_images=images[1:]
            )
        self.accept()

    def moveup(self):
        if self.ui.lw.count() < 2 : return
        i = self.ui.lw.currentRow()
        if i < 1: return
        item = self.ui.lw.takeItem(i)
        self.ui.lw.insertItem(i - 1, item)
        self.ui.lw.setCurrentRow(i - 1)

    def movedown(self):
        if self.ui.lw.count() < 2 : return
        i = self.ui.lw.currentRow()
        if i >= self.ui.lw.count() - 1: return
        item = self.ui.lw.takeItem(i)
        self.ui.lw.insertItem(i + 1, item)
        self.ui.lw.setCurrentRow(i + 1)

    def rotate(self):
        if self.ui.lw.count() < 1 : return
        i = self.ui.lw.currentRow()
        if i < 0: return
        item = self.ui.lw.item(i)
        im = Image.open(item.text())
        im = im.rotate(180)
        im.save(self.ui.lw.item(i).text())
        im.thumbnail((160,160))
        tfn = os.path.join(self.cachedir, 'tumb.jpg')
        im.save(tfn)
        item.setIcon(QtGui.QIcon(tfn))
        self.itemClick()

    def crop(self):
        if self.ui.lw.count() < 1 : return
        i = self.ui.lw.currentRow()
        if i < 0: return
        item = self.ui.lw.item(i)
        fn = item.text()
        if previewImage(fn, self.lang):
            im = Image.open(fn)
            im.thumbnail((160,160))
            tfn = os.path.join(self.cachedir, 'tumb.jpg')
            im.save(tfn)
            item.setIcon(QtGui.QIcon(tfn))
            self.itemClick()
    
    def itemClick(self):
        if self.ui.lw.count() < 1 : return
        i = self.ui.lw.currentRow()
        if i < 0: return
        fn =  self.ui.lw.item(i).text()
        self.ui.lPreview.setPixmap(QtGui.QPixmap(fn))
        self.ui.lPreview.repaint()

