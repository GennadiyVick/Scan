import os
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PopupWindow(object):
    def setupUi(self, PopupWindow, lang):
        PopupWindow.setObjectName("PopupWindow")
        PopupWindow.resize(224, 132)
        PopupWindow.setStyleSheet("background: #444;")
        self.layout = QtWidgets.QHBoxLayout(PopupWindow)
        self.layout.setObjectName("layout")
        self.linfo = QtWidgets.QLabel(PopupWindow)
        self.linfo.setStyleSheet("QLabel{background: #333; font-size: 14pt;}")
        self.linfo.setAlignment(QtCore.Qt.AlignCenter)
        self.linfo.setObjectName("linfo")
        self.layout.addWidget(self.linfo)
        self.linfo.setText(lang.tr("scannersearch"))
        #PopupWindow.setWindowTitle("PopupWindow")


class PopupWidget(QtWidgets.QWidget):
    def __init__(self, lang, parent=None):
        super(PopupWidget, self).__init__(parent)
        self.ui = Ui_PopupWindow()
        self.ui.setupUi(self,lang)
        if parent != None:
            #self.move(parent.rect().center() - self.rect().center())
            l = parent.pos().x()
            t = parent.pos().y()
            w = parent.width()
            h = parent.height()
            self.move(l+(w-self.width()) // 2, t+(h-self.height()) // 2)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool |  QtCore.Qt.WindowStaysOnTopHint)
        #self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
