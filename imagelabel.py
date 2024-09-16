from PyQt5 import QtCore, QtWidgets

class ImageLabel(QtWidgets.QLabel):
    def __init__(self, parent):
        super(ImageLabel, self).__init__(parent)
        self.pix = None
        self.setScaledContents(False)
        #self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored))
    def setPixmap(self, pix):
        self.pix = pix
        super().setPixmap(self.scaledPixmap())

    def heightForWidth(self, w):
        return self.height() if self.pix is None else round((self.pix.height() * w)/self.pix.width())

    def sizeHint(self):
        w = self.width()
        h = self.heightForWidth(w)
        return QtCore.QSize(w, h)

    def scaledPixmap(self):
        return self.pix.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

    def resizeEvent(self, event):
        if self.pix != None:
            super().setPixmap(self.scaledPixmap())
