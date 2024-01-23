import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
from Image import Image


class ClickableLabel(qtw.QLabel):
    clicked = qtc.pyqtSignal()
    dragged = qtc.pyqtSignal()
    dragged_downwards = qtc.pyqtSignal()
    dragged_right = qtc.pyqtSignal()
    dragged_left = qtc.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.startPos = None

    def mousePressEvent(self, event):
        if event.button() == qtc.Qt.LeftButton:
            self.clicked.emit()
            self.startPos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == qtc.Qt.RightButton and self.startPos is not None:
            if event.pos().y() < self.startPos.y():
                self.dragged.emit()
            elif event.pos().y() > self.startPos.y():
                self.dragged_downwards.emit()
            if event.pos().x() < self.startPos.x():
                self.dragged_right.emit()
            elif event.pos().x() > self.startPos.x():
                self.dragged_left.emit()
