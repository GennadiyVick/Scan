from PyQt5 import QtCore, QtGui, QtWidgets
#https://evileg.com/en/post/272/
class ClipScene(QtWidgets.QGraphicsScene):

    def __init__(self, parent):
        super(ClipScene, self).__init__(parent)
        self.mousePressed = False
        self.m_selection = QtWidgets.QGraphicsRectItem()
        self.imageitem = None #QtWidgets.QGraphicsPixmapItem()
        self.prevpos = QtCore.QPointF(0, 0)
        self.scaled = 1.0
        self.croped = False

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mousePressed = True
            self.prevpos = event.scenePos()
            self.m_selection = QtWidgets.QGraphicsRectItem()
            self.m_selection.setBrush(QtGui.QBrush(QtGui.QColor(158,182,255,96)))
            self.m_selection.setPen(QtGui.QPen(QtGui.QColor(158,182,255,96), 1))
            self.addItem(self.m_selection)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.mousePressed:
            dx = event.scenePos().x() - self.prevpos.x()
            dy = event.scenePos().y() - self.prevpos.y()
            self.m_selection.setRect(
                self.prevpos.x() if dx > 0 else self.prevpos.x() + dx,
                self.prevpos.y() if dy > 0 else self.prevpos.y() + dy,
                abs(dx), abs(dy))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mousePressed = False
            selectionRect = self.m_selection.boundingRect().toRect()
            if selectionRect.width() > 10 and selectionRect.height() > 10:
                if self.scaled < 1.0:
                    x = int(selectionRect.x()/self.scaled)
                    y = int(selectionRect.y()/self.scaled)
                    w = int(selectionRect.width()/self.scaled)
                    h = int(selectionRect.height()/self.scaled)
                    iw = self.imageitem.pixmap().width()
                    ih = self.imageitem.pixmap().height()
                    if x < 0: x = 0
                    if y < 0: y = 0
                    if w > iw: w = iw
                    if h > ih: h = ih
                    selectionRect.setRect(x,y,w,h)
                self.imageitem.setPixmap(self.imageitem.pixmap().copy(selectionRect))
                self.updateScaled(self.sceneRect().width(), self.sceneRect().height())
                self.croped = True
            self.removeItem(self.m_selection)
        super().mouseReleaseEvent(event)

    def setImage(self, filePath):
        pix = QtGui.QPixmap(filePath)
        if self.imageitem:
            self.removeItem(self.imageitem)
        self.imageitem = QtWidgets.QGraphicsPixmapItem(pix)
        self.updateScaled(self.sceneRect().width(), self.sceneRect().height())
        self.addItem(self.imageitem)
        self.croped = False

    def rotate(self):
        rm = QtGui.QTransform()
        rm.rotate(180.0)
        pix = self.imageitem.pixmap().transformed(rm)
        self.imageitem.setPixmap(pix)

    def updateScaled(self, w, h):
        if h == 0: return
        if self.imageitem:
            iw = self.imageitem.pixmap().width()
            ih = self.imageitem.pixmap().height()
            if iw <= w and ih <= h:
                self.scaled = 1.0
                self.imageitem.setScale(1.0)
                return
            k = w/h
            ik = iw/ih
            if ik >= k:
                k = w/iw
            else:
                k = h/ih
            self.imageitem.setScale(k)
            self.scaled = k

    def setSceneRect(self, x, y,w,h):
        self.updateScaled(w,h)
        super().setSceneRect(x,y,w,h)




    
