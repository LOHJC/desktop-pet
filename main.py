

from PyQt5 import QtGui, QtCore, QtWidgets
import sys

class PetHouse(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # borderless, transparent and stay on top
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # this is for calculate dragging
        self.mouseDragPos = 0
    
    def paintEvent(self, a0):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Fill entire window with a color
        painter.setBrush(QtGui.QColor(100, 180, 250, 255))  # RGBA
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(self.rect())

        return super().paintEvent(a0)
    
    def mousePressEvent(self, a0):
        # TOFIX: temp using rightclick to close the window
        if (a0.button() == QtCore.Qt.RightButton):
            self.close()
            QtWidgets.QApplication.instance().quit()
        self.mouseDragPos = a0.globalPos()
        return super().mousePressEvent(a0)
    
    def mouseMoveEvent(self, a0):
        delta = QtCore.QPoint(a0.globalPos() - self.mouseDragPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.mouseDragPos = a0.globalPos()

        return super().mouseMoveEvent(a0)


class PetLoader():
    def __init__(self, petname):
        self.idle_sprites = []
        self.walking_sprites = []

if __name__ == "__main__":
    # create a borderless window
    app = QtWidgets.QApplication([])
    window = PetHouse()
    window.show()

    # load the sprites
    pass

    sys.exit(app.exec_())