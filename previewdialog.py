import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from previewdialoggui import Ui_PreviewDialog
from clipscene import ClipScene

class Preview(QtWidgets.QDialog):
    def __init__(self, filename, lang, parent = None):
        super(Preview,self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.ui = Ui_PreviewDialog()
        self.ui.setupUi(self, lang)
        self.loadsets()
        self.scene = ClipScene(self)
        self.ui.gv.setScene(self.scene)
        self.ui.gv.setStyleSheet('QGraphicsView{background: #222;}')
        self.filename = filename
        self.scene.setImage(filename)
        self.ui.bRestore.clicked.connect(self.restore)
        self.ui.bRotate.clicked.connect(self.scene.rotate)
        QtCore.QTimer.singleShot(50, self.setSceneRect)

    def loadsets(self):
        set = QtCore.QSettings(os.path.join('RoganovSoft', 'Scan'), "config")
        x = int(set.value("Preview/left",0))
        y = int(set.value("Preview/top",0))
        w = int(set.value("Preview/width",0))
        h = int(set.value("Preview/height",0))
        if x != 0 and y != 0:
            self.move(x,y)
        if w != 0 and h != 0:
            self.resize(w,h)

    def savesets(self):
        set = QtCore.QSettings(os.path.join('RoganovSoft', 'Scan'), "config")
        p = self.pos()
        set.setValue("Preview/left",p.x())
        set.setValue("Preview/top",p.y())
        set.setValue("Preview/width",self.width())
        set.setValue("Preview/height",self.height())

    def done(self, r):
        self.savesets()
        super(Preview,self).done(r)

    def setSceneRect(self):
        rcontent = self.ui.gv.contentsRect()
        self.scene.setSceneRect(0,0,rcontent.width(), rcontent.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setSceneRect()

    def restore(self):
        self.scene.setImage(self.filename)


def previewImage(filename, lang, isjpeg=True, compression=80, parent=None):
    dlg = Preview(filename, lang, parent)
    if dlg.exec() == 1:
        if dlg.scene.imageitem:
            if isjpeg:
                dlg.scene.imageitem.pixmap().save(filename, "JPEG", compression)
            else:
                dlg.scene.imageitem.pixmap().save(filename, "PNG")
        return True
    else:
        return False

'''
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(':/icon.png'))
    appdir = os.path.dirname(os.path.realpath(__file__))
    fn = os.path.join(appdir,'dark.qss')
    if os.path.isfile(fn):
        with open(fn, 'r') as f:
            darktheme = f.read()
        app.setStyleSheet(darktheme)
    window = Preview('1.jpg')
    print(window.exec())
    sys.exit()


if __name__ == '__main__':
    main()
'''

